from settings.settings import Settings
import numpy as np
import glob
from support.strings import *
import logging

class PriorSetup:
    """
    This class represents the priors that are used to fit the data with DIAMONDS. You need two kinds of these,
    one for the fullBackground model, one for the noiseOnly model. These are calculated using the PriorCalculator
    """

    def __init__(self,kicID = None,runID = None):
        """
        Constructor for the PriorSetup class.
        :param kicID: KICID of the star
        :type kicID: string
        :param runID: Represents the Run -> i.e. fullBackground or noiseOnly
        :type runID: string
        """
        self.m_kicID = None
        self.m_runId = None

        self.m_priors = {}
        self.logger = logging.getLogger(__name__)
        self.kicID = kicID
        self.runID = runID

    @property
    def kicID(self):
        """
        Property for the KICID of the star
        :return: KICID of the star
        :rtype: string
        """
        return self.m_kicID

    @kicID.setter
    def kicID(self,value):
        """
        Property setter for the KICID
        :param value:
        :type value:
        :return:
        :rtype:
        """
        self.m_kicID = value
        if self.m_kicID is not None and self.m_runId is not None:
            self.__readData()

    @property
    def runID(self):
        return self.m_runId

    @runID.setter
    def runID(self,value):
        self.m_runId = value
        if self.m_kicID is not None and self.m_runId is not None:
            self.__readData()

    def getData(self,key=None):
        if any(self.m_priors) is False:
            self.__readData()

        if key is None:
            return self.m_priors
        else:
            try:
                return self.m_priors[key]
            except:
                self.logger.warning("No value for key '"+key+"', returning full dict")
                return self.m_priors

    def __readData(self):
        try:
            self.m_dataFolder = Settings.Instance().getSetting(strDiamondsSettings,
                                                               strSectBackgroundResPath).value
            mpFile = None
            if self.m_runId is not None:
                mpFile = glob.glob(self.m_dataFolder + 'KIC{}/{}/background_hyperParametersUniform.txt'
                                   .format(self.m_kicID, self.m_runId))[0]
            else:
                mpFile = glob.glob(self.m_dataFolder + 'KIC{}/background_hyperParameters.txt'
                                   .format(self.m_kicID))[0]
            values = np.loadtxt(mpFile).T

            self.m_priors[strPriorFlatNoise] = (values[0][0], values[1][0])
            self.m_priors[strPriorAmpHarvey1] = (values[0][1], values[1][1])
            self.m_priors[strPriorFreqHarvey1] = (values[0][2], values[1][2])
            self.m_priors[strPriorAmpHarvey2] = (values[0][3], values[1][3])
            self.m_priors[strPriorFreqHarvey2] = (values[0][4], values[1][4])
            self.m_priors[strPriorAmpHarvey3] = (values[0][5], values[1][5])
            self.m_priors[strPriorFreqHarvey3] = (values[0][6], values[1][6])
            if len(values[0])>7:
                self.m_priors[strPriorHeight] = (values[0][7], values[1][7])
                self.m_priors[strPriorNuMax] = (values[0][8], values[1][8])
                self.m_priors[strPriorSigma] = (values[0][9], values[1][9])
        except Exception as e:
            self.logger.warning("Failed to open Priors '" + self.m_dataFolder)
            self.logger.warning(e)
            self.logger.warning("Setting Data to None")
            self.m_priors = {}
