import glob
import logging

import numpy as np

from settings.settings import Settings
from support.strings import *
from filehandler.Diamonds.InternalStructure.backgroundAbstractFile import BaseBackgroundFile


class MarginalDistribution(BaseBackgroundFile):

    def __init__(self,name, unit, kickId=None,runID = 00,id = None):
        '''
        Constructs an object containing the content of one backgroundparameter file.
        :param name: The name of the parameter, i.e. H
        :type name:string
        :param unit: The unit contained in the values, i.e. uHz
        :type unit:string
        :param kickId: the KicID of the Star
        :type kickId: string
        :param runID: The RunID used by Diamonds (subfolder in results file)!
        :type runID: string
        :param id: Id used between 0 and 9 (last three digits of Filename)
        :type id: int
        '''
        BaseBackgroundFile.__init__(self,kickId,runID)
        self.logger = logging.getLogger(__name__)
        self._id = id
        self._name = name
        self._unit = unit
        if (kickId is not None and runID is not None and id is not None):
            self.__readData()
        return

    def setKICID(self,kicId):
        '''
        Sets the KicID and rereads data
        :param kicId: KicID of the star
        :return: returns Data. See getData()
        '''
        self.kicID = kicId
        self.__readData()
        return self.getData()

    def setRunID(self,runId):
        '''
        Sets the RunID and rereads data
        :param runId: runId of the Diamonds run (subfolder in results file)!
        :return: returns Data. See getData()
        '''
        self.runID = runId
        self.__readData()
        return self.getData()

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

    def getData(self):
        '''
        :return: The Dataset. Single numpy array
        '''
        if self._data is None:
            self.__readData()

        return self._data

    def setBackgroundParameters(self,backgroundData):
        self._backgroundData = backgroundData

    def createMarginalDistribution(self):
        if self._backgroundData is None:
            self.logger.warning("BackgroundData is not set, returning")
            return

        par_median, par_le, par_ue = self._backgroundData
        par, marg = self._data

        par_err_le = par_median - par_le
        par_err_ue = par_ue - par_median
        par_err = (par_err_le ** 2 + par_err_ue ** 2) ** (0.5) / 2 ** (0.5)

        fill_x = par[(par >= par_le) & (par <= par_ue)]
        fill_y = marg[(par >= par_le) & (par <= par_ue)]

        return (par,marg,fill_x,fill_y,par_err)

    def __readData(self):
        '''
        Reads the Data. Should be only used internally
        '''
        self._dataFolder = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundResPath).value
        try:
            mpFile = glob.glob(self._dataFolder+'KIC{}/{}/background_marginalDistribution{}.txt'
                               .format(self.kicID, self.runID, '00'+str(self._id)))[0]
            self._data = np.loadtxt(mpFile).T
        except:
            self.logger.warning("Failed to open File '"+self._dataFolder+'KIC{}/{}/background_marginalDistribution{}.txt'
                               .format(self.kicID, self.runID, '00'+str(self._id))+"'")
            self.logger.warning("Setting Data to None")
            self._data = None
