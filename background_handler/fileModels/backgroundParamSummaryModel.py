import glob
import logging

import numpy as np
from uncertainties import ufloat

from background_handler.fileModels.backgroundBaseFileModel import BackgroundBaseFileModel
from res.strings import *
from res.conf_file_str import general_background_result_path,internal_path
from support.printer import print_int


class BackgroundParamSummaryModel(BackgroundBaseFileModel):
    '''
    This class represents the summary file provided by DIAMONDS. From here we can calculate
    the background model, which in turn provides the final values for the fit
    '''

    def __init__(self,kwargs,runID=None):
        '''
        Constructor for the summary class. KICID and RunID are set within the Baseclass,
        which provides properties for these parameters.
        :param kicID: The KICID for the star
        :type kicID: string
        :param runID: The RunID for the star, can be fullBackground or noiseOnly
        :type runID: string
        '''
        BackgroundBaseFileModel.__init__(self, kwargs, runID)
        self.kwargs = kwargs
        self._rawValues = {}
        self._priorValues = {}
        self.logger = logging.getLogger(__name__)

        if(runID is not None):
            self._readData(kwargs)

    def dataLength(self):
        return len(self._priorValues)

    def getRawData(self,key=None):
        '''
        Gets the raw data from the parameterSummary, i.e. Median, LowCredLim,UpCredLim.
        Calls the internal function _getInternalData, which contains the logic on what to return.
        Can return the full dict or just one element. If no key is provided, it will return
        the full dict
        :param key: The key for the dict. Optional
        :type key: string
        :return: Full dict if key is None(default), one value if key is not None
        :rtype: dict/float
        '''
        return self._getDataWrapper(self._rawValues, key)

    def getData(self,key=None):
        '''
        Gets the full BackgroundModel of the ParameterSummary, so all 6/9 values that
        were fitted by DIAMONDS. Calls the internal function _getInternalData, which
        contains the logic on what to return.
        Can return the full dict or just one element. If no key is provided it will return
        the full dict
        :param key: The key for the dict. Optional
        :type key: string
        :return: Full dict if key is None (default), one value if key is not None
        :rtype: dict/float
        '''
        return self._getDataWrapper(self._priorValues,key)

    def _getDataWrapper(self,map,key):
        if any(map) is False:
            self._readData(self.kwargs)
        return self._getInternalData(map,key)

    def _getInternalData(self,dict,key):
        '''
        Internal reader function. Checks if the dict is false, i.e. not existend and reads
        the data if necessary. Checks if the key is in the dictionary and returns the element,
        otherwise returns the full dict
        :param dict: Dictionary containing the data.
        :type dict: dict
        :param key: Key contained in dict. Optional
        :type key: string
        :return: Full dictionary or one value, depending on key is none
        :rtype: dict/float
        '''

        return self._getValueFromDict(dict,key)

    def _readData(self,kwargs):
        '''
        Internal reader function. Reads the values of the backgroundSummary file and creates
        the background model. If something fails in reading, the raw values and the
        background model will be set empty.
        '''
        if general_background_result_path in kwargs.keys():
            dataFolder = kwargs[general_background_result_path]
        else:
            dataFolder = kwargs[general_background_result_path] + "/Background/results/"

        file = dataFolder+"KIC"+self.kicID+"/"+self.runID+"/background_parameterSummary.txt"
        try:

            values = np.loadtxt(file).T
            for i in range(0,7):
                self._rawValues[summaryValues[i]] = values[i]

            self._createBackgroundModel()
        except Exception as e:
            raise FileNotFoundError("Cannot find summary file!")

    def _createBackgroundModel(self):
        '''
        Creates the backgroundModel
        '''
        par_median = self._rawValues[strSummaryMedian]
        par_le = self._rawValues[strSummaryLowCredLim]
        length = 7
        if len(par_median) > 7 and len(par_le) > 7:
            length = 10

        for i in range(0,length):
            self._priorValues[priorNames[i]] = ufloat(par_median[i], abs(par_median[i] - par_le[i]))