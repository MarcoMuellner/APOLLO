import glob
import logging

from typing import Dict,Union,List
import numpy as np
from copy import deepcopy
from uncertainties import ufloat

from background.fileModels.backgroundDataFileModel import BackgroundDataFileModel
from background.fileModels.backgroundEvidenceFileModel import BackgroundEvidenceFileModel
from background.fileModels.backgroundMarginalDistrFileModel import BackgroundMarginalDistrFileModel
from background.fileModels.backgroundParamSummaryModel import BackgroundParamSummaryModel
from background.fileModels.backgroundParameterFileModel import BackgroundParameterFileModel
from background.fileModels.backgroundPriorFileModel import BackgroundPriorFileModel
from res.strings import *
from support.printer import print_int
from data_handler.signal_features import background_model

from res.conf_file_str import general_kic, general_background_result_path,internal_noise_value


class BackgroundResults:
    '''
    The results class is the core of all DIAMONDS files. It provides a common interface to the data fitted by
    DIAMONDS, you should therefore access all Data access through this channel. It also provides some calculation
    methods.

    This class represents a single Run for a single star. So if you want to access both fullBackground and noiseOnly you
     need to instantiate this class twice with a different runID
    '''

    def __init__(self, kwargs: Dict, runID: str):
        '''
        The constructor of the class. It sets up all classes that provide an interface to the lower laying files
        from DIAMONDS. It also sets up some other things like names
        :param kicID: The KicID of the star
        :param runID: The RunID of the star -> fullBackground or noiseOnly
        :param tEff: The effective temperature of the star. Used for calculations of radius, luminosity and distance
        modulus. An error of 200K is assumed. Optional
        '''
        self.logger = logging.getLogger(__name__)

        self.kwargs = deepcopy(kwargs)

        kic = self.kwargs[general_kic]
        if internal_noise_value in kwargs.keys():
            kic_new = str(kic) + f"_{kwargs[internal_noise_value]}"
        else:
            kic_new = kic
        self.kwargs[general_kic] = kic_new
        self._kicID = self.kwargs[general_kic]
        self._runID = runID
        self._dataFile = BackgroundDataFileModel(self.kwargs)
        try:
            self._summary = BackgroundParamSummaryModel(self.kwargs, runID)
        except FileNotFoundError:
            self._summary = None
        self._evidence = BackgroundEvidenceFileModel(self.kwargs, runID)
        #self._prior = BackgroundPriorFileModel(self.kwargs, runID)
        self._backgroundPriors = BackgroundPriorFileModel(self.kwargs, runID)
        self._backgroundParameter = []
        self._marginalDistributions = []
        self._dataFolder = self.kwargs[general_background_result_path]
        self._nyq = float(
            np.loadtxt(glob.glob(self._dataFolder + 'KIC{}/NyquistFrequency.txt'.format(self.kwargs[general_kic]))[0]))
        self._names = priorNames
        self._units = priorUnits
        self._psdOnlyFlag = False
        #self._readBackgroundParameter()

    def getBackgroundParameters(self, key: str = None) ->Union[BackgroundParameterFileModel,List[BackgroundParameterFileModel]]:
        '''
        Provides an interface for the single background Parameters (e.g. Noise,HarveyParameters, Powerexcess parameters)
        fitted by DIAMONDS. Depending on the mode, this will either return a list of 7-10 items or a single item
        if key is not None
        :param key: key for the parameter. Should be a name of a parameter --> see strings.py. Optional
        :return:Full dict or single parameter depending on key
        :rtype:List/BackgroundParameterFileModel
        '''
        return self._getValueFromDict(self._backgroundParameter, key)

    def getMarginalDistribution(self, key: str = None):
        '''
        Returns single MarginalDistributions or full MarginalDistributions. Contains the MarginalDistributions class
        :param key: key for the Marginal Distribution
        :rtype:list/MarginalDistribution
        '''
        return self._getValueFromDict(self._marginalDistributions, key)

    def _getValueFromDict(self, dict: dict, key: str = None):
        '''
        This is a helper method, which returns a single item from a list if the item exists or the whole dict otherwhise
        :param dict: The list to search in
        :param key: The key. Optional
        :return: The appropriate Value(s)
        '''
        if key is None:
            return dict
        else:
            for i in dict:
                if i.name == key:
                    return i

            print_int("Found no object for '" + key + "'", self.kwargs)
            print_int("Returning full list", self.kwargs)
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

    def _getSummaryParameter(self, key: str = None):
        '''
        Returns the SummaryParameter, i.e. the value computed by DIAMONDS. Can be a single Parameter or a full dict
        if key is None
        :param key: Key for the dict -> see strings.py
        :return: Single Parameter or full dict
        :rtype: dict/ufloat
        '''
        if key is not None and key in self.summary.getData().keys():
            return self.summary.getData(key)
        elif key is None:
            return self.summary.getData()
        else:
            raise ValueError(key + " is not in Summary -> did DIAMONDS run correctly?")

    def createBackgroundModel(self):
        '''
        Creates a full Background model
        :return: Background Model
        '''
        psd = self._dataFile.powerSpectralDensity.T
        par_median = self.summary.getRawData(strSummaryMedian)  # median values

        w = par_median[0]  # White noise component
        sigma_long = par_median[1]
        freq_long = par_median[2]
        sigma_gran1 = par_median[3]
        freq_gran1 = par_median[4]
        sigma_gran2 = par_median[5]
        freq_gran2 = par_median[6]

        runGauss = (self._runID is strDiModeFull)
        if runGauss:
            nu_max = self.nuMax.n
            amp = self.oscillationAmplitude.n
            sigma = self.sigma.n
        else:
            nu_max = None
            amp = None
            sigma = None

        return background_model(psd, self._nyq, w, sigma_long, freq_long, sigma_gran1, freq_gran1, sigma_gran2,
                                freq_gran2, nu_max, amp, sigma)

    def _readBackgroundParameter(self):
        for i in range(0, len(self._backgroundPriors.getData())):
            try:
                self._backgroundParameter.append(
                    BackgroundParameterFileModel(self._names[i], self._units[i], self.kwargs, self._runID, i))
            except (IOError,ValueError) as e:
                print_int("Failed to find backgroundparameter for " + self._names[i], self.kwargs)
            try:
                self._marginalDistributions.append(
                    BackgroundMarginalDistrFileModel(self._names[i], self._units[i], self.kwargs, self._runID, i))
                if self._summary is not None:
                    self._marginalDistributions[i]._backgroundData = np.vstack(
                        (self.summary.getRawData()[strSummaryMedian][i],
                         self.summary.getRawData()[strSummaryLowCredLim][i],
                         self.summary.getRawData()[strSummaryUpCredLim][i]))

                    if self._backgroundParameter[i].getData() is None:
                        self._psdOnlyFlag = True
            except Exception as e:
                pass
                #print_int("Failed to find marginal distribution for " + self._names[i], self.kwargs)
