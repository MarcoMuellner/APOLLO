from settings.settings import Settings
import numpy as np
import glob
from support.strings import *
from uncertainties import ufloat
import logging

class ParameterSummary:

    def __init__(self,kicID=None,runID=None):
        self.rawValues = {}
        self.logger = logging.getLogger(__name__)
        self.m_kicID  = kicID
        self.m_runId = runID
        if(kicID is not None and runID is not None):
            self.__readData()
        return

    def setKICID(self, kicId):
        '''
        Sets the KicID and rereads data
        :param kicId: KicID of the star
        :return: returns Data. See getData()
        '''
        self.m_kicID = kicId
        self.__readData()
        return self.getData()

    def setRunID(self, runId):
        '''
        Sets the RunID and rereads data
        :param runId: runId of the Diamonds run (subfolder in results file)!
        :return: returns Data. See getData()
        '''
        self.m_runId = runId
        self.__readData()
        return self.getData()

    def setParameters(self, kicId, runId):
        self.setKICID(kicId)
        self.setRunID(runId)
        return self.getData()

    def getData(self,key=None,priorData=False):
        if any(self.rawValues) is False:
            self.__readData()
        retDict = {}

        if priorData == True:
            retDict = self.priorValues
        else:
            retDict = self.rawValues

        if key is None:
            return retDict
        else:
            try:
                return retDict[key]
            except:
                self.logger.warning("No value for key '" + key + "', returning full dict")
                return retDict

    def __readData(self):
        try:
            self.m_dataFolder = Settings.Instance().getSetting(strDiamondsSettings,
                                                               strSectBackgroundResPath).value
            mpFile = glob.glob(self.m_dataFolder + 'KIC{}/{}/background_parameterSummary.txt'
                               .format(self.m_kicID, self.m_runId))[0]
            values = np.loadtxt(mpFile).T
            self.rawValues[strSummaryMean] = values[0] 
            self.rawValues[strSummaryMedian] = values[1] 
            self.rawValues[strSummaryMode] = values[2] 
            self.rawValues[strSummaryIIMoment] = values[3]  
            self.rawValues[strSummaryLowCredLim] = values[4]  
            self.rawValues[strSummaryUpCredLim] = values[5]
            self.rawValues[strSummarySkew] = values[6]

            self.__createBackgroundModel()
        except Exception as e:
            self.logger.warning("Failed to open File '" + self.m_dataFolder +
                    'KIC{}/{}/background_parameterSummary.txt'.format(self.m_kicID, self.m_runId) + "'")
            self.logger.warning(e)
            self.logger.warning("Setting Data to None")
            self.rawValues = {}

    def __createBackgroundModel(self):
        par_median = self.rawValues[strSummaryMedian]
        par_le = self.rawValues[strSummaryLowCredLim]
        par_ue = self.rawValues[strSummaryUpCredLim]

        self.priorValues = {}
        self.priorValues[strPriorFlatNoise] = ufloat(par_median[0],abs(par_median[0]-par_le[0]))
        self.priorValues[strPriorAmpHarvey1] = ufloat(par_median[1],abs( par_median[1] - par_le[1]))
        self.priorValues[strPriorFreqHarvey1] = ufloat(par_median[2], abs(par_median[2] - par_le[2]))
        self.priorValues[strPriorAmpHarvey2] = ufloat(par_median[3], abs(par_median[3] - par_le[3]))
        self.priorValues[strPriorFreqHarvey2] = ufloat(par_median[4], abs(par_median[4] - par_le[4]))
        self.priorValues[strPriorAmpHarvey3] = ufloat(par_median[5], abs(par_median[5] - par_le[5]))
        self.priorValues[strPriorFreqHarvey3] = ufloat(par_median[6], abs(par_median[6] - par_le[6]))
        if len(par_median)>7 and len(par_le)>7:
            self.priorValues[strPriorHeight] = ufloat(par_median[7], abs(par_median[7] - par_le[7]))
            self.priorValues[strPriorNuMax] = ufloat(par_median[8], abs(par_median[8] - par_le[8]))
            self.priorValues[strPriorSigma] = ufloat(par_median[9], abs(par_median[9] - par_le[9]))