import glob
import numpy as np
from settings.settings import Settings
from support.strings import *

class BackgroundParameter:
    m_kicID = None
    m_runId = None
    m_dataFolder = None
    m_id = None
    m_parameters = None
    m_name = None
    m_unit = None


    def __init__(self,name, unit, kickId=None,runID = 00,id = None):
        '''
        Constructs an object containing the content of one backgroundparameter file.
        :param name: The name of the parameter, i.e. H
        :param unit: The unit contained in the values, i.e. uHz
        :param kickId: the KicID of the Star
        :param runID: The RunID used by Diamonds (subfolder in results file)!
        :param id: Id used between 0 and 9 (last three digits of Filename)
        '''
        self.m_kicID = kickId
        self.m_runId = runID
        self.m_id = id
        self.m_name = name
        self.m_unit = unit
        if (kickId is not None and runID is not None and id is not None):
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

    def setID(self,id):
        '''
        Sets the Id of the filename and rereads data
        :param id: The id of the file, last three digits of filename
        :return: returns Data. See getData()
        '''
        self.m_id = id
        self.__readData()
        return self.getData()

    def getName(self):
        '''
        :return: The Name of the object
        '''
        return self.m_name

    def getUnit(self):
        '''
        :return: The Unit of the object
        '''
        return self.m_unit

    def setParameters(self,kicId,runId,id):
        '''
        Convinience function for setting all parameters at once
        '''
        self.setKICID(kicId)
        self.setRunID(runId)
        self.setID(id)
        return self.getData()

    def getData(self):
        '''
        :return: The Dataset. Single numpy array
        '''
        if self.m_parameters is None:
            self.__readData()

        return self.m_parameters

    def __readData(self):
        '''
        Reads the Data. Should be only used internally
        '''
        self.m_dataFolder = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundResPath).value
        try:
            mpFile = glob.glob(self.m_dataFolder+'KIC{}/{}/background_parameter*{}.txt'
                               .format(self.m_kicID, self.m_runId, '00'+str(self.m_id)))[0]
            self.m_parameters = np.loadtxt(mpFile).T
        except:
            print("Failed to open File '"+self.m_dataFolder+'KIC*{}*/{}/background_parameter*{}.txt'
                               .format(self.m_kicID, self.m_runId, '00'+str(self.m_id))+"'")
            print("Setting Data to None")
            self.m_parameters = None

