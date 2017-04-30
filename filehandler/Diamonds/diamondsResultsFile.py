import glob
import numpy as np
from scipy.signal import butter, filtfilt
from math import sqrt

from filehandler.Diamonds.InternalStructure.backgroundParameterSummaryFile import ParameterSummary
from filehandler.Diamonds.InternalStructure.backgroundEvidenceInformationFile import Evidence
from filehandler.Diamonds.InternalStructure.backgroundParameterFile import BackgroundParameter
from filehandler.Diamonds.InternalStructure.backgroundMarginalDistributionFile import MarginalDistribution
from filehandler.Diamonds.diamondsPriorsFile import Priors
from filehandler.Diamonds.dataFile import DataFile
from settings.settings import Settings
from support.strings import *
from calculations.deltaNuCalculations import DeltaNuCalculator
from calculations.bolometricCorrectionCalculations import BCCalculator


class Results:
    __summary = None
    __evidence = None
    __backgroundParameter = []
    __marginalDistributions = []
    __prior = None
    __backgroundPriors = None
    __kicID = None
    __runID = None
    __dataFile = None
    __names = []
    __units = []
    __nyq = None
    __dataFolder = None
    __smoothedData = None
    __hg = None
    __numax = None
    __sigma = None
    __gaussBoundaries = None
    __deltaNuCalculator = None
    __PDSOnly = None
    __radiusStar = None
    __BCCalculator = None
    __BC = None


    def __init__(self,kicID,runID,Teff = None):
        self.__kicID = kicID
        self.__runID = runID
        self.__Teff = Teff
        self.__dataFile = DataFile(kicID)
        self.__summary = ParameterSummary(kicID, runID)
        self.__evidence = Evidence(kicID, runID)
        self.__prior = Priors(kicID)
        self.__backgroundPriors = Priors(kicID, runID)
        self.__dataFolder = Settings.Instance().getSetting(strDataSettings, strSectBackgroundResPath).value
        nyqFile = glob.glob(self.__dataFolder + 'KIC{}/NyquistFrequency.txt'.format(kicID))[0]
        self.__nyq = np.loadtxt(nyqFile)

        self.__names = ['w', '$\sigma_\mathrm{long}$', '$b_\mathrm{long}$', '$\sigma_\mathrm{gran,1}$',
                  '$b_\mathrm{gran,1}$', '$\sigma_\mathrm{gran,2}$', '$b_\mathrm{gran,2}$',
                  '$H_\mathrm{osc}$','$f_\mathrm{max}$ ', '$\sigma_\mathrm{env}$']

        self.__units = ['ppm$^2$/$\mu$Hz', 'ppm', '$\mu$Hz', 'ppm', '$\mu$Hz', 'ppm', '$\mu$Hz', 'ppm$^2$/$\mu$Hz',
                        '$\mu$Hz','$\mu$Hz']

        self.m_PSDOnly = False

        #todo this should happen again if Diamondsrun is finished!
        for i in range(0,10):
            try:
                par_median = self.__summary.getData(strSummaryMedian)[i]  # median values
                par_le = self.__summary.getData(strSummaryLowCredLim)[i]  # lower credible limits
                par_ue = self.__summary.getData(strSummaryUpCredlim)[i]  # upper credible limits
                backGroundParameters = np.vstack((par_median, par_le, par_ue))
            except:
                par_median = 0  # median values
                par_le = 0  # lower credible limits
                par_ue = 0  # upper credible limits
                backGroundParameters = np.vstack((par_median, par_le, par_ue))
                print("Problem creating median,le,ue values. Creating them with 0")

            self.__backgroundParameter.append(BackgroundParameter(self.__names[i], self.__units[i], kicID, runID, i))

            self.__marginalDistributions.append(MarginalDistribution(self.__names[i], self.__units[i], kicID, runID, i))
            self.__marginalDistributions[i].setBackgroundParameters(backGroundParameters)
            if self.__backgroundParameter[i].getData() is None:
                self.m_PSDOnly = True

        if Teff is not None:
            self.__BCCalculator = BCCalculator(Teff)
            self.__BC = self.__BCCalculator.getBC()



    def getBackgroundParameters(self,key = None):
        if key is None:
            return self.__backgroundParameter
        else:
            for i in self.__backgroundParameter:
                if i.getName == key:
                    return self.__backgroundParameter[i]

            print("Found no background parameter for '"+key+"'")
            print("Returning full list")
            return self.__backgroundParameter

    def getPrior(self):
        return self.__prior

    def getBackgroundPrior(self):
        return self.__backgroundPriors

    def getEvidence(self):
        return self.__evidence

    def getSummary(self):
        return self.__summary

    def getNyquistFrequency(self):
        return self.__nyq

    def getPSD(self):
        return self.__dataFile.getPSD()

    def getSmoothing(self):
        return self.__butter_lowpass_filtfilt(self.__dataFile.getPSD()[1])

    def getKicID(self):
        return self.__kicID

    def getNuMax(self):
        return self.__numax

    def getHg(self):
        return self.__hg

    def getSigma(self):
        return self.__sigma

    def getFirstHarveyFrequency(self):
        return self.__harveyF1

    def getSecondHarveyFrequency(self):
        return self.__harveyF2

    def getThirdHarveyFrequency(self):
        return self.__harveyF3

    def getFirstHarveyAmplitude(self):
        return self.__harveyA1

    def getSecondHarveyAmplitude(self):
        return self.__harveyA2

    def getThirdHarveyAmplitude(self):
        return self.__harveyA3

    def getBackgroundNoise(self):
        return self.__bgNoise

    def getGaussBoundaries(self):
        return self.__gaussBoundaries

    def getPSDOnly(self):
        return self.m_PSDOnly

    def getRadius(self):
        return self.__radiusStar

    def getBC(self):
        return self.__BC

    def getLuminosity(self):
        return self.__Luminosity

    def calculateDeltaNu(self):
        backgroundModel = self.createBackgroundModel(True)
        par_median = self.__summary.getData(strSummaryMedian)  # median values
        par_le = self.__summary.getData(strSummaryLowCredLim)  # lower credible limits
        par_ue = self.__summary.getData(strSummaryUpCredlim)   # upper credible limits
        backGroundParameters = np.vstack((par_median, par_le, par_ue))

        self.__deltaNuCalculator = DeltaNuCalculator(self.__numax[0], self.__sigma[0], self.__dataFile.getPSD(),
                                                     self.__nyq, backGroundParameters, backgroundModel)
        self.__deltaNuCalculator.calculateFit()

    def getDeltaNuCalculator(self):
        return self.__deltaNuCalculator

    def getBCCalculator(self):
        return self.__BCCalculator

    def __butter_lowpass_filtfilt(self,data,order=5):
        b, a = self.__butter_lowpass(0.7, order=order) # todo 0.7 is just empirical, this may work better with something else?
        psd = data
        self.__smoothedData = filtfilt(b, a, psd)
        return self.__smoothedData

    def __butter_lowpass(self,cutoff, order=5):#todo these should be reworked and understood properly!
        normal_cutoff = cutoff / self.__nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a


    def createBackgroundModel(self, runGauss):
        freq, psd = self.__dataFile.getPSD()
        par_median = self.__summary.getData(strSummaryMedian)  # median values
        par_le = self.__summary.getData(strSummaryLowCredLim)  # lower credible limits
        par_ue = self.__summary.getData(strSummaryUpCredlim) # upper credible limits
        if runGauss:
            self.__bgNoise = (par_median[0],par_median[0] - par_le[0])
            self.__harveyA1 = (par_median[1],par_median[1] - par_le[1])
            self.__harveyF1 = (par_median[2],par_median[2] - par_le[2])
            self.__harveyA2 = (par_median[3],par_median[3] - par_le[3])
            self.__harveyF2 = (par_median[4],par_median[4] - par_le[4])
            self.__harveyA3 = (par_median[5],par_median[5] - par_le[5])
            self.__harveyF3 = (par_median[6],par_median[6] - par_le[6])
            self.__hg = (par_median[7],par_median[7] - par_le[7])  # third last parameter
            self.__numax = (par_median[8],par_median[8] - par_le[8])  # second last parameter
            self.__sigma = (par_median[9],par_median[9] - par_le[9])  # last parameter

            print("Height is '" + str(self.__hg[0]) + "'")
            print("Numax is '" + str(self.__numax[0]) + "'")
            print("Sigma is '" + str(self.__sigma[0]) + "'")

        zeta = 2. * np.sqrt(2.) / np.pi  # !DPI is the pigreca value in double precision
        r = (np.sin(np.pi / 2. * freq / self.__nyq) / (
        np.pi / 2. * freq / self.__nyq)) ** 2  # ; responsivity (apodization) as a sinc^2
        w = par_median[0]  # White noise component
        g = 0
        if runGauss:
            g = self.__hg[0] * np.exp(-(self.__numax[0] - freq) ** 2 / (2. * self.__sigma[0] ** 2))  ## Gaussian envelope

        ## Long-trend variations
        sigma_long = par_median[1]
        freq_long = par_median[2]
        h_long = (sigma_long ** 2 / freq_long) / (1. + (freq / freq_long) ** 4)

        ## First granulation component
        sigma_gran1 = par_median[3]
        freq_gran1 = par_median[4]
        h_gran1 = (sigma_gran1 ** 2 / freq_gran1) / (1. + (freq / freq_gran1) ** 4)

        ## Second granulation component
        sigma_gran2 = par_median[5]
        freq_gran2 = par_median[6]
        h_gran2 = (sigma_gran2 ** 2 / freq_gran2) / (1. + (freq / freq_gran2) ** 4)

        ## Global background model
        print(w)
        w = np.zeros_like(freq) + w
        b1 = zeta * (h_long + h_gran1 + h_gran2) * r + w
        print("Whitenoise is '" + str(w) + "'")
        if runGauss:
            b2 = (zeta * (h_long + h_gran1 + h_gran2) + g) * r + w
            return zeta * h_long * r, zeta * h_gran1 * r, zeta * h_gran2 * r, w, g * r
        else:
            return zeta * h_long * r, zeta * h_gran1 * r, zeta * h_gran2 * r, w


    def createMarginalDistribution(self,key = None):
        if key is None:
            return self.__marginalDistributions
        else:
            for i in self.__marginalDistributions:
                if i.getName() == key:
                    return self.__marginalDistributions[i]

            print("Found no marginal Distribution for '"+key+"'")
            print("Returning full list")
            return self.__marginalDistributions

    def calculateRadius(self,TSun,NuMaxSun,DeltaNuSun):
        if self.__Teff is None:
            print("Teff is None, no calculation of BC takes place")
            return None

        if self.__deltaNuCalculator is None:
            print("Delta Nu is not yet calculated, need to calculate that first")
            self.calculateDeltaNu()

        self.__radiusStar = (DeltaNuSun / self.getDeltaNuCalculator().getCen()[0]) ** 2 * (self.getNuMax()[0] / NuMaxSun) * \
            sqrt(self.__Teff / TSun)

    def calculateLuminosity(self,TSun):
        if self.__Teff is None:
            print("Teff is None, no calculation of BC takes place")
            return None

        if self.__deltaNuCalculator is None:
            print("Delta Nu is not yet calculated, need to calculate that first")
            self.calculateDeltaNu()

        if self.__radiusStar is None:
            print("Radius not yet calculated, need to calculate that first")
            self.calculateRadius()

        self.__Luminosity = self.__radiusStar** 2 * (self.__Teff / TSun) ** 4


