import glob
import logging

import numpy as np

from background.fileModels.backgroundBaseFileModel import BackgroundBaseFileModel
from res.strings import *
from settings.settings import Settings


class BackgroundPriorFileModel(BackgroundBaseFileModel):
    '''
    This class represents the priors with which the diamonds run was done. There are multiple ways this class
    reads the priors. In general, if the runID is None, it will read the fullBackground and noiseOnly priors
    and are accessible via the getData function using the mode as a parameter. If a runID is provided, it will
    return the correct priors independently of the mode set.
    '''

    def __init__(self,kicID = None,runID = None):
        '''
        Constructor for the PriorSetup. KicID and runID are set via the BaseBackgroundFile class.
        :param kicID: KicID of the star. Optional, but should be set here. If not set via property setter
        :type kicID: string
        :param runID: RunID of the star. Optional. If None it will read the ones in the parent directory of the results
        :type runID: string
        '''
        BackgroundBaseFileModel.__init__(self, kicID, runID)

        self._fullPriors = {}
        self._noisePriors = {}
        self._parameterNames = [strPriorFlatNoise,
                                strPriorAmpHarvey1,
                                strPriorFreqHarvey1,
                                strPriorAmpHarvey2,
                                strPriorFreqHarvey2,
                                strPriorAmpHarvey3,
                                strPriorFreqHarvey3,
                                strPriorHeight,
                                strPriorNuMax,
                                strPriorSigma]
        self.logger = logging.getLogger(__name__)

    def getData(self,key=None,mode=strDiamondsModeFull):
        '''
        Returns the dataset accordingly to the set runID, mode and key. If the runID is None, it will return the
        map/tuple according to the mode. If it is not none, it will look indepently, even if you provide a wrong mode.
        :param key: Key within the map. If provided, it will return one tuple. Is part of the parameterNames list
        :type key:string
        :param mode: Defines the PriorFile that is returned. One for fullBackground and noiseOnly
        :type mode: string
        :return:Dataset
        :rtype:dict/2-D tuple
        '''
        self.logger.debug("Retrieving data with key "+str(key) + " and mode "+mode)

        dict = self._fullPriors if mode == strDiamondsModeFull else self._noisePriors
        self.logger.debug("Data is ")
        self.logger.debug(dict)
        if any(dict) is False and (self.runID is None or
                                    (any(self._fullPriors) is False and any(self._noisePriors) is False)):
            self._readData()
            dict = self._fullPriors if mode == strDiamondsModeFull else self._noisePriors

        if any(dict) is False and self.runID is not None:
            if any(self._fullPriors) is True:
                dict = self._fullPriors
            elif any(self._noisePriors) is True:
                dict = self._noisePriors
            else:
                self.logger.error("Something went terribly wrong. Neither noisePriors or fullBackground were set"
                                  "properly")
                raise ValueError

        return self._getValueFromDict(dict,key)

    def _readData(self):
        '''
        Reads the data. If runID is not None, it will read only one file, the one in the result of the mode. If it is
        None it will read both in the parent directory
        '''
        filesToLoad = []
        values = []
        dataFolder = self._getFullPath(Settings.Instance().getSetting(strDiamondsSettings,
                                                                            strSectBackgroundResPath).value)
        basePath = dataFolder + "KIC" + self.kicID + "/"
        if self.runID is not None:
            file = basePath + self.runID + "/background_hyperParametersUniform.txt"
            filesToLoad.append(file)
        else:
            file = basePath + "background_hyperParameters.txt"
            filesToLoad.append(file)
            file = basePath + "background_hyperParameters_noise.txt"
            filesToLoad.append(file)
        try:
            for files in filesToLoad:
                values.append(np.loadtxt(files).T)
        except FileNotFoundError as e:
            self.logger.error("Failed to open Prior file")
            self.logger.error(e)
            raise IOError("Failed to open Prior file")

        for priorList in values:
            for it,(priorMin,priorMax) in enumerate(zip(priorList[0],priorList[1])):
                if len(priorList[0])>7:
                    self._fullPriors[self._parameterNames[it]] = (priorMin,priorMax)
                else:
                    self._noisePriors[self._parameterNames[it]] = (priorMin,priorMax)

    def _getFullPath(self,path):
        '''
        This method will create an absolute path if the path it inputs wasn't that already
        :param path: The path you want to have the absolute of
        :type path: str
        :return: Absolute path
        :rtype: str
        '''
        if path[0] not in ["~", "/", "\\"]:
            self.logger.debug("Setting priors to full path")
            self.logger.debug("Prepending" + ROOT_PATH)
            path = ROOT_PATH + "/" + path
            self.logger.debug("New path: "+path)
        else:
            self.logger.debug("Path is already absolute path")

        return path
