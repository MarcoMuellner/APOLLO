import glob
import logging

import numpy as np

from background.fileModels.backgroundBaseFileModel import BackgroundBaseFileModel
from res.strings import *
from settings.settings import Settings


class BackgroundMarginalDistrFileModel(BackgroundBaseFileModel):

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
        BackgroundBaseFileModel.__init__(self, kickId, runID)
        self.logger = logging.getLogger(__name__)
        self._id = id
        self._name = name
        self._unit = unit
        self.dataFolder = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundResPath).value
        if (kickId is not None and runID is not None and id is not None):
            self._readData()
        return


    @property
    def id(self):
        '''
        ID of the marginal distribution (between 0 and 9)
        :return: ID
        :rtype: int
        '''
        return self._id

    @id.setter
    def id(self,value):
        '''
        Sets the ID and rereads the data
        :param value: ID
        :type value: int
        '''
        if value is None:
            self._id = ""
        else:
            self._id = value
        if self.kicID not in ["",None] and self.runID not in ["",None] and self._id not in ["",None]:
            self._readData()

    @property
    def name(self):
        '''
        Name of the marginal distribution, set in Constructor
        :return: Name
        :rtype: string
        '''
        return self._name

    @property
    def unit(self):
        '''
        Unit of the marginal distribution, set in Constructor
        :return: Unit
        :rtype: string
        '''
        return self._unit

    def getData(self):
        '''
        :return: The Dataset. Single numpy array
        '''
        if self._data is None:
            self._readData()

        return self._data

    @property
    def backgroundData(self):
        '''
        BackgroundData for a Dataset, set via setter property
        :return: BackgroundData
        :rtype: 1-D numpy array
        '''
        return self._backgroundData

    @backgroundData.setter
    def backgroundData(self,value):
        '''
        Setter method for the backgroundData
        :param value:BackgroundData for one Dataset
        :type value: 1-D numpy array
        '''
        self._backgroundData = value

    def createMarginalDistribution(self):
        '''
        Calculates necessary values for plotting the Marginal distribution
        :return: Values needed for plotting the Marginal distribution
        :rtype: 5-D tuple
        '''
        if self._backgroundData is None:
            self.logger.error("BackgroundData is not set, returning")
            raise ValueError("BackgroundData is not set, returning")

        par_median, par_le, par_ue = self._backgroundData
        par, marg = self._data

        par_err_le = par_median - par_le
        par_err_ue = par_ue - par_median
        par_err = (par_err_le ** 2 + par_err_ue ** 2) ** (0.5) / 2 ** (0.5)

        fill_x = par[(par >= par_le) & (par <= par_ue)]
        fill_y = marg[(par >= par_le) & (par <= par_ue)]

        return (par,marg,fill_x,fill_y,par_err)

    def _readData(self):
        '''
        Reads the Data. Should be only used internally
        '''
        file = self.dataFolder + "KIC" + self.kicID + "/" + self.runID + "/" + "background_marginalDistribution00"+\
               str(self.id)+".txt"
        self._data = self._readFile(file)
