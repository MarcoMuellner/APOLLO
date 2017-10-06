import glob
import logging

import numpy as np

from background.fileModels.backgroundBaseFileModel import BackgroundBaseFileModel
from res.strings import *
from settings.settings import Settings
from uncertainties import ufloat


class BackgroundEvidenceFileModel(BackgroundBaseFileModel):
    '''
    This class represents the evidence file DIAMONDS creates during its run. It has three different values, each value
    is saved inside the _evidence map, which can be accessed using the stringtypes defined in strings.py. See
    BaseBackgroundFile for documentation for further documentation of the base class
    '''
    def __init__(self,kicID = None,runID = None):
        '''
        The constructor for the evidence class. Similarly to the other classes, it reads the data from the file
        :param kicID: The KICId of the star.
        :type kicID: string
        :param runID: the RunID of the run. Can be fullBackground or noiseOnly -> see strings.py
        :type runID: string
        '''
        self.logger = logging.getLogger(__name__)
        BackgroundBaseFileModel.__init__(self, kicID, runID)

        self._evidence = {}

        if(kicID is not None and runID is not None):
            self._readData()

    def getData(self,key=None):
        '''
        Returns the evidence map. Reads it if necessary
        :param key: One of the three used to setup the dict -> see strings.py
        :type key: string
        :return: The dictionary or single value of the gathered data
        :rtype: dict{string:float}/float
        '''
        if any(self._evidence) is False:
            self._readData()

        if key is None:
            return self._evidence
        else:
            try:
                return self._evidence[key]
            except:
                self.logger.warning("No value for key '"+key+"', returning full dict")
                return self._evidence

    def _readData(self):
        '''
        Reads the data from the background_evidenceInformation file. Uses the settings configured in
        ~/lightcurve_analyzer.json
        :return: Dict containing the values in the evidence file
        :rtype:dict{string:float}
        '''
        self._dataFolder = Settings.Instance().getSetting(strDiamondsSettings,
                                                          strSectBackgroundResPath).value
        file = self._dataFolder + "KIC" + self.kicID + "/" + self.runID + "/background_evidenceInformation.txt"
        try:
            values = np.loadtxt(file).T

            self._evidence[strEvidSkillLog] = values[0]
            self._evidence[strEvidSkillErrLog] = values[1]
            self._evidence[strEvidSkillInfLog] = values[2]
            self._evidence[strEvidSkillLogWithErr] = ufloat(values[0], values[1])
        except Exception as e:
            self.logger.error("Failed to open File '" +file)
            self.logger.error(e)
            raise IOError
