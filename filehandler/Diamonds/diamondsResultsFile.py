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
from uncertainties import ufloat


class Results:
    """
    The results class is the core of all DIAMONDS files. It provides a common interface to the data fitted by
    DIAMONDS, you should therefore access all Data access through this channel. It also provides some calculation
    methods.

    This class represents a single Run for a single star. So if you want to access both fullBackground and noiseOnly you
     need to instantiate this class twice with a different runID
    """
    def __init__(self, kicID, runID, tEff = None):
        """
        The constructor of the class. It sets up all classes that provide an interface to the lower laying files
        from DIAMONDS. It also sets up some other things like names
        :param kicID: The KicID of the star
        :type kicID: string
        :param runID: The RunID of the star -> fullBackground or noiseOnly
        :type runID:string
        :param tEff: The effective temperature of the star. Used for calculations of radius, luminosity and distance
        modulus. An error of 200K is assumed. Optional
        :type tEff:float
        """
        self.logger = logging.getLogger(__name__)
        self._kicID = kicID
        self._runID = runID
        self._dataFile = DataFile(kicID)
        self._summary = ParameterSummary(kicID, runID)
        self._evidence = Evidence(kicID, runID)
        self._prior = PriorSetup(kicID,runID)
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
            self._tEff = ufloat(tEff,200)
            self._bolometricCorrCalculator = BCCalculator(tEff)
            self.bolometricCorrection = self._bolometricCorrCalculator.BC



    def getBackgroundParameters(self,key = None):
        """
        Provides an interface for the single background Parameters (e.g. Noise,HarveyParameters, Powerexcess parameters)
        fitted by DIAMONDS. Depending on the mode, this will either return a dict of 7-10 items or a single item
        if key is not None
        :param key: key for the dictionary. Should be a name of a parameter --> see strings.py. Optional
        :type key:string
        :return:Full dict or single parameter depending on key
        :rtype:Dict/BackgroundParameter
        """
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
        """
        Property for the prior object.
        :return: Returns the object that accesses the priors used for the DIAMONDS run.
        :rtype: PriorSetup
        """
        return self._prior

    @property
    def evidence(self):
        """
        Property for the evidence object
        :return: Returns the object that accesses the evidence generated by the DIAMONDS run.
        :rtype: Evidence
        """
        return self._evidence

    @property
    def summary(self):
        """
        Property for the summary object
        :return: Returns the object that accesses the summary generated by the DIAMONDS run.
        :rtype:ParameterSummary
        """
        return self._summary

    @property
    def powerSpectralDensity(self):
        """
        Property for the PSD
        :return: Returns the Array that contains the PSD used for the DIAMONDS run.
        :rtype: 2-D numpy array
        """
        return self._dataFile.powerSpectralDensity

    @property
    def kicID(self):
        """
        Property for the KicID of the star
        :return: Returns the KicID of the star
        :rtype: string
        """
        return self._kicID

    @property
    def nuMax(self):
        """
        Property for nuMax. Accessed through the _getSummaryParameter method, which accesses the _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        """
        return self._getSummaryParameter(strPriorNuMax)

    @property
    def oscillationAmplitude(self):
        """
        Property for power of osc. Accessed through the _getSummaryParameter method, which accesses the _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        """
        return self._getSummaryParameter(strPriorHeight)

    @property
    def sigma(self):
        """
        Property for the standard deviation of the powerexcess. Accessed through the _getSummaryParameter method, which
        accesses the _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        """
        return self._getSummaryParameter(strPriorSigma)

    @property
    def firstHarveyFrequency(self):
        """
        Property for first Harvey frequency. Accessed through the _getSummaryParameter method, which accesses the
        _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        """
        return self._getSummaryParameter(strPriorFreqHarvey1)

    @property
    def secondHarveyFrequency(self):
        """
        Property for second Harvey frequency. Accessed through the _getSummaryParameter method, which accesses the
        _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        """
        return self._getSummaryParameter(strPriorFreqHarvey2)

    @property
    def thirdHarveyFrequency(self):
        """
        Property for third Harvey frequency. Accessed through the _getSummaryParameter method, which accesses the
        _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        """
        return self._getSummaryParameter(strPriorFreqHarvey3)

    @property
    def firstHarveyAmplitude(self):
        """
        Property for first Harvey amplitude. Accessed through the _getSummaryParameter method, which accesses the
        _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        """
        return self._getSummaryParameter(strPriorAmpHarvey1)

    @property
    def secondHarveyAmplitude(self):
        """
        Property for second Harvey amplitude. Accessed through the _getSummaryParameter method, which accesses the
        _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        """
        return self._getSummaryParameter(strPriorAmpHarvey2)

    @property
    def thirdHarveyAmplitude(self):
        """
        Property for third Harvey amplitude. Accessed through the _getSummaryParameter method, which accesses the
        _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        """
        return self._getSummaryParameter(strPriorAmpHarvey3)

    @property
    def backgroundNoise(self):
        """
        Property for the background noise. Accessed through the _getSummaryParameter method, which accesses the
        _summary object
        :return: The value for nuMax as computed by DIAMONDS.
        :rtype: ufloat
        """
        return self._getSummaryParameter(strPriorFlatNoise)

    @property
    def psdOnlyFlag(self):
        """
        Property for the psdOnlyFlag. If BackgroundParameter is not set, this will return true. Otherwise this flag
        will be False.
        :return:
        :rtype:
        """
        return self._psdOnlyFlag

    @psdOnlyFlag.setter
    def psdOnlyFlag(self,value):
        """
        Setter property for the psdOnlyFlag
        :param value: Value for the flag
        :type value: bool
        """
        self._psdOnlyFlag = value

    @property
    def radiusStar(self):
        """
        Property for the radiusStar. Is calculated using the calculateRadius() method
        :return:Radius of the star in solar radii
        :rtype:ufloat
        """
        return self._radiusStar

    @radiusStar.setter
    def radiusStar(self,value):
        """
        Setter property for the radiusStar.
        :param value: The value for the radius in solar radii
        :type value: ufloat
        """
        self._radiusStar = value

    @property
    def bolometricCorrection(self):
        """
        Bolometric Correction of the star. Computed using the BCCalculator
        :return: Bolometric Correction ini mag
        :rtype: float
        """
        return self._bolometricCorrection

    @bolometricCorrection.setter
    def bolometricCorrection(self,value):
        """
        Setter property for the Bolometric Correction of the star
        :param value: Bolometric Correction value in mag
        :type value:float
        """
        self._bolometricCorrection = value

    @property
    def luminosity(self):
        """
        Property for the luminosity of the star. Calculated using calculateLuminosity()
        :return:Luminosity of the star in Wattt
        :rtype:ufloat
        """
        return self._luminosity

    @luminosity.setter
    def luminosity(self,value):
        """
        Setter Property of the luminosity.
        :param value:Luminosity in Watt
        :type value:ufloat
        """
        self._luminosity = value

    @property
    def distanceModulus(self):
        """
        Property of the distance Modulus for the star. Calculated using the calculateDistanceModulus()
        :return: Distance Modulus in mag
        :rtype: ufloat
        """
        return self._distanceModulus

    @distanceModulus.setter
    def distanceModulus(self,value):
        """
        Property setter of the distance modulus
        :param value: Distance modulus in mag
        :type value: ufloat
        """
        self._distanceModulus = value

    @property
    def kicDistanceModulus(self):
        """
        Property for the KIC Distance modulus in mag. Computed using the KIC teff. Legacy
        :return: KIC Distance modulus
        :rtype: ufloat
        """
        return self._kicDistanceModulus

    @kicDistanceModulus.setter
    def kicDistanceModulus(self,value):
        """
        Property setter for the KIC Distance modulus in mag.
        :param value: KIC Distance modulus
        :type value:ufloat
        """
        self._kicDistanceModulus = value

    @property
    def robustnessValue(self):
        """
        Robustness Value, computes the difference between KIC distance modulus and distance modulus. Legacy
        :return: Robustness Value in mag
        :rtype: ufloat
        """
        return abs(self.distanceModulus[0] - self.kicDistanceModulus) * 100 / self.distanceModulus[0]

    @property
    def robustnessSigma(self):
        """
        Sigma of the robustness value
        :return: sigma
        :rtype: ufloat
        """
        return abs(self.distanceModulus[0] - self.kicDistanceModulus) / self.distanceModulus[1]

    @property
    def deltaNuCalculator(self):
        """
        Returns the deltaNuCalculator
        :return: DeltaNuCalculator
        :rtype: DeltaNuCalculator
        """
        return self._deltaNuCalculator

    @deltaNuCalculator.setter
    def deltaNuCalculator(self,value):
        """
        Setter for the deltaNuCalculator property
        :param value: Instance of the DeltaNuCalculator
        :type value: DeltaNuCalculator
        """
        self._deltaNuCalculator = value

    def _getSummaryParameter(self,key):
        """
        Returns the SummaryParameter, i.e. the value computed by DIAMONDS. Can be a single Parameter or a full dict
        if key is None
        :param key: Key for the dict -> see strings.py
        :type key: string
        :return: Single Parameter or full dict
        :rtype: dict/ufloat
        """
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
        """
        Computes delta nu using the deltaNuCalculator
        """
        backgroundModel = self.createBackgroundModel((self._runID is strDiamondsModeFull))
        backGroundData = np.vstack((self.summary.getRawData(strSummaryMedian),
                                    self.summary.getRawData(strSummaryLowCredLim),
                                    self.summary.getRawData(strSummaryUpCredLim)))

        self.deltaNuCalculator = DeltaNuCalculator(self.nuMax[0], self.sigma[0],
                                                    self._dataFile.powerSpectralDensity,
                                                    self._nyq, backGroundData, backgroundModel)

    def createBackgroundModel(self, runGauss):
        """
        Creates a full Background model
        :param runGauss: Parameter used as an indicator if this is a fullBackground or noiseOnly model
        :type runGauss: bool
        :return: Background Model
        """
        freq, psd = self._dataFile.powerSpectralDensity
        par_median = self.summary.getRawData(strSummaryMedian)  # median values

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
        if runGauss and self._runID is strDiamondsModeFull:
            retVal =zeta * h_long * r, zeta * h_gran1 * r, zeta * h_gran2 * r, w, g * r
        else:
            retVal =  zeta * h_long * r, zeta * h_gran1 * r, zeta * h_gran2 * r, w

        return retVal


    def getMarginalDistribution(self, key = None):
        """
        Returns single MarginalDistributions or full MarginalDistributions. Contains the MarginalDistributions class
        :param key: key for the dict
        :type key: string
        :rtype:dict/MarginalDistribution
        """
        if key is None:
            return self._marginalDistributions
        else:
            for i in self._marginalDistributions:
                if i.name == key:
                    return self._marginalDistributions[i]

            self.logger.debug("Found no marginal Distribution for '"+key+"'")
            self.logger.debug("Returning full list")
            return self._marginalDistributions

    def calculateRadius(self, tSun, nuMaxSun, deltaNuSun):
        """
        Legacy
        """
        if self._tEff is None:
            self.logger.debug("Teff is None, no calculation of BC takes place")
            return None

        if self.nuMax is None:
            self.logger.debug("NuMax is not calculated, need nuMax to proceed")
            return None

        if self.deltaNuCalculator is None:
            self.logger.debug("Delta Nu is not yet calculated, need to calculate that first")
            self.calculateDeltaNu()

        self.radiusStar = (self.deltaNuCalculator.deltaNu / deltaNuSun) ** -2 * (self.nuMax / nuMaxSun) * \
                          sqrt(self._tEff / tSun)


    def calculateLuminosity(self, tSun):
        """
        Legacy
        """
        if self._tEff is None:
            self.logger.debug("Teff is None, no calculation of Luminosity takes place")
            return None

        if self.radiusStar is None:
            self.logger.debug("Radius not yet calculated, need to calculate that first")
            self.calculateRadius()

        self.luminosity = self.radiusStar ** 2 * (self._tEff / tSun) ** 4

    def calculateDistanceModulus(self, appMag, kicmag, av, nuMaxSun, deltaNuSun, tSun):
        """
        Legacy
        """
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

        self.distanceModulus = (6 * log10(self.nuMax / nuMaxSun) + 15 * log10(self._tEff / tSun) - 12 * log10(self.deltaNuCalculator.deltaNu / deltaNuSun) \
                                + 1.2 * (appMag + self.bolometricCorrection) - 1.2 * av - 5.7) / 1.2

        self.kicDistanceModulus = (6 * log10(self.nuMax / nuMaxSun) + 15 * log10(self._tEff / tSun) - 12 * log10(self.deltaNuCalculator.deltaNu / deltaNuSun) \
                                   + 1.2 * (kicmag + self.bolometricCorrection) - 1.2 * av - 5.7) / 1.2

        self.mu_diff = self.distanceModulus - self.kicDistanceModulus
