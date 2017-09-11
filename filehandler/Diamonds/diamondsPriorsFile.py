from settings.settings import Settings
import numpy as np
import glob
from support.strings import *
import logging
from filehandler.Diamonds.backgroundAbstractFile import BaseBackgroundFile

class PriorSetup(BaseBackgroundFile):
    """
    This class represents the priors with which the diamonds run was done. There are multiple ways this class
    reads the priors. In general, if the runID is None, it will read the fullBackground and noiseOnly priors
    and are accessible via the getData function using the mode as a parameter. If a runID is provided, it will
    return the correct priors independently of the mode set.
    """

    def __init__(self,kicID = None,runID = None):
        """
        Constructor for the PriorSetup. KicID and runID are set via the BaseBackgroundFile class.
        :param kicID: KicID of the star. Optional, but should be set here. If not set via property setter
        :type kicID: string
        :param runID: RunID of the star. Optional. If None it will read the ones in the parent directory of the results
        :type runID: string
        """
        BaseBackgroundFile.__init__(self,kicID,runID)

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
        """
        Returns the dataset accordingly to the set runID, mode and key. If the runID is None, it will return the
        map/tuple according to the mode. If it is not none, it will look indepently, even if you provide a wrong mode.
        :param key: Key within the map. If provided, it will return one tuple. Is part of the parameterNames list
        :type key:string
        :param mode: Defines the PriorFile that is returned. One for fullBackground and noiseOnly
        :type mode: string
        :return:Dataset
        :rtype:dict/2-D tuple
        """
        dict = self._fullPriors if mode == strDiamondsModeFull else self._noisePriors
        if any(dict) is False and (self.runID is None or
                                    (any(self._fullPriors) is False and any(self._noisePriors) is False)):
            self._readData()
            dict = self._fullPriors if mode == strDiamondsModeFull else self._noisePriors
        elif any(dict) is False and self.runID is not None:
            if any(self._fullPriors) is True:
                dict = self._fullPriors
            elif any(self._noisePriors) is True:
                dict = self._noisePriors
            else:
                self.logger.error("Something went terribly wrong. Neither noisePriors or fullBackground were set"
                                  "properly")
                raise ValueError



        if key is None:
            return dict
        else:
            try:
                return dict[key]
            except:
                self.logger.warning("No value for key '"+key+"', returning full dict")
                return dict

    def _readData(self):
        """
        Reads the data. If runID is not None, it will read only one file, the one in the result of the mode. If it is
        None it will read both in the parent directory
        """
        values = []
        try:
            self._dataFolder = Settings.Instance().getSetting(strDiamondsSettings,
                                                               strSectBackgroundResPath).value
            if self.runID is not None:
                mpFile = glob.glob(self._dataFolder + 'KIC{}/{}/background_hyperParametersUniform.txt'
                                   .format(self.kicID, self.runID))[0]
                values.append(np.loadtxt(mpFile).T)
            else:
                mpFile = glob.glob(self._dataFolder + 'KIC{}/background_hyperParameters.txt'
                                   .format(self.kicID))[0]
                values.append(np.loadtxt(mpFile).T)
                mpFile = glob.glob(self._dataFolder + 'KIC{}/background_hyperParameters_noise.txt'
                                   .format(self.kicID))[0]
                values.append(np.loadtxt(mpFile).T)


            for priorList in values:
                it = 0
                for prior in priorList:
                    if len(priorList)>7:
                        self._fullPriors[self._parameterNames[it]] = prior
                    else:
                        self._noisePriors[self._parameterNames[it]] = prior

        except Exception as e:
            self.logger.warning("Failed to open Priors '" + self._dataFolder)
            self.logger.warning(e)
            self.logger.warning("Setting Data to None")
            self._fullPriors = {}
            self._noisePriors = {}
