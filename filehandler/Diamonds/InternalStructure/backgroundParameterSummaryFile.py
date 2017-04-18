from settings.settings import Settings
import numpy as np
import glob

class ParameterSummary:
    m_kicID = None
    m_runId = None
    m_dataFolder = None
    m_id = None
    m_data = None
    m_name = None
    m_unit = None
    m_values = {}

    def __init__(self,kicID=None,runID=None):
        self.m_kicID  = kicID
        self.m_runId = runID
        if(kicID is not None and runID is not None):
            self.__readData()
        return

    def setKICID(self, kicId):
        '''
        Sets the KicID and rereads data
        :param kicId: KicID of the star
        :return: returns Data. See getData()
        '''
        self.m_kicID = kicId
        self.__readData()
        return self.getData()

    def setRunID(self, runId):
        '''
        Sets the RunID and rereads data
        :param runId: runId of the Diamonds run (subfolder in results file)!
        :return: returns Data. See getData()
        '''
        self.m_runId = runId
        self.__readData()
        return self.getData()

    def setParameters(self, kicId, runId):
        self.setKICID(kicId)
        self.setRunID(runId)
        return self.getData()


    def getData(self, key=None):
        if any(self.m_values) is False:
            self.__readData()

        if key is None:
            return self.m_data
        else:
            try:
                return self.m_data[key]
            except:
                print("No value for key '" + key + "', returning full dict")
                return self.m_data

    def __readData(self):
        try:
            self.m_dataFolder = Settings.Instance().getSetting("Files",
                                                               "dataFolder")  # todo change this to strings in strings
            mpFile = glob.glob(self.m_dataFolder + 'KIC*{}*/{}/background_parameterSummary.txt'
                               .format(self.m_KicID, self.m_runId))[0]
            values = np.loadtxt(mpFile).T
            self.m_values["I Moment (Mean)"] = values[0] #todo replace with string
            self.m_values["Median"] = values[1] #todo replace with string
            self.m_values["Mode"] = values[2] #todo replace with string
            self.m_values["II Moment (Variance if Normal distribution)"] = values[3]  # todo replace with string
            self.m_values["Lower Credible Limit"] = values[4]  # todo replace with string
            self.m_values["Upper Credible Limit"] = values[5]  # todo replace with string
            self.m_values["Skewness"] = values[6]  # todo replace with string
        except:
            print("Failed to open File '" + glob.glob(self.m_dataFolder +
                    'KIC*{}*/{}/background_parameterSummary.txt'.format(self.m_KicID, self.m_runId))[0] + "'")
            print("Setting Data to None")
            self.m_values = {}