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
        self._kicID = kicID
        self.runID = runID
        self.Teff = Teff
        self.dataFile = DataFile(kicID)
        self._summary = ParameterSummary(kicID, runID)
        self._evidence = Evidence(kicID, runID)
        self._prior = Priors(kicID)
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

        self._psdOnlyFlag = False

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
                    self._psdOnlyFlag = True

        if Teff is not None:
            self.TeffError = 200
            self._bolometricCorrCalculator = BCCalculator(Teff)
            self._bolometricCorrection = self._bolometricCorrCalculator.BC



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

    @property
    def prior(self):
        return self._prior

    @property
    def evidence(self):
        return self._evidence

    @property
    def summary(self):
        return self._summary

    @property
    def powerSpectralDensity(self):
        return self.dataFile.getPSD()

    @property
    def kicID(self):
        return self._kicID

    @property
    def nuMax(self):
        return self.numax

    @property
    def oscillationAmplitude(self):
        return self._oscillationAmplitude

    @property
    def sigma(self):
        return self._sigma

    @property
    def firstHarveyFrequency(self):
        return self._firstHarveyFrequency

    @property
    def secondHarveyFrequency(self):
        return self._secondHarveyFrequency

    @property
    def thirdHarveyFrequency(self):
        return self._thirdHarveyFrequency

    @property
    def firstHarveyAmplitude(self):
        return self._firstHarveyAmplitude

    @property
    def secondHarveyAmplitude(self):
        return self._secondHarveyAmplitude

    @property
    def thirdHarveyAmplitude(self):
        return self._thirdHarveyAmplitude

    @property
    def backgroundNoise(self):
        return self._backgroundNoise

    @property
    def psdOnlyFlag(self):
        return self._psdOnlyFlag

    @property
    def radiusStar(self):
        return self._radiusStar

    @property
    def bolometricCorrection(self):
        return self._bolometricCorrection

    @property
    def luminosity(self):
        return self._luminosity

    @property
    def distanceModulus(self):
        return self._distanceModulus

    @property
    def kicDistanceModulus(self):
        return self._kicDistanceModulus

    @property
    def robustnessValue(self):
        return abs(self._distanceModulus[0] - self._kicDistanceModulus) * 100 / self._distanceModulus[0]

    @property
    def robustnessSigma(self):
        return abs(self._distanceModulus[0] - self._kicDistanceModulus) / self._distanceModulus[1]

    @property
    def deltaNuCalculator(self):
        return self._deltaNuCalculator


    def calculateDeltaNu(self):
        backgroundModel = self.createBackgroundModel(True)
        par_median = self.summary.getData(strSummaryMedian)  # median values
        par_le = self.summary.getData(strSummaryLowCredLim)  # lower credible limits
        par_ue = self.summary.getData(strSummaryUpCredLim)   # upper credible limits
        backGroundParameters = np.vstack((par_median, par_le, par_ue))

        self._deltaNuCalculator = DeltaNuCalculator(self.numax[0], self._sigma[0], self.dataFile.getPSD(),
                                                    self.nyq, backGroundParameters, backgroundModel)

    def createBackgroundModel(self, runGauss):
        freq, psd = self.dataFile.getPSD()
        par_median = self.summary.getData(strSummaryMedian)  # median values
        par_le = self.summary.getData(strSummaryLowCredLim)  # lower credible limits
        par_ue = self.summary.getData(strSummaryUpCredLim) # upper credible limits
        if runGauss:
            self._backgroundNoise = (par_median[0], par_median[0] - par_le[0])
            self._firstHarveyAmplitude = (par_median[1], par_median[1] - par_le[1])
            self._firstHarveyFrequency = (par_median[2], par_median[2] - par_le[2])
            self._secondHarveyAmplitude = (par_median[3], par_median[3] - par_le[3])
            self._secondHarveyFrequency = (par_median[4], par_median[4] - par_le[4])
            self._thirdHarveyAmplitude = (par_median[5], par_median[5] - par_le[5])
            self._thirdHarveyFrequency = (par_median[6], par_median[6] - par_le[6])
            self._oscillationAmplitude = (par_median[7], par_median[7] - par_le[7])  # third last parameter
            self.numax = (par_median[8],par_median[8] - par_le[8])  # second last parameter
            self._sigma = (par_median[9], par_median[9] - par_le[9])  # last parameter

            self.logger.debug("Height is '" + str(self._oscillationAmplitude[0]) + "'")
            self.logger.debug("Numax is '" + str(self.numax[0]) + "'")
            self.logger.debug("Sigma is '" + str(self._sigma[0]) + "'")

        zeta = 2. * np.sqrt(2.) / np.pi  # !DPI is the pigreca value in double precision
        r = (np.sin(np.pi / 2. * freq / self.nyq) / (
        np.pi / 2. * freq / self.nyq)) ** 2  # ; responsivity (apodization) as a sinc^2
        w = par_median[0]  # White noise component
        g = 0
        if runGauss:
            g = self._oscillationAmplitude[0] * np.exp(-(self.numax[0] - freq) ** 2 / (2. * self._sigma[0] ** 2))  ## Gaussian envelope

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

        if self._deltaNuCalculator is None:
            self.logger.debug("Delta Nu is not yet calculated, need to calculate that first")
            self.calculateDeltaNu()

        self._radiusStar = (self.deltaNuCalculator.deltaNu[0] / DeltaNuSun) ** -2 * (self.nuMax[0] / NuMaxSun) * \
                           sqrt(self.Teff / TSun)

        errorNuMax = ((1/NuMaxSun) * (self.deltaNuCalculator.deltaNu[0] / DeltaNuSun) ** -2 *
                      sqrt(self.Teff/TSun) * self.nuMax[1])**2

        errorDeltaNu = ((self.deltaNuCalculator.deltaNu[0] / DeltaNuSun) ** -3 * (self.nuMax[0] / NuMaxSun) * \
                        sqrt(self.Teff / TSun) * (2 * self.deltaNuCalculator.deltaNu[1] / DeltaNuSun)) ** 2

        errorTemperature = ((self.deltaNuCalculator.deltaNu[0] / DeltaNuSun) ** -2 * (self.nuMax[0] / NuMaxSun) * \
                            self.TeffError / (TSun * sqrt(self.Teff / TSun)))**2

        error = sqrt(errorNuMax+errorDeltaNu+errorTemperature)

        self._radiusStar = (self._radiusStar, error)


    def calculateLuminosity(self,TSun):
        if self.Teff is None:
            self.logger.debug("Teff is None, no calculation of BC takes place")
            return None

        if self._deltaNuCalculator is None:
            self.logger.debug("Delta Nu is not yet calculated, need to calculate that first")
            self.calculateDeltaNu()

        if self._radiusStar is None:
            self.logger.debug("Radius not yet calculated, need to calculate that first")
            self.calculateRadius()

        self._luminosity = self._radiusStar[0] ** 2 * (self.Teff / TSun) ** 4

        errorRadius = (self._radiusStar[0] * (self.Teff / TSun) ** 4 * self._radiusStar[1] * 2) ** 2
        errorTemperature = (self._radiusStar[0] ** 2 * 4 * (self.TeffError / TSun) * (self.Teff / TSun) ** 3) ** 2

        error = sqrt(errorRadius + errorTemperature)

        self._luminosity = (self._luminosity, error)

    def calculateDistanceModulus(self,appMag,kicmag,magError,Av,NuMaxSun,DeltaNuSun,TSun):

        appMag = appMag if appMag != 0 else kicmag
        if self.Teff is None:
            self.logger.debug("TEff is None, no calculation of distance modulus takes place")
            return None

        if self._deltaNuCalculator is None:
            self.logger.debug("Delta Nu is not yet calculated, need to calculate that first")
            self.calculateDeltaNu()

        if self.numax is None:
            self.logger.debug("NuMax is not calculated, need nuMax to proceed")
            return None

        if self._bolometricCorrCalculator is None:
            self.logger.debug("BC is not yet calculated, need to calculate that first")
            self.calculate
            self._bolometricCorrCalculator = BCCalculator(self.Teff)
            self._bolometricCorrection = self._bolometricCorrCalculator.BC

        self._distanceModulus = (6 * log10(self.numax[0] / NuMaxSun) + 15 * log10(self.Teff / TSun) - 12 * log10(self._deltaNuCalculator.deltaNu[0] / DeltaNuSun) \
                                 + 1.2 * (appMag + self._bolometricCorrection) - 1.2 * Av[0] - 5.7) / 1.2

        self._kicDistanceModulus = (6 * log10(self.numax[0] / NuMaxSun) + 15 * log10(self.Teff / TSun) - 12 * log10(self._deltaNuCalculator.deltaNu[0] / DeltaNuSun) \
                                    + 1.2 * (kicmag + self._bolometricCorrection) - 1.2 * Av[0] - 5.7) / 1.2

        self.mu_diff = self._distanceModulus - self._kicDistanceModulus

        errorNuMax = (6*self.nuMax[1]/(self.nuMax[0]*log(10)*1.2))**2
        errorDeltaNu = ((12 * self.deltaNuCalculator.deltaNu[1] / (self.deltaNuCalculator.deltaNu[0] * log(10))) / 1.2) ** 2
        errorV = magError
        errorAv= (Av[1])**2
        errorTemperature = ((15/1.2)*(self.TeffError/self.Teff))**2

        self.logger.debug("Error"+str(errorNuMax)+","+str(errorDeltaNu)+","+str(errorV)+","+str(errorAv)+","+str(errorTemperature))
        error = sqrt(errorNuMax + errorDeltaNu+errorV+errorAv + errorTemperature)

        self._distanceModulus = (self._distanceModulus, error)

        return self._distanceModulus
