import glob
import logging

import numpy as np
from uncertainties import ufloat

from background.fileModels.backgroundDataFileModel import BackgroundDataFileModel
from background.fileModels.backgroundEvidenceFileModel import BackgroundEvidenceFileModel
from background.fileModels.backgroundMarginalDistrFileModel import BackgroundMarginalDistrFileModel
from background.fileModels.backgroundParamSummaryModel import BackgroundParamSummaryModel
from background.fileModels.backgroundParameterFileModel import BackgroundParameterFileModel
from background.fileModels.backgroundPriorFileModel import BackgroundPriorFileModel
from evaluators.bcEvaluator import BCEvaluator
from evaluators.deltaNuEvaluator import DeltaNuEvaluator
from res.strings import *
from settings.settings import Settings


class BackgroundResults:
    '''
    The results class is the core of all DIAMONDS files. It provides a common interface to the data fitted by
    DIAMONDS, you should therefore access all Data access through this channel. It also provides some calculation
    methods.

    This class represents a single Run for a single star. So if you want to access both fullBackground and noiseOnly you
     need to instantiate this class twice with a different runID
    '''

    def __init__(self, kicID, runID, tEff=None):
        '''
        The constructor of the class. It sets up all classes that provide an interface to the lower laying files
        from DIAMONDS. It also sets up some other things like names
        :param kicID: The KicID of the star
        :type kicID: string
        :param runID: The RunID of the star -> fullBackground or noiseOnly
        :type runID:string
        :param tEff: The effective temperature of the star. Used for calculations of radius, luminosity and distance
        modulus. An error of 200K is assumed. Optional
        :type tEff:float
        '''
        self.logger = logging.getLogger(__name__)
        self._kicID = kicID
        self._runID = runID
        self._dataFile = BackgroundDataFileModel(kicID)
        self._summary = BackgroundParamSummaryModel(kicID, runID)
        self._evidence = BackgroundEvidenceFileModel(kicID, runID)
        self._prior = BackgroundPriorFileModel(kicID, runID)
        self._backgroundPriors = BackgroundPriorFileModel(kicID, runID)
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

        self._psdOnlyFlag = False

        summaryRawData = self.summary.getRawData()

        for i in range(0, self.summary.dataLength()):
            self._backgroundParameter.append(
                BackgroundParameterFileModel(self._names[i], self._units[i], kicID, runID, i))
            self._marginalDistributions.append(
                BackgroundMarginalDistrFileModel(self._names[i], self._units[i], kicID, runID, i))
            self._marginalDistributions[i].backgrounddata = np.vstack((summaryRawData[strSummaryMedian][i],
                                                                       summaryRawData[strSummaryLowCredLim][i],
                                                                       summaryRawData[strSummaryUpCredLim][i]))
            if self._backgroundParameter[i].getData() is None:
                self._psdOnlyFlag = True

        if tEff is not None:
            self._tEff = ufloat(tEff, 200)
            self._bolometricCorrCalculator = BCEvaluator(tEff)
            self._bolometricCorrection = self._bolometricCorrCalculator.BC

    def getBackgroundParameters(self, key=None):
        '''
        Provides an interface for the single background Parameters (e.g. Noise,HarveyParameters, Powerexcess parameters)
        fitted by DIAMONDS. Depending on the mode, this will either return a list of 7-10 items or a single item
        if key is not None
        :param key: key for the parameter. Should be a name of a parameter --> see strings.py. Optional
        :type key:string
        :return:Full dict or single parameter depending on key
        :rtype:List/BackgroundParameterFileModel
        '''
        return self._getValueFromDict(self._backgroundParameter,key)

    def getMarginalDistribution(self, key=None):
        '''
        Returns single MarginalDistributions or full MarginalDistributions. Contains the MarginalDistributions class
        :param key: key for the Marginal Distribution
        :type key: string
        :rtype:list/MarginalDistribution
        '''
        return self._getValueFromDict(self._marginalDistributions,key)



    def _getValueFromDict(self,dict,key=None):
        '''
        This is a helper method, which returns a single item from a list if the item exists or the whole dict otherwhise
        :param dict: The list to search in
        :type dict: list
        :param key: The key. Optional
        :type key: str
        :return: The appropriate Value(s)
        '''
        if key is None:
            return dict
        else:
            for i in dict:
                if i.name == key:
                    return i

            self.logger.warning("Found no object for '" + key + "'")
            self.logger.warning("Returning full list")
            return dict

    @property
    def prior(self):
        '''
        Property for the prior object.
        :return: Returns the object that accesses the priors used for the DIAMONDS run.
        :rtype: BackgroundPriorFileModel
        '''
        return self._prior

    @property
    def evidence(self):
        '''
        Property for the evidence object
        :return: Returns the object that accesses the evidence generated by the DIAMONDS run.
        :rtype: Evidence
        '''
        return self._evidence

    @property
    def summary(self):
        '''
        Property for the summary object
        :return: Returns the object that accesses the summary generated by the DIAMONDS run.
        :rtype:ParameterSummary
        '''
        return self._summary

    @property
    def powerSpectralDensity(self):
        '''
        Property for the PSD
        :return: Returns the Array that contains the PSD used for the DIAMONDS run.
        :rtype: 2-D numpy array
        '''
        return self._dataFile.powerSpectralDensity

    @property
    def kicID(self):
        '''
        Property for the KicID of the star
        :return: Returns the KicID of the star
        :rtype: string
        '''
        return self._kicID

    @property
    def nuMax(self):
        '''
        Property for nuMax. Accessed through the _getSummaryParameter method, which accesses the _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        '''
        return self._getSummaryParameter(strPriorNuMax)

    @property
    def oscillationAmplitude(self):
        '''
        Property for power of osc. Accessed through the _getSummaryParameter method, which accesses the _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        '''
        return self._getSummaryParameter(strPriorHeight)

    @property
    def sigma(self):
        '''
        Property for the standard deviation of the powerexcess. Accessed through the _getSummaryParameter method, which
        accesses the _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        '''
        return self._getSummaryParameter(strPriorSigma)

    @property
    def firstHarveyFrequency(self):
        '''
        Property for first Harvey frequency. Accessed through the _getSummaryParameter method, which accesses the
        _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        '''
        return self._getSummaryParameter(strPriorFreqHarvey1)

    @property
    def secondHarveyFrequency(self):
        '''
        Property for second Harvey frequency. Accessed through the _getSummaryParameter method, which accesses the
        _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        '''
        return self._getSummaryParameter(strPriorFreqHarvey2)

    @property
    def thirdHarveyFrequency(self):
        '''
        Property for third Harvey frequency. Accessed through the _getSummaryParameter method, which accesses the
        _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        '''
        return self._getSummaryParameter(strPriorFreqHarvey3)

    @property
    def firstHarveyAmplitude(self):
        '''
        Property for first Harvey amplitude. Accessed through the _getSummaryParameter method, which accesses the
        _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        '''
        return self._getSummaryParameter(strPriorAmpHarvey1)

    @property
    def secondHarveyAmplitude(self):
        '''
        Property for second Harvey amplitude. Accessed through the _getSummaryParameter method, which accesses the
        _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        '''
        return self._getSummaryParameter(strPriorAmpHarvey2)

    @property
    def thirdHarveyAmplitude(self):
        '''
        Property for third Harvey amplitude. Accessed through the _getSummaryParameter method, which accesses the
        _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        '''
        return self._getSummaryParameter(strPriorAmpHarvey3)

    @property
    def backgroundNoise(self):
        '''
        Property for the background noise. Accessed through the _getSummaryParameter method, which accesses the
        _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        '''
        return self._getSummaryParameter(strPriorFlatNoise)


    def _getSummaryParameter(self, key=None):
        '''
        Returns the SummaryParameter, i.e. the value computed by DIAMONDS. Can be a single Parameter or a full dict
        if key is None
        :param key: Key for the dict -> see strings.py
        :type key: string
        :return: Single Parameter or full dict
        :rtype: dict/ufloat
        '''
        if key is not None and key in self.summary.getData().keys():
            return self.summary.getData(key)
        elif key is None:
            return self.summary.getData()
        else:
            self.logger.error(key + " is not in Summary -> did DIAMONDS run correctly?")
            if key in (strPriorNuMax, strPriorHeight, strPriorSigma):
                self.logger.error("Check if you used the correct runID. runID is " + self._runID)
            self.logger.error("Content of dict is")
            self.logger.error(self.summary.getData())
            raise ValueError

    def calculateDeltaNu(self):
        '''
        Computes delta nu using the deltaNuCalculator
        '''
        backgroundModel = self.createBackgroundModel()
        backGroundData = np.vstack((self.summary.getRawData(strSummaryMedian),
                                    self.summary.getRawData(strSummaryLowCredLim),
                                    self.summary.getRawData(strSummaryUpCredLim)))

        self._deltaNuCalculator = DeltaNuEvaluator(self.nuMax[0], self.sigma[0],
                                                   self._dataFile.powerSpectralDensity,
                                                   self._nyq, backGroundData, backgroundModel)

    def createBackgroundModel(self):
        '''
        Creates a full Background model
        :return: Background Model
        '''
        freq, psd = self._dataFile.powerSpectralDensity
        par_median = self.summary.getRawData(strSummaryMedian)  # median values
        runGauss = (self._runID is strDiamondsModeFull)
        if runGauss:
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
        if runGauss:
            retVal = zeta * h_long * r, zeta * h_gran1 * r, zeta * h_gran2 * r, w, g * r
        else:
            retVal = zeta * h_long * r, zeta * h_gran1 * r, zeta * h_gran2 * r, w

        return retVal