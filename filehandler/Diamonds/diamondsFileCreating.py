import os
import numpy as np

from settings.settings import Settings
from support.strings import *
from support.directoryManager import cd
import logging

class FileCreater:
    def __init__(self,kicID,powerspectrum,nyquistFrequency,priors):
        self.logger = logging.getLogger(__name__)
        self.dataFolder = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundDataPath).value
        self.resultsFolder = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundResPath).value

        self.kicID = kicID
        self.powerSpectrum = powerspectrum
        self.powerSpectrum = self.powerSpectrum.transpose()
        self.nyq = nyquistFrequency
        self.priors = priors

        self.__createFolder()
        self.__createdata()
        self.__createPriors()
        self.__createNSMC_configuringParameters()
        self.__createXmeans_configuringParameters()
        self.__createNyquistFrequency()

        return

    def __createFolder(self):
        self.fullResultPath = self.resultsFolder + "KIC"+self.kicID
        print(self.fullResultPath)
        if not os.path.exists(self.fullResultPath):
            os.makedirs(self.fullResultPath)
        return

    def __createPriors(self):
        arr_full = self.priors
        arr_min = self.priors[:7]
        filename_full = "background_hyperParameters.txt"
        filename_min = "background_hyperParameters_noise.txt"
        self.__saveNumpyArray(self.fullResultPath,filename_full,arr_full,'14')
        self.__saveNumpyArray(self.fullResultPath, filename_min, arr_min,'14')
        return

    def __createNSMC_configuringParameters(self):
        arr = np.array([500,500,1000,1500,50,2.10,0.01,0.01]).transpose()
        filename = "NSMC_configuringParameters.txt"
        self.__saveNumpyArray(self.fullResultPath, filename, arr)
        return

    def __createNyquistFrequency(self):
        arr = np.array([self.nyq])
        filename = "NyquistFrequency.txt"
        self.__saveNumpyArray(self.fullResultPath,filename,arr)
        return

    def __createXmeans_configuringParameters(self):
        arr = np.array([1,10]).transpose()
        arr.transpose()
        filename = "Xmeans_configuringParameters.txt"
        self.__saveNumpyArray(self.fullResultPath,filename,arr)
        return

    def __saveNumpyArray(self,path,filename,array,comma ='14'):
        self.logger.debug("Saving filename "+filename+" to "+path)
        with cd(path):
            np.savetxt(filename,array,fmt='%10.'+comma+'f')

    def __createdata(self):
        filename = "KIC"+str(self.kicID)+".txt"
        self.__saveNumpyArray(self.dataFolder,filename,self.powerSpectrum)
        return
