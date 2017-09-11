import glob
import logging

import numpy as np

from filehandler.Diamonds.backgroundAbstractFile import BaseBackgroundFile
from settings.settings import Settings
from support.strings import *


class Evidence(BaseBackgroundFile):
    """
    This class represents the evidence file DIAMONDS creates during its run. It has three different values, each value
    is saved inside the _evidence map, which can be accessed using the stringtypes defined in strings.py. See
    BaseBackgroundFile for documentation for further documentation of the base class
    """
    def __init__(self,kicID = None,runID = None):
        """
        The constructor for the evidence class. Similarly to the other classes, it reads the data from the file
        :param kicID: The KICId of the star.
        :type kicID: string
        :param runID: the RunID of the run. Can be fullBackground or noiseOnly -> see strings.py
        :type runID: string
        """
        BaseBackgroundFile.__init__(self,kicID,runID)
        self._evidence = {}
        self.logger = logging.getLogger(__name__)

        if(kicID is not None and runID is not None):
            self.__readData()

    def getData(self,key=None):
        """
        Returns the evidence map. Reads it if necessary
        :param key: One of the three used to setup the dict -> see strings.py
        :type key: string
        :return: The dictionary or single value of the gathered data
        :rtype: dict{string:float}/float
        """
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
        """
        Reads the data from the background_evidenceInformation file. Uses the settings configured in
        ~/lightcurve_analyzer.json
        :return: Dict containing the values in the evidence file
        :rtype:dict{string:float}
        """
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
                    'KIC{}/{}/background_evidenceInformation.txt'.format(self.kicID, self.runID) + "'")
            self.logger.warning("Setting Data to None")
            self._evidence = {}
