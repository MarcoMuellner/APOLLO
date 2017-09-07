import glob
import numpy as np
from scipy.signal import butter, filtfilt
from math import sqrt,log10,log

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
import logging


class Results:
    def __init__(self,kicID,runID,Teff = None):
        self.logger = logging.getLogger(__name__)
        self.kicID = kicID
        self.runID = runID
        self.Teff = Teff
        self.dataFile = DataFile(kicID)
        self.summary = ParameterSummary(kicID, runID)
        self.evidence = Evidence(kicID, runID)
        self.prior = Priors(kicID)
        self.backgroundPriors = Priors(kicID, runID)
        self.backgroundParameter = []
        self.marginalDistributions = []
        self.names = []
        self.units = []
        self.dataFolder = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundResPath).value
        nyqFile = glob.glob(self.dataFolder + 'KIC{}/NyquistFrequency.txt'.format(kicID))[0]
        self.nyq = np.loadtxt(nyqFile)

        self.names = ['w', '$\sigma_\mathrm{long}$', '$b_\mathrm{long}$', '$\sigma_\mathrm{gran,1}$',
                  '$b_\mathrm{gran,1}$', '$\sigma_\mathrm{gran,2}$', '$b_\mathrm{gran,2}$',
                  '$H_\mathrm{osc}$','$f_\mathrm{max}$ ', '$\sigma_\mathrm{env}$']

        self.units = ['ppm$^2$/$\mu$Hz', 'ppm', '$\mu$Hz', 'ppm', '$\mu$Hz', 'ppm', '$\mu$Hz', 'ppm$^2$/$\mu$Hz',
                        '$\mu$Hz','$\mu$Hz']

        self.m_PSDOnly = False

        for i in range(0,10):
            try:
                par_median = self.summary.getData(strSummaryMedian)[i]  # median values
                par_le = self.summary.getData(strSummaryLowCredLim)[i]  # lower credible limits
                par_ue = self.summary.getData(strSummaryUpCredLim)[i]  # upper credible limits
                backGroundParameters = np.vstack((par_median, par_le, par_ue))
            except:
                par_median = 0  # median values
                par_le = 0  # lower credible limits
                par_ue = 0  # upper credible limits
                backGroundParameters = np.vstack((par_median, par_le, par_ue))
                self.logger.debug("Problem creating median,le,ue values. Creating them with 0")
            if par_median != 0 or par_le != 0 or par_ue != 0:
                self.backgroundParameter.append(BackgroundParameter(self.names[i], self.units[i], kicID, runID, i))
                self.marginalDistributions.append(MarginalDistribution(self.names[i], self.units[i], kicID, runID, i))
                self.marginalDistributions[i].setBackgroundParameters(backGroundParameters)
                if self.backgroundParameter[i].getData() is None:
                    self.m_PSDOnly = True

        if Teff is not None:
            self.TeffError = 200
            self.BCCalculator = BCCalculator(Teff)
            self.BC = self.BCCalculator.BC



    def getBackgroundParameters(self,key = None):
        if key is None:
            return self.backgroundParameter
        else:
            for i in self.backgroundParameter:
                if i.getName == key:
                    return self.backgroundParameter[i]

            self.logger.debug("Found no background parameter for '"+key+"'")
            self.logger.debug("Returning full list")
            return self.backgroundParameter

    def getPrior(self):
        return self.prior

    def getBackgroundPrior(self):
        return self.backgroundPriors

    def getEvidence(self):
        return self.evidence

    def getSummary(self):
        return self.summary

    def getNyquistFrequency(self):
        return self.nyq

    def getPSD(self):
        return self.dataFile.getPSD()

    def getSmoothing(self):
        return self.__butter_lowpass_filtfilt(self.dataFile.getPSD()[1])

    def getKicID(self):
        return self.kicID

    def getNuMax(self):
        return self.numax

    def getHg(self):
        return self.hg

    def getSigma(self):
        return self.sigma

    def getFirstHarveyFrequency(self):
        return self.harveyF1

    def getSecondHarveyFrequency(self):
        return self.harveyF2

    def getThirdHarveyFrequency(self):
        return self.harveyF3

    def getFirstHarveyAmplitude(self):
        return self.harveyA1

    def getSecondHarveyAmplitude(self):
        return self.harveyA2

    def getThirdHarveyAmplitude(self):
        return self.harveyA3

    def getBackgroundNoise(self):
        return self.bgNoise

    def getGaussBoundaries(self):
        return self.gaussBoundaries

    def getPSDOnly(self):
        return self.m_PSDOnly

    def getRadius(self):
        return self.radiusStar

    def getBC(self):
        return self.BC

    def getLuminosity(self):
        return self.Luminosity

    def getDistanceModulus(self):
        return self.mu

    def getKICDistanceModulus(self):
        return self.mu_kic

    def getRobustnessValue(self):
        return abs(self.mu[0]-self.mu_kic)*100/self.mu[0]

    def getRobustnessSigma(self):
        return abs(self.mu[0]-self.mu_kic)/self.mu[1]

    def calculateDeltaNu(self):
        backgroundModel = self.createBackgroundModel(True)
        par_median = self.summary.getData(strSummaryMedian)  # median values
        par_le = self.summary.getData(strSummaryLowCredLim)  # lower credible limits
        par_ue = self.summary.getData(strSummaryUpCredLim)   # upper credible limits
        backGroundParameters = np.vstack((par_median, par_le, par_ue))

        self.deltaNuCalculator = DeltaNuCalculator(self.numax[0], self.sigma[0], self.dataFile.getPSD(),
                                                     self.nyq, backGroundParameters, backgroundModel)

    def getDeltaNuCalculator(self):
        return self.deltaNuCalculator

    def getBCCalculator(self):
        return self.BCCalculator

    def __butter_lowpass_filtfilt(self,data,order=5):
        b, a = self.__butter_lowpass(0.7, order=order) # todo 0.7 is just empirical, this may work better with something else?
        psd = data
        self.smoothedData = filtfilt(b, a, psd)
        return self.smoothedData

    def __butter_lowpass(self,cutoff, order=5):#todo these should be reworked and understood properly!
        normal_cutoff = cutoff / self.nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a


    def createBackgroundModel(self, runGauss):
        freq, psd = self.dataFile.getPSD()
        par_median = self.summary.getData(strSummaryMedian)  # median values
        par_le = self.summary.getData(strSummaryLowCredLim)  # lower credible limits
        par_ue = self.summary.getData(strSummaryUpCredLim) # upper credible limits
        if runGauss:
            self.bgNoise = (par_median[0],par_median[0] - par_le[0])
            self.harveyA1 = (par_median[1],par_median[1] - par_le[1])
            self.harveyF1 = (par_median[2],par_median[2] - par_le[2])
            self.harveyA2 = (par_median[3],par_median[3] - par_le[3])
            self.harveyF2 = (par_median[4],par_median[4] - par_le[4])
            self.harveyA3 = (par_median[5],par_median[5] - par_le[5])
            self.harveyF3 = (par_median[6],par_median[6] - par_le[6])
            self.hg = (par_median[7],par_median[7] - par_le[7])  # third last parameter
            self.numax = (par_median[8],par_median[8] - par_le[8])  # second last parameter
            self.sigma = (par_median[9],par_median[9] - par_le[9])  # last parameter

            self.logger.debug("Height is '" + str(self.hg[0]) + "'")
            self.logger.debug("Numax is '" + str(self.numax[0]) + "'")
            self.logger.debug("Sigma is '" + str(self.sigma[0]) + "'")

        zeta = 2. * np.sqrt(2.) / np.pi  # !DPI is the pigreca value in double precision
        r = (np.sin(np.pi / 2. * freq / self.nyq) / (
        np.pi / 2. * freq / self.nyq)) ** 2  # ; responsivity (apodization) as a sinc^2
        w = par_median[0]  # White noise component
        g = 0
        if runGauss:
            g = self.hg[0] * np.exp(-(self.numax[0] - freq) ** 2 / (2. * self.sigma[0] ** 2))  ## Gaussian envelope

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
        self.logger.debug(w)
        w = np.zeros_like(freq) + w
        b1 = zeta * (h_long + h_gran1 + h_gran2) * r + w
        self.logger.debug("Whitenoise is '" + str(w) + "'")
        if runGauss:
            b2 = (zeta * (h_long + h_gran1 + h_gran2) + g) * r + w
            return zeta * h_long * r, zeta * h_gran1 * r, zeta * h_gran2 * r, w, g * r
        else:
            return zeta * h_long * r, zeta * h_gran1 * r, zeta * h_gran2 * r, w


    def createMarginalDistribution(self,key = None):
        if key is None:
            return self.marginalDistributions
        else:
            for i in self.marginalDistributions:
                if i.getName() == key:
                    return self.marginalDistributions[i]

            self.logger.debug("Found no marginal Distribution for '"+key+"'")
            self.logger.debug("Returning full list")
            return self.marginalDistributions

    def calculateRadius(self,TSun,NuMaxSun,DeltaNuSun):
        if self.Teff is None:
            self.logger.debug("Teff is None, no calculation of BC takes place")
            return None

        if self.numax is None:
            self.logger.debug("NuMax is not calculated, need nuMax to proceed")
            return None

        if self.deltaNuCalculator is None:
            self.logger.debug("Delta Nu is not yet calculated, need to calculate that first")
            self.calculateDeltaNu()

        self.radiusStar = (self.getDeltaNuCalculator().deltaNu[0] / DeltaNuSun) ** -2 * (self.getNuMax()[0] / NuMaxSun) * \
                          sqrt(self.Teff / TSun)

        errorNuMax = ((1/NuMaxSun) * (self.getDeltaNuCalculator().deltaNu[0] / DeltaNuSun) ** -2 *
                      sqrt(self.Teff/TSun) * self.getNuMax()[1])**2

        errorDeltaNu = ((self.getDeltaNuCalculator().deltaNu[0] / DeltaNuSun) ** -3 * (self.getNuMax()[0] / NuMaxSun) * \
                        sqrt(self.Teff / TSun) * (2 * self.getDeltaNuCalculator().deltaNu[1] / DeltaNuSun)) ** 2

        errorTemperature = ((self.getDeltaNuCalculator().deltaNu[0] / DeltaNuSun) ** -2 * (self.getNuMax()[0] / NuMaxSun) * \
                            self.TeffError / (TSun * sqrt(self.Teff / TSun)))**2

        error = sqrt(errorNuMax+errorDeltaNu+errorTemperature)

        self.radiusStar = (self.radiusStar,error)


    def calculateLuminosity(self,TSun):
        if self.Teff is None:
            self.logger.debug("Teff is None, no calculation of BC takes place")
            return None

        if self.deltaNuCalculator is None:
            self.logger.debug("Delta Nu is not yet calculated, need to calculate that first")
            self.calculateDeltaNu()

        if self.radiusStar is None:
            self.logger.debug("Radius not yet calculated, need to calculate that first")
            self.calculateRadius()

        self.Luminosity = self.radiusStar[0]** 2 * (self.Teff / TSun) ** 4

        errorRadius = (self.radiusStar[0] * (self.Teff / TSun) ** 4 *self.radiusStar[1] *2)**2
        errorTemperature = (self.radiusStar[0]** 2 *4* (self.TeffError / TSun) *(self.Teff / TSun) ** 3)**2

        error = sqrt(errorRadius + errorTemperature)

        self.Luminosity = (self.Luminosity,error)

    def calculateDistanceModulus(self,appMag,kicmag,magError,Av,NuMaxSun,DeltaNuSun,TSun):

        appMag = appMag if appMag != 0 else kicmag
        if self.Teff is None:
            self.logger.debug("TEff is None, no calculation of distance modulus takes place")
            return None

        if self.deltaNuCalculator is None:
            self.logger.debug("Delta Nu is not yet calculated, need to calculate that first")
            self.calculateDeltaNu()

        if self.numax is None:
            self.logger.debug("NuMax is not calculated, need nuMax to proceed")
            return None

        if self.BCCalculator is None:
            self.logger.debug("BC is not yet calculated, need to calculate that first")
            self.calculate
            self.BCCalculator = BCCalculator(self.Teff)
            self.BC = self.BCCalculator.BC

        self.mu = (6*log10(self.numax[0]/NuMaxSun)+15*log10(self.Teff/TSun) -12*log10(self.deltaNuCalculator.deltaNu[0] / DeltaNuSun)\
                    +1.2*(appMag + self.BC) -1.2*Av[0] - 5.7)/1.2

        self.mu_kic = (6*log10(self.numax[0]/NuMaxSun)+15*log10(self.Teff/TSun) -12*log10(self.deltaNuCalculator.deltaNu[0] / DeltaNuSun)\
                    +1.2*(kicmag + self.BC) -1.2*Av[0] - 5.7)/1.2

        self.mu_diff = self.mu-self.mu_kic

        errorNuMax = (6*self.getNuMax()[1]/(self.getNuMax()[0]*log(10)*1.2))**2
        errorDeltaNu = ((12 * self.getDeltaNuCalculator().deltaNu[1] / (self.getDeltaNuCalculator().deltaNu[0] * log(10))) / 1.2) ** 2
        errorV = magError
        errorAv= (Av[1])**2
        errorTemperature = ((15/1.2)*(self.TeffError/self.Teff))**2

        self.logger.debug("Error"+str(errorNuMax)+","+str(errorDeltaNu)+","+str(errorV)+","+str(errorAv)+","+str(errorTemperature))
        error = sqrt(errorNuMax + errorDeltaNu+errorV+errorAv + errorTemperature)

        self.mu = (self.mu,error)

        return self.mu
