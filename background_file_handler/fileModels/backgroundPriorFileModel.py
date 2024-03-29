import glob
import logging
from typing import List,Tuple,Dict
import numpy as np

from background_file_handler.fileModels.backgroundBaseFileModel import BackgroundBaseFileModel
from res.strings import *
from support.printer import print_int
from res.conf_file_str import general_background_result_path,internal_path,analysis_folder_prefix


class BackgroundPriorFileModel(BackgroundBaseFileModel):
    '''
    This class represents the priors with which the diamonds run was done. There are multiple ways this class
    reads the priors. In general, if the runID is None, it will read the Oscillation/Noise priors
    and are accessible via the getData function using the mode as a parameter. If a runID is provided, it will
    return the correct priors independently of the mode set.
    '''

    def __init__(self,kwargs,runID = None):
        '''
        Constructor for the PriorSetup. KicID and runID are set via the BaseBackgroundFile class.
        :param star_id: KicID of the star. Optional, but should be set here. If not set via property setter
        :type star_id: string
        :param runID: RunID of the star. Optional. If None it will read the ones in the parent directory of the results
        :type runID: string
        '''
        BackgroundBaseFileModel.__init__(self, kwargs, runID)

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

        self.kwargs = kwargs
        self.logger = logging.getLogger(__name__)

    def getData(self, key=None, mode=strDiModeFull):
        '''
        Returns the dataset accordingly to the set runID, mode and key. If the runID is None, it will return the
        map/tuple according to the mode. If it is not none, it will look indepently, even if you provide a wrong mode.
        :param key: Key within the map. If provided, it will return one tuple. Is part of the parameterNames list
        :type key:string
        :param mode: Defines the PriorFile that is returned. One for Oscillation/Noise
        :type mode: string
        :return:Dataset
        :rtype:dict/2-D tuple
        '''
        dict = self._fullPriors if mode == strDiModeFull else self._noisePriors
        if any(dict) is False and (self.runID is None or
                                    (any(self._fullPriors) is False and any(self._noisePriors) is False)):
            self._readData(self.kwargs)
            dict = self._fullPriors if mode == strDiModeFull else self._noisePriors

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

    def _readData(self,kwargs):
        '''
        Reads the data. If runID is not None, it will read only one file, the one in the result of the mode. If it is
        None it will read both in the parent directory
        '''
        filesToLoad = []
        if general_background_result_path in kwargs.keys():
            dataFolder = self.kwargs[general_background_result_path]
        else:
            dataFolder = self.kwargs[internal_path] + "/Background/results/"

        basePath = dataFolder + self.kwargs[analysis_folder_prefix] + self.kicID + "/"
        if self.runID is not None:
            if self.runID == "Oscillation":
                filesToLoad.append(basePath + self.runID + "/background_hyperParametersUniform_lower.txt")
                filesToLoad.append(basePath + self.runID + "/background_hyperParametersGaussian_nu_max.txt")
                filesToLoad.append(basePath + self.runID + "/background_hyperParametersUniform_upper.txt")
            else:
                file = basePath + self.runID + "/background_hyperParametersUniform.txt"
                filesToLoad.append(file)
        else:
            file = basePath + "background_hyperParameters.txt"
            filesToLoad.append(file)
            file = basePath + "background_hyperParameters_noise.txt"
            filesToLoad.append(file)
            file = basePath + "background_hyperParametersUniform_lower.txt"
            filesToLoad.append(file)
            file = basePath + "background_hyperParametersGaussian_nu_max.txt"
            filesToLoad.append(file)
            file = basePath + "background_hyperParametersUniform_upper.txt"
            filesToLoad.append(file)
        try:
            for files in filesToLoad:
                try:
                    values = np.vstack((values,np.loadtxt(files)))
                except UnboundLocalError:
                    values = np.loadtxt(files)
        except (FileNotFoundError,IOError) as e:
            pass

        for it,(priorMin,priorMax) in enumerate(values):
            if len(values)>7:
                self._fullPriors[self._parameterNames[it]] = (priorMin,priorMax)
            else:
                self._noisePriors[self._parameterNames[it]] = (priorMin,priorMax)

    def rewritePriors(self,priors : Dict[str,Tuple[float,float]]):
        if general_background_result_path in self.kwargs.keys():
            dataFolder = self.kwargs[general_background_result_path]
        else:
            dataFolder = self.kwargs[internal_path] + "/Background/results/"

        basePath = dataFolder + self.kwargs[analysis_folder_prefix] + self.kicID + "/"

        if len(priors) == 10:
            file = basePath + "background_hyperParameters.txt"
        else:
            file = basePath + "background_hyperParameters_noise.txt"

        dataList = []
        for name in self._parameterNames[0:len(priors)]:
            dataList.append(priors[name])

        data = np.array(dataList)

        np.savetxt(file, data, fmt='%10.14f')

    def _getFullPath(self,path):
        '''
        This method will create an absolute path if the path it inputs wasn't that already
        :param path: The path you want to have the absolute of
        :type path: str
        :return: Absolute path
        :rtype: str
        '''
        if path[0] not in ["~", "/", "\\"]:
            print_int("Setting priors to full path",self.kwargs)
            print_int("Prepending" + ROOT_PATH,self.kwargs)
            path = ROOT_PATH + "/" + path
            print_int("New path: "+path,self.kwargs)
        else:
            print_int("Path is already absolute path",self.kwargs)

        return path
