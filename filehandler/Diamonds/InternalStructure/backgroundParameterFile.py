import logging

import numpy as np

from settings.settings import Settings
from support.strings import *
from filehandler.Diamonds.InternalStructure.backgroundAbstractFile import BaseBackgroundFile


class BackgroundParameter(BaseBackgroundFile):

    def __init__(self, name, unit, kicID=None, runID = 00, id = None):
        '''
        Constructs an object containing the content of one backgroundparameter file. Needs
        to be called for every single parameter in DIAMONDS (i.e. 6 or 9 times)
        :param name: The name of the parameter, i.e. H
        :type name:string
        :param unit: The unit contained in the values, i.e. uHz
        :type unit:string
        :param kicID: the KicID of the Star
        :type kicID:string
        :param runID: The RunID used by Diamonds (subfolder in results file)!
        :type runID:string
        :param id: Id used between 0 and 9 (last three digits of Filename)
        :type id:int
        '''
        BaseBackgroundFile.__init__(self,kicID,runID)
        self.logger = logging.getLogger(__name__)
        self._id = id
        self._name = name
        self._unit = unit
        self._dataFolder = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundResPath).value

        if (kicID is not None and runID is not None and id is not None):
            self._readData()

    @property
    def name(self):
        """
        :return: Name of the parameter
        :rtype:string
        """
        return self._name

    @property
    def unit(self):
        """
        :return:Unit of the parameter
        :rtype: string
        """
        return self._unit

    def getData(self,reReaddata = False):
        '''
        :return: The Dataset.
        :type: 1-D numpy array
        '''
        if self._parameters is None:
            self._readData()

        return self._parameters

    def _readData(self):
        """
        Reads the dataset from the parameterfiled created by DIAMONDS.
        """

        file = self._dataFolder + 'KIC' + self.kicID + "/" + self.runID + "/background_parameter_00" + str(
            self._id) + ".txt"
        self._parameters = np.loadtxt(file).T

