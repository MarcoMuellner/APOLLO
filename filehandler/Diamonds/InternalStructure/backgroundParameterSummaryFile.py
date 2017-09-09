import glob
import logging

import numpy as np
from uncertainties import ufloat

from settings.settings import Settings
from support.strings import *
from filehandler.Diamonds.InternalStructure.backgroundAbstractFile import BaseBackgroundFile


class ParameterSummary(BaseBackgroundFile):
    """
    This class represents the summary file provided by DIAMONDS. From here we can calculate
    the background model, which in turn provides the final values for the fit
    """

    def __init__(self,kicID=None,runID=None):
        """
        Constructor for the summary class. KICID and RunID are set within the Baseclass,
        which provides properties for these parameters.
        :param kicID: The KICID for the star
        :type kicID: string
        :param runID: The RunID for the star, can be fullBackground or noiseOnly
        :type runID: string
        """
        BaseBackgroundFile.__init__(self,kicID,runID)
        self._rawValues = {}
        self.logger = logging.getLogger(__name__)

        if(kicID is not None and runID is not None):
            self._readData()

    def getRawData(self,key=None):
        """
        Gets the raw data from the parameterSummary, i.e. Median, LowCredLim,UpCredLim.
        Calls the internal function _getInternalData, which contains the logic on what to return.
        Can return the full dict or just one element. If no key is provided, it will return
        the full dict
        :param key: The key for the dict. Optional
        :type key: string
        :return: Full dict if key is None(default), one value if key is not None
        :rtype: dict/float
        """
        if any(self._rawValues) is False:
            self._readData()
        return self._getInternalData(self._rawValues,key)

    def getData(self,key=None):
        """
        Gets the full BackgroundModel of the ParameterSummary, so all 6/9 values that
        were fitted by DIAMONDS. Calls the internal function _getInternalData, which
        contains the logic on what to return.
        Can return the full dict or just one element. If no key is provided it will return
        the full dict
        :param key: The key for the dict. Optional
        :type key: string
        :return: Full dict if key is None (default), one value if key is not None
        :rtype: dict/float
        """
        if any(self._priorValues) is False:
            self._readData()
        return self._getInternalData(self._priorValues,key)

    def _getInternalData(self,dict,key):
        """
        Internal reader function. Checks if the dict is false, i.e. not existend and reads
        the data if necessary. Checks if the key is in the dictionary and returns the element,
        otherwise returns the full dict
        :param dict: Dictionary containing the data.
        :type dict: dict
        :param key: Key contained in dict. Optional
        :type key: string
        :return: Full dictionary or one value, depending on key is none
        :rtype: dict/float
        """

        if key is None:
            return dict
        else:
            try:
                return dict[key]
            except:
                self.logger.warning("No value for key '"+key+"',returning full dict")
                return dict

    def _readData(self):
        """
        Internal reader function. Reads the values of the backgroundSummary file and creates
        the background model. If something fails in reading, the raw values and the
        background model will be set empty.
        """
        try:
            self.m_dataFolder = Settings.Instance().getSetting(strDiamondsSettings,
                                                               strSectBackgroundResPath).value
            mpFile = glob.glob(self.m_dataFolder + 'KIC{}/{}/background_parameterSummary.txt'
                               .format(self.kicID, self.runID))[0]
            values = np.loadtxt(mpFile).T
            self._rawValues[strSummaryMean] = values[0]
            self._rawValues[strSummaryMedian] = values[1]
            self._rawValues[strSummaryMode] = values[2]
            self._rawValues[strSummaryIIMoment] = values[3]
            self._rawValues[strSummaryLowCredLim] = values[4]
            self._rawValues[strSummaryUpCredLim] = values[5]
            self._rawValues[strSummarySkew] = values[6]

            self._createBackgroundModel()
        except Exception as e:
            self.logger.warning("Failed to open File '" + self.m_dataFolder +
                    'KIC{}/{}/background_parameterSummary.txt'.format(self.kicID, self.runID) + "'")
            self.logger.warning(e)
            self.logger.warning("Setting Data to None")
            self._rawValues = {}
            self._priorValues = {}

    def _createBackgroundModel(self):
        """
        Creates the backgroundModel
        """
        par_median = self._rawValues[strSummaryMedian]
        par_le = self._rawValues[strSummaryLowCredLim]

        self._priorValues = {}
        self._priorValues[strPriorFlatNoise] = ufloat(par_median[0], abs(par_median[0] - par_le[0]))
        self._priorValues[strPriorAmpHarvey1] = ufloat(par_median[1], abs(par_median[1] - par_le[1]))
        self._priorValues[strPriorFreqHarvey1] = ufloat(par_median[2], abs(par_median[2] - par_le[2]))
        self._priorValues[strPriorAmpHarvey2] = ufloat(par_median[3], abs(par_median[3] - par_le[3]))
        self._priorValues[strPriorFreqHarvey2] = ufloat(par_median[4], abs(par_median[4] - par_le[4]))
        self._priorValues[strPriorAmpHarvey3] = ufloat(par_median[5], abs(par_median[5] - par_le[5]))
        self._priorValues[strPriorFreqHarvey3] = ufloat(par_median[6], abs(par_median[6] - par_le[6]))
        if len(par_median)>7 and len(par_le)>7:
            self._priorValues[strPriorHeight] = ufloat(par_median[7], abs(par_median[7] - par_le[7]))
            self._priorValues[strPriorNuMax] = ufloat(par_median[8], abs(par_median[8] - par_le[8]))
            self._priorValues[strPriorSigma] = ufloat(par_median[9], abs(par_median[9] - par_le[9]))