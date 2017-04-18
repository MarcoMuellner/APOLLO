from settings.settings import Settings
import numpy as np
import glob
from support.strings import *

class Priors:

    m_kicID = None
    m_runId = None
    m_dataFolder = None
    m_priors = {}

    def __init__(self,kicID = None,runID = None):
        self.m_kicID = kicID
        self.m_runId = runID

        if(kicID is not None):
            self.__readData()

    def setKICID(self,kicId):
        '''
        Sets the KicID and rereads data
        :param kicId: KicID of the star
        :return: returns Data. See getData()
        '''
        self.m_kicID = kicId
        self.__readData()
        return self.getData()

    def setRunID(self,runId):
        '''
        Sets the RunID and rereads data
        :param runId: runId of the Diamonds run (subfolder in results file)!
        :return: returns Data. See getData()
        '''
        self.m_runId = runId
        self.__readData()
        return self.getData()

    def setParameters(self,kicId,runId):
        self.setKICID(kicId)
        self.setRunID(runId)
        return self.getData()

    def getData(self,key=None):
        if any(self.m_priors) is False:
            self.__readData()

        if key is None:
            return self.m_priors
        else:
            try:
                return self.m_priors[key]
            except:
                print("No value for key '"+key+"', returning full dict")
                return self.m_priors

    def __readData(self):
        try:
            self.m_dataFolder = Settings.Instance().getSetting(strDataSettings,
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
            self.m_priors[strPriorHeight] = (values[0][7], values[1][7])
            self.m_priors[strPriorNuMax] = (values[0][8], values[1][8])
            self.m_priors[strPriorSigma] = (values[0][9], values[1][9])
        except:
            print("Failed to open File '" + glob.glob(self.m_dataFolder +
                    'KIC{}/{}/background_evidenceInformation.txt'.format(self.m_kicID, self.m_runId))[0] + "'")
            print("Setting Data to None")
            self.m_priors = {}

