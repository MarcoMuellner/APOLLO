import glob
import numpy as np
from settings.settings import Settings
from support.strings import *
import logging

class BackgroundParameter:

    def __init__(self,name, unit, kickId=None,runID = 00,id = None,readData = True,readLiveData = True):
        '''
        Constructs an object containing the content of one backgroundparameter file.
        :param name: The name of the parameter, i.e. H
        :param unit: The unit contained in the values, i.e. uHz
        :param kickId: the KicID of the Star
        :param runID: The RunID used by Diamonds (subfolder in results file)!
        :param id: Id used between 0 and 9 (last three digits of Filename)
        '''
        self.logger = logging.getLogger(__name__)
        self.m_kicID = kickId
        self.m_runId = runID
        self.m_id = id
        self.m_name = name
        self.m_unit = unit
        self.m_dataFolder = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundResPath).value

#        if readLiveData == True:
#            self.__deleteFile("_live")

        if (kickId is not None and runID is not None and id is not None):
            self.__readData(readData,readLiveData)

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

    def getLiveData(self,reReadData = True):
        '''
        :return: Live Data set. Single numpy array
        '''

        if self.m_liveParameters is None or reReadData == True:
            self.__readData(readParameters=False, readLiveParameters=True)

        return self.m_liveParameters



    def getData(self,reReaddata = False):
        '''
        :return: The Dataset. Single numpy array
        '''
        if self.m_parameters is None or reReaddata == True:
            self.__readData(readParameters=True,readLiveParameters=False)

        return self.m_parameters

    def __readData(self,readParameters = True,readLiveParameters = True):
        '''
        Reads the Data. Should be only used internally
        '''
        if readParameters == True:
            self.m_parameters = self.__readInternalData()

        if readLiveParameters == True:
            self.m_liveParameters = self.__readInternalData("_live")

    def __readInternalData(self,appendix = ""):
        file = self.m_dataFolder + 'KIC' + self.m_kicID + "/" + self.m_runId + "/background_parameter" + appendix + "00" + str(
            self.m_id)+".txt"
        try:
            return np.loadtxt(file).T
        except:
            self.logger.warning("Failed to open File '"+file+"'")
            self.logger.warning("Setting Data to None")
            return None

    def __deleteFile(self,appendix):
        file = self.m_dataFolder + 'KIC' + self.m_kicID + "/" + self.m_runId + "/background_parameter" + appendix + "00" + str(
            self.m_id) + ".txt"
        try:
            os.remove(file)
        except OSError:
            self.logger.debug("File "+file+" doesnt exist")

