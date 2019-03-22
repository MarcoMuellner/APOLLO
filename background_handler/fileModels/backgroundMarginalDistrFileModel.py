import glob
import logging

import numpy as np

from background.fileModels.backgroundBaseFileModel import BackgroundBaseFileModel
from res.strings import *
from res.conf_file_str import general_background_result_path,general_kic
from support.printer import print_int


class BackgroundMarginalDistrFileModel(BackgroundBaseFileModel):

    def __init__(self,name, unit, kwargs,runID = 00,id = None):
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
        BackgroundBaseFileModel.__init__(self, kwargs, runID)
        self.logger = logging.getLogger(__name__)
        self._id = id
        self._name = name
        self._unit = unit
        self.kwargs = kwargs
        self.dataFolder = kwargs[general_background_result_path]
        if (runID is not None and id is not None):
            self._readData(kwargs)
        return

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
            self._readData(self.kwargs)

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

        par, marg = self._data
        try:
            par_median, par_le, par_ue = self._backgroundData

            par_err_le = par_median - par_le
            par_err_ue = par_ue - par_median
            par_err = (par_err_le ** 2 + par_err_ue ** 2) ** (0.5) / 2 ** (0.5)

            fill_x = par[(par >= par_le) & (par <= par_ue)]
            fill_y = marg[(par >= par_le) & (par <= par_ue)]
        except:
            fill_x = None
            fill_y = None
            par_err = None
            par_median = None

        return (par,marg,fill_x,fill_y,par_err,par_median)

    def _readData(self,kwargs):
        '''
        Reads the Data. Should be only used internally
        '''
        file = self.dataFolder + "KIC" + self.kicID + "/" + self.runID + "/" + "background_marginalDistribution00"+\
               str(self.id)+".txt"
        self._data = self._readFile(file)
