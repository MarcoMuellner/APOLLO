import glob
import logging

import numpy as np

from background_file_handler.fileModels.backgroundBaseFileModel import BackgroundBaseFileModel
from res.strings import *
from res.conf_file_str import general_background_result_path,internal_path,analysis_folder_prefix
from uncertainties import ufloat
from support.printer import print_int
from support.exceptions import EvidenceFileNotFound


class BackgroundEvidenceFileModel(BackgroundBaseFileModel):
    '''
    This class represents the evidence file DIAMONDS creates during its run. It has three different values, each value
    is saved inside the _evidence map, which can be accessed using the stringtypes defined in strings.py. See
    BaseBackgroundFile for documentation for further documentation of the base class
    '''
    def __init__(self,kwargs,runID = None):
        '''
        The constructor for the evidence class. Similarly to the other classes, it reads the data from the file
        :param star_id: The KICId of the star.
        :type star_id: string
        :param runID: the RunID of the run. Can be Oscillation/Noise  -> see strings.py
        :type runID: string
        '''
        self.logger = logging.getLogger(__name__)
        BackgroundBaseFileModel.__init__(self, kwargs, runID)

        self._evidence = {}
        self.kwargs = kwargs

        if(runID is not None):
            self._readData(kwargs)

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
                print_int("No value for key '"+key+"', returning full dict",self.kwargs)
                return self._evidence

    def _readData(self,kwargs):
        '''
        Reads the data from the background_evidenceInformation file. Uses the settings configured in
        ~/lightcurve_analyzer.json
        :return: Dict containing the values in the evidence file
        :rtype:dict{string:float}
        '''
        if general_background_result_path in kwargs.keys():
            self._dataFolder = kwargs[general_background_result_path]
        else:
            self._dataFolder = kwargs[internal_path] + "/Background/results/"
        file = self._dataFolder + self.kwargs[analysis_folder_prefix] + self.kicID + "/" + self.runID + "/background_evidenceInformation.txt"
        try:
            values = np.loadtxt(file).T

            self._evidence[strEvidSkillLog] = values[0]
            self._evidence[strEvidSkillErrLog] = values[1]
            self._evidence[strEvidSkillInfLog] = values[2]
            self._evidence[strEvidSkillLogWithErr] = ufloat(values[0], values[1])
        except Exception as e:
            raise EvidenceFileNotFound("Failed to open File '" +file,kwargs)
