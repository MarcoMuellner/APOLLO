import glob
import logging

import numpy as np

from settings.settings import Settings
from support.strings import *


class Evidence:
    def __init__(self,kicID = None,runID = None):
        self.m_evidence = {}
        self.logger = logging.getLogger(__name__)
        self.m_kicID = kicID
        self.m_runId = runID

        if(kicID is not None and runID is not None):
            self.__readData()

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
        return self.getData()

    def getData(self,key=None):
        if any(self.m_evidence) is False:
            self.__readData()

        if key is None:
            return self.m_evidence
        else:
            try:
                return self.m_evidence[key]
            except:
                self.logger.warning("No value for key '"+key+"', returning full dict")
                return self.m_evidence

    def __readData(self):
        try:
            self.m_dataFolder = Settings.Instance().getSetting(strDiamondsSettings,
                                                               strSectBackgroundResPath).value
            mpFile = glob.glob(self.m_dataFolder + 'KIC{}/{}/background_evidenceInformation.txt'
                               .format(self.m_kicID, self.m_runId))[0]
            values = np.loadtxt(mpFile).T
            self.m_evidence[strEvidenceSkillLog] = values[0] 
            self.m_evidence[strEvidenceSkillErrLog] = values[1] 
            self.m_evidence[strEvidenceSkillInfLog] = values[2] 
        except:
            self.logger.warning("Failed to open File '" + self.m_dataFolder +
                    'KIC{}/{}/background_evidenceInformation.txt'.format(self.m_kicID, self.m_runId) + "'")
            self.logger.warning("Setting Data to None")
            self.m_evidence = {}
