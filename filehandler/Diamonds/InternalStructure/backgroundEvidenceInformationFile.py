from settings.settings import Settings
import numpy as np
import glob


class Evidence:
    m_kicID = None
    m_runId = None
    m_dataFolder = None
    m_evidence = {}

    def __init__(self,kicID = None,runID = None):
        self.m_kicID = kicID
        self.m_runId = runID

        if(kicID is not None and runID is not None):
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
        return self.getData()

    def setParameters(self,kicId,runId):
        self.setKICID(kicId)
        self.setRunID(runId)
        return self.getData()

    def getData(self,key=None):
        if any(self.m_evidence) is False:
            self.__readData()

        if key is None:
            return self.m_evidence
        else:
            try:
                return self.m_evidence[key]
            except:
                print("No value for key '"+key+"', returning full dict")
                return self.m_evidence

    def __readData(self):
        try:
            self.m_dataFolder = Settings.Instance().getSetting("Files",
                                                               "dataFolder")  # todo change this to strings in strings
            mpFile = glob.glob(self.m_dataFolder + 'KIC*{}*/{}/background_evidenceInformation.txt'
                               .format(self.m_KicID, self.m_runId))[0]
            values = np.loadtxt(mpFile).T
            self.m_evidence["Skilling's log(Evidence)"] = values[0] #todo replace with string
            self.m_evidence["Skilling's Error log(Evidence)"] = values[1] #todo replace with string
            self.m_evidence["Skilling's Information Gain"] = values[2] #todo replace with string
        except:
            print("Failed to open File '" + glob.glob(self.m_dataFolder +
                    'KIC*{}*/{}/background_evidenceInformation.txt'.format(self.m_KicID, self.m_runId))[0] + "'")
            print("Setting Data to None")
            self.m_evidence = {}
