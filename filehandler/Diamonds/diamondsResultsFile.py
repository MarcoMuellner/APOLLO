import glob
import logging
from math import sqrt, log10, log

import numpy as np

from calculations.bolometricCorrectionCalculations import BCCalculator
from calculations.deltaNuCalculations import DeltaNuCalculator
from filehandler.Diamonds.InternalStructure.backgroundEvidenceInformationFile import Evidence
from filehandler.Diamonds.InternalStructure.backgroundMarginalDistributionFile import MarginalDistribution
from filehandler.Diamonds.InternalStructure.backgroundParameterFile import BackgroundParameter
from filehandler.Diamonds.InternalStructure.backgroundParameterSummaryFile import ParameterSummary
from filehandler.Diamonds.dataFile import DataFile
from filehandler.Diamonds.diamondsPriorsFile import PriorSetup
from settings.settings import Settings
from support.strings import *


class Results:
    """
    This is the core of all the Files for one RunID. It summarizes every file within the Background file structure
    and gives them usefulness for further use. You probably want to use this class to access the data created by
    DIAMONDS, as it handles most of the fiddling with filenames and calculations.
    """
    def __init__(self, kicID, runID, tEff = None):
        self.logger = logging.getLogger(__name__)
        self._kicID = kicID
        self._runID = runID
        self._tEff = tEff
        self._dataFile = DataFile(kicID)
        self._summary = ParameterSummary(kicID, runID)
        self._evidence = Evidence(kicID, runID)
        self._prior = PriorSetup(kicID)
        self._backgroundPriors = PriorSetup(kicID, runID)
        self._backgroundParameter = []
        self._marginalDistributions = []
        self._dataFolder = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundResPath).value
        nyqFile = glob.glob(self._dataFolder + 'KIC{}/NyquistFrequency.txt'.format(kicID))[0]
        self._nyq = float(np.loadtxt(nyqFile))

        self._names = [strPriorFlatNoise,
                       strPriorAmpHarvey1,
                       strPriorFreqHarvey1,
                       strPriorAmpHarvey2,
                       strPriorFreqHarvey2,
                       strPriorAmpHarvey3,
                       strPriorFreqHarvey3,
                       strPriorHeight,
                       strPriorNuMax,
                       strPriorSigma]

        self._units = [strPriorUnitFlatNoise,
                       strPriorUnitAmpHarvey1,
                       strPriorUnitFreqHarvey1,
                       strPriorUnitAmpHarvey2,
                       strPriorUnitFreqHarvey2,
                       strPriorUnitAmpHarvey3,
                       strPriorUnitFreqHarvey3,
                       strPriorUnitHeight,
                       strPriorUnitNuMax,
                       strPriorUnitSigma]

        self.psdOnlyFlag = False

        summaryRawData = self.summary.getRawData()

        for i in range(0,self.summary.dataLength()):
            self._backgroundParameter.append(BackgroundParameter(self._names[i],self._units[i],kicID,runID,i))
            self._marginalDistributions.append(MarginalDistribution(self._names[i],self._units[i],kicID,runID,i))
            self._marginalDistributions[i].backgrounddata = np.vstack((summaryRawData[strSummaryMedian][i],
                                                                      summaryRawData[strSummaryLowCredLim][i],
                                                                      summaryRawData[strSummaryUpCredLim][i]))
            if self._backgroundParameter[i].getData() is None:
                self.psdOnlyFlag = True

        if tEff is not None:
            self._teffError = 200
            self._bolometricCorrCalculator = BCCalculator(tEff)
            self.bolometricCorrection = self._bolometricCorrCalculator.BC



    def getBackgroundParameters(self,key = None):
        if key is None:
            return self._backgroundParameter
        else:
            for i in self._backgroundParameter:
                if i.name == key:
                    return self._backgroundParameter[i]

            self.logger.debug("Found no background parameter for '"+key+"'")
            self.logger.debug("Returning full list")
            return self._backgroundParameter

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
        return self._dataFile.powerSpectralDensity

    @property
    def kicID(self):
        return self._kicID

    @property
    def nuMax(self):
        return self._getSummaryParameter(strPriorNuMax)

    @property
    def oscillationAmplitude(self):
        return self._getSummaryParameter(strPriorHeight)

    @property
    def sigma(self):
        return self._getSummaryParameter(strPriorSigma)

    @property
    def firstHarveyFrequency(self):
        return self._getSummaryParameter(strPriorFreqHarvey1)

    @property
    def secondHarveyFrequency(self):
        return self._getSummaryParameter(strPriorFreqHarvey2)

    @property
    def thirdHarveyFrequency(self):
        return self._getSummaryParameter(strPriorFreqHarvey3)

    @property
    def firstHarveyAmplitude(self):
        return self._getSummaryParameter(strPriorAmpHarvey1)

    @property
    def secondHarveyAmplitude(self):
        return self._getSummaryParameter(strPriorAmpHarvey2)

    @property
    def thirdHarveyAmplitude(self):
        return self._getSummaryParameter(strPriorAmpHarvey3)

    @property
    def backgroundNoise(self):
        return self._getSummaryParameter(strPriorFlatNoise)

    @property
    def psdOnlyFlag(self):
        return self._psdOnlyFlag

    @psdOnlyFlag.setter
    def psdOnlyFlag(self,value):
        self._psdOnlyFlag = value

    @property
    def radiusStar(self):
        return self._radiusStar

    @radiusStar.setter
    def radiusStar(self,value):
        self._radiusStar = value

    @property
    def bolometricCorrection(self):
        return self._bolometricCorrection

    @bolometricCorrection.setter
    def bolometricCorrection(self,value):
        self._bolometricCorrection = value

    @property
    def luminosity(self):
        return self._luminosity

    @luminosity.setter
    def luminosity(self,value):
        self._luminosity = value

    @property
    def distanceModulus(self):
        return self._distanceModulus

    @distanceModulus.setter
    def distanceModulus(self,value):
        self._distanceModulus = value

    @property
    def kicDistanceModulus(self):
        return self._kicDistanceModulus

    @property
    def robustnessValue(self):
        return abs(self.distanceModulus[0] - self.kicDistanceModulus) * 100 / self.distanceModulus[0]

    @property
    def robustnessSigma(self):
        return abs(self.distanceModulus[0] - self.kicDistanceModulus) / self.distanceModulus[1]

    @property
    def deltaNuCalculator(self):
        return self._deltaNuCalculator

    @deltaNuCalculator.setter
    def deltaNuCalculator(self,value):
        self._deltaNuCalculator = value

    def _getSummaryParameter(self,key):
        if key in self.summary.getData().keys():
            return self.summary.getData(key)
        else:
            self.logger.error(key + " is not in Summary -> did DIAMONDS run correctly?")
            if key in (strPriorNuMax,strPriorHeight,strPriorSigma):
                self.logger.error("Check if you used the correct runID. runID is "+self._runID)
            self.logger.error("Content of dict is")
            self.logger.error(self.summary.getData())
            raise ValueError

    def calculateDeltaNu(self):
        backgroundModel = self.createBackgroundModel((self._runID is strDiamondsModeFull))
        backGroundData = np.vstack((self.summary.getRawData(strSummaryMedian),
                                    self.summary.getRawData(strSummaryLowCredLim),
                                    self.summary.getRawData(strSummaryUpCredLim)))

        self.deltaNuCalculator = DeltaNuCalculator(self.nuMax[0], self.sigma[0],
                                                    self._dataFile.powerSpectralDensity,
                                                    self._nyq, backGroundData, backgroundModel)

    def createBackgroundModel(self, runGauss):
        freq, psd = self._dataFile.powerSpectralDensity
        par_median = self.summary.getRawData(strSummaryMedian)  # median values
        par_le = self.summary.getRawData(strSummaryLowCredLim)  # lower credible limits

        if runGauss and self._runID is strDiamondsModeFull:
            self.logger.debug("Height is '" + str(self.oscillationAmplitude) + "'")
            self.logger.debug("Numax is '" + str(self.nuMax) + "'")
            self.logger.debug("Sigma is '" + str(self.sigma) + "'")
            g = self.oscillationAmplitude.n * np.exp(
                -(self.nuMax.n - freq) ** 2 / (2. * self.sigma.n ** 2))  ## Gaussian envelope
        else:
            g = 0


        zeta = 2. * np.sqrt(2.) / np.pi  # !DPI is the pigreca value in double precision
        r = (np.sin(np.pi / 2. * freq / self._nyq) / (
        np.pi / 2. * freq / self._nyq)) ** 2  # ; responsivity (apodization) as a sinc^2
        w = par_median[0]  # White noise component

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
        w = np.zeros_like(freq) + w
        self.logger.debug("Whitenoise is '" + str(w) + "'")
        if runGauss and self._runID is strDiamondsModeFull:
            retVal =zeta * h_long * r, zeta * h_gran1 * r, zeta * h_gran2 * r, w, g * r
        else:
            retVal =  zeta * h_long * r, zeta * h_gran1 * r, zeta * h_gran2 * r, w

        return retVal


    def getMarginalDistribution(self, key = None):
        if key is None:
            return self._marginalDistributions
        else:
            for i in self._marginalDistributions:
                if i.name == key:
                    return self._marginalDistributions[i]

            self.logger.debug("Found no marginal Distribution for '"+key+"'")
            self.logger.debug("Returning full list")
            return self._marginalDistributions

    def calculateRadius(self,TSun,NuMaxSun,DeltaNuSun):
        if self._tEff is None:
            self.logger.debug("Teff is None, no calculation of BC takes place")
            return None

        if self.nuMax is None:
            self.logger.debug("NuMax is not calculated, need nuMax to proceed")
            return None

        if self.deltaNuCalculator is None:
            self.logger.debug("Delta Nu is not yet calculated, need to calculate that first")
            self.calculateDeltaNu()

        self.radiusStar = (self.deltaNuCalculator.deltaNu[0] / DeltaNuSun) ** -2 * (self.nuMax[0] / NuMaxSun) * \
                           sqrt(self._tEff / TSun)

        errorNuMax = ((1/NuMaxSun) * (self.deltaNuCalculator.deltaNu[0] / DeltaNuSun) ** -2 *
                      sqrt(self._tEff / TSun) * self.nuMax[1]) ** 2

        errorDeltaNu = ((self.deltaNuCalculator.deltaNu[0] / DeltaNuSun) ** -3 * (self.nuMax[0] / NuMaxSun) * \
                        sqrt(self._tEff / TSun) * (2 * self.deltaNuCalculator.deltaNu[1] / DeltaNuSun)) ** 2

        errorTemperature = ((self.deltaNuCalculator.deltaNu[0] / DeltaNuSun) ** -2 * (self.nuMax[0] / NuMaxSun) * \
                            self._teffError / (TSun * sqrt(self._tEff / TSun))) ** 2

        error = sqrt(errorNuMax+errorDeltaNu+errorTemperature)

        self.radiusStar = (self.radiusStar, error)


    def calculateLuminosity(self,TSun):
        if self._tEff is None:
            self.logger.debug("Teff is None, no calculation of BC takes place")
            return None

        if self.deltaNuCalculator is None:
            self.logger.debug("Delta Nu is not yet calculated, need to calculate that first")
            self.calculateDeltaNu()

        if self.radiusStar is None:
            self.logger.debug("Radius not yet calculated, need to calculate that first")
            self.calculateRadius()

        self.luminosity = self.radiusStar[0] ** 2 * (self._tEff / TSun) ** 4

        errorRadius = (self.radiusStar[0] * (self._tEff / TSun) ** 4 * self.radiusStar[1] * 2) ** 2
        errorTemperature = (self.radiusStar[0] ** 2 * 4 * (self._teffError / TSun) * (self._tEff / TSun) ** 3) ** 2

        error = sqrt(errorRadius + errorTemperature)

        self.luminosity = (self.luminosity, error)

    def calculateDistanceModulus(self,appMag,kicmag,magError,Av,NuMaxSun,DeltaNuSun,TSun):

        appMag = appMag if appMag != 0 else kicmag
        if self._tEff is None:
            self.logger.debug("TEff is None, no calculation of distance modulus takes place")
            return None

        if self.deltaNuCalculator is None:
            self.logger.debug("Delta Nu is not yet calculated, need to calculate that first")
            self.calculateDeltaNu()

        if self.nuMax is None:
            self.logger.debug("NuMax is not calculated, need nuMax to proceed")
            return None

        if self._bolometricCorrCalculator is None:
            self.logger.debug("BC is not yet calculated, need to calculate that first")
            self._bolometricCorrCalculator = BCCalculator(self._tEff)
            self.bolometricCorrection = self._bolometricCorrCalculator.BC

        self.distanceModulus = (6 * log10(self.nuMax[0] / NuMaxSun) + 15 * log10(self._tEff / TSun) - 12 * log10(self.deltaNuCalculator.deltaNu[0] / DeltaNuSun) \
                                 + 1.2 * (appMag + self.bolometricCorrection) - 1.2 * Av[0] - 5.7) / 1.2

        self.kicDistanceModulus = (6 * log10(self.nuMax[0] / NuMaxSun) + 15 * log10(self._tEff / TSun) - 12 * log10(self.deltaNuCalculator.deltaNu[0] / DeltaNuSun) \
                                    + 1.2 * (kicmag + self.bolometricCorrection) - 1.2 * Av[0] - 5.7) / 1.2

        self.mu_diff = self.distanceModulus - self.kicDistanceModulus

        errorNuMax = (6*self.nuMax[1]/(self.nuMax[0]*log(10)*1.2))**2
        errorDeltaNu = ((12 * self.deltaNuCalculator.deltaNu[1] / (self.deltaNuCalculator.deltaNu[0] * log(10))) / 1.2) ** 2
        errorV = magError
        errorAv= (Av[1])**2
        errorTemperature = ((15/1.2) * (self._teffError / self._tEff)) ** 2

        self.logger.debug("Error"+str(errorNuMax)+","+str(errorDeltaNu)+","+str(errorV)+","+str(errorAv)+","+str(errorTemperature))
        error = sqrt(errorNuMax + errorDeltaNu+errorV+errorAv + errorTemperature)

        self.distanceModulus = (self.distanceModulus, error)

        return self.distanceModulus
