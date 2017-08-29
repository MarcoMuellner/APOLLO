import glob
import numpy as np
from settings.settings import Settings
from support.strings import *
import logging

class MarginalDistribution:

    def __init__(self,name, unit, kickId=None,runID = 00,id = None):
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
        if (kickId is not None and runID is not None and id is not None):
            self.__readData()
        return

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
        if self.m_data is None:
            self.__readData()

        return self.m_data

    def setBackgroundParameters(self,backgroundData):
        self.m_backgroundData = backgroundData

    def createMarginalDistribution(self):
        if self.m_backgroundData is None:
            self.logger.warning("BackgroundData is not set, returning")
            return

        par_median, par_le, par_ue = self.m_backgroundData
        par, marg = self.m_data

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
        self.m_dataFolder = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundResPath).value
        try:
            mpFile = glob.glob(self.m_dataFolder+'KIC{}/{}/background_marginalDistribution{}.txt'
                               .format(self.m_kicID, self.m_runId, '00'+str(self.m_id)))[0]
            self.m_data = np.loadtxt(mpFile).T
        except:
            self.logger.warning("Failed to open File '"+self.m_dataFolder+'KIC{}/{}/background_marginalDistribution{}.txt'
                               .format(self.m_kicID, self.m_runId, '00'+str(self.m_id))+"'")
            self.logger.warning("Setting Data to None")
            self.m_data = None
