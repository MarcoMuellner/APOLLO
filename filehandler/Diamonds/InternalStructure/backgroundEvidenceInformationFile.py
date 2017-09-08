import glob
import logging

import numpy as np

from settings.settings import Settings
from support.strings import *

from filehandler.Diamonds.InternalStructure.backgroundAbstractFile import BaseBackgroundFile


class Evidence(BaseBackgroundFile):
    def __init__(self,kicID = None,runID = None):
        BaseBackgroundFile.__init__(self,kicID,runID)
        self._evidence = {}
        self.logger = logging.getLogger(__name__)

        if(kicID is not None and runID is not None):
            self.__readData()

    def getData(self,key=None):
        if any(self._evidence) is False:
            self.__readData()

        if key is None:
            return self._evidence
        else:
            try:
                return self._evidence[key]
            except:
                self.logger.warning("No value for key '"+key+"', returning full dict")
                return self._evidence

    def __readData(self):
        try:
            self._dataFolder = Settings.Instance().getSetting(strDiamondsSettings,
                                                              strSectBackgroundResPath).value
            mpFile = glob.glob(self._dataFolder + 'KIC{}/{}/background_evidenceInformation.txt'
                               .format(self.kicID, self.runID))[0]
            values = np.loadtxt(mpFile).T
            self._evidence[strEvidenceSkillLog] = values[0]
            self._evidence[strEvidenceSkillErrLog] = values[1]
            self._evidence[strEvidenceSkillInfLog] = values[2]
        except:
            self.logger.warning("Failed to open File '" + self._dataFolder +
                    'KIC{}/{}/background_evidenceInformation.txt'.format(self.m_kicID, self.m_runId) + "'")
            self.logger.warning("Setting Data to None")
            self._evidence = {}
