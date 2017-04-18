from settings.settings import Settings
import numpy as np
import glob

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
            self.m_dataFolder = Settings.Instance().getSetting("Files",
                                                               "dataFolder")  # todo change this to strings in strings
            mpFile = None
            if self.m_runId is not None:
                mpFile = glob.glob(self.m_dataFolder + 'KIC*{}*/{}/background_hyperParametersUniform.txt'
                                   .format(self.m_KicID, self.m_runId))[0]
            else:
                mpFile = glob.glob(self.m_dataFolder + 'KIC*{}*/background_hyperParameters.txt'
                                   .format(self.m_KicID))[0]
            values = np.loadtxt(mpFile).T
            self.m_priors["Flatnoiselevel"] = (values[0][0], values[0][1]) #todo replace with string
            self.m_priors["AmplitudeHarvey1"] = (values[1][0], values[1][1])  # todo replace with string
            self.m_priors["FrequencyHarvey1"] = (values[2][0], values[2][1])  # todo replace with string
            self.m_priors["AmplitudeHarvey2"] = (values[3][0], values[3][1])  # todo replace with string
            self.m_priors["FrequencyHarvey2"] = (values[4][0], values[4][1])  # todo replace with string
            self.m_priors["AmplitudeHarvey3"] = (values[5][0], values[5][1])  # todo replace with string
            self.m_priors["FrequencyHarvey3"] = (values[6][0], values[6][1])  # todo replace with string
            self.m_priors["HeightOscillation"] = (values[7][0], values[7][1])  # todo replace with string
            self.m_priors["NuMax"] = (values[8][0], values[8][1])  # todo replace with string
            self.m_priors["Sigma"] = (values[9][0], values[9][1])  # todo replace with string
        except:
            print("Failed to open File '" + glob.glob(self.m_dataFolder +
                    'KIC*{}*/{}/background_evidenceInformation.txt'.format(self.m_KicID, self.m_runId))[0] + "'")
            print("Setting Data to None")
            self.m_priors = {}

