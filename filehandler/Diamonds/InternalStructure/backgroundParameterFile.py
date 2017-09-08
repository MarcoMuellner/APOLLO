import logging

import numpy as np

from settings.settings import Settings
from support.strings import *
from filehandler.Diamonds.InternalStructure.backgroundAbstractFile import BaseBackgroundFile


class BackgroundParameter(BaseBackgroundFile):

    def __init__(self, name, unit, kicID=None, runID = 00, id = None, readData = True, readLiveData = True):
        '''
        Constructs an object containing the content of one backgroundparameter file.
        :param name: The name of the parameter, i.e. H
        :param unit: The unit contained in the values, i.e. uHz
        :param kicID: the KicID of the Star
        :param runID: The RunID used by Diamonds (subfolder in results file)!
        :param id: Id used between 0 and 9 (last three digits of Filename)
        '''
        BaseBackgroundFile.__init__(self,kicID,runID)
        self.logger = logging.getLogger(__name__)
        self._id = id
        self._name = name
        self._unit = unit
        self._dataFolder = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundResPath).value

#        if readLiveData == True:
#            self.__deleteFile("_live")

        if (kicID is not None and runID is not None and id is not None):
            self.__readData(readData,readLiveData)

    def setID(self,id):
        '''
        Sets the Id of the filename and rereads data
        :param id: The id of the file, last three digits of filename
        :return: returns Data. See getData()
        '''
        self._id = id
        self.__readData()
        return self.getData()

    def getName(self):
        '''
        :return: The Name of the object
        '''
        return self._name

    def getUnit(self):
        '''
        :return: The Unit of the object
        '''
        return self._unit

    def getLiveData(self,reReadData = True):
        '''
        :return: Live Data set. Single numpy array
        '''

        if self._liveParameters is None or reReadData == True:
            self.__readData(readParameters=False, readLiveParameters=True)

        return self._liveParameters

    def getData(self,reReaddata = False):
        '''
        :return: The Dataset. Single numpy array
        '''
        if self._parameters is None or reReaddata == True:
            self.__readData(readParameters=True,readLiveParameters=False)

        return self._parameters

    def __readData(self,readParameters = True,readLiveParameters = True):
        '''
        Reads the Data. Should be only used internally
        '''
        if readParameters == True:
            self._parameters = self.__readInternalData()

        if readLiveParameters == True:
            self._liveParameters = self.__readInternalData("_live")

    def __readInternalData(self,appendix = ""):
        file = self._dataFolder + 'KIC' + self.kicID + "/" + self.runID + "/background_parameter" + appendix + "00" + str(
            self._id)+".txt"
        try:
            return np.loadtxt(file).T
        except:
            self.logger.warning("Failed to open File '"+file+"'")
            self.logger.warning("Setting Data to None")
            return None

    def __deleteFile(self,appendix):
        file = self._dataFolder + 'KIC' + self._kicID + "/" + self._runId + "/background_parameter" + appendix + "00" + str(
            self._id) + ".txt"
        try:
            os.remove(file)
        except OSError:
            self.logger.debug("File "+file+" doesnt exist")

