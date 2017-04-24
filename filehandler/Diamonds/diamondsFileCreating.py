import os
import numpy as np

from settings.settings import Settings
from support.strings import *
from support.directoryManager import cd

class FileCreater:
    def __init__(self,kicID,powerspectrum,nyquistFrequency,priors):
        self.__dataFolder = Settings.Instance().getSetting(strDataSettings, strSectBackgroundDataPath).value
        self.__resultsFolder = Settings.Instance().getSetting(strDataSettings, strSectBackgroundResPath).value

        self.__kicID = kicID
        self.__powerSpectrum = powerspectrum
        self.__powerSpectrum = self.__powerSpectrum.transpose()
        self.__nyq = nyquistFrequency
        self.__priors = priors

        self.__createFolder()
        self.__createdata()
        self.__createPriors()
        self.__createNSMC_configuringParameters()
        self.__createXmeans_configuringParameters()
        self.__createNyquistFrequency()

        return

    def __createFolder(self):
        self.__fullResultPath = self.__resultsFolder + "KIC"+self.__kicID
        if not os.path.exists(self.__fullResultPath):
            os.makedirs(self.__fullResultPath)
        return

    def __createPriors(self):
        arr_full = self.__priors
        arr_min = self.__priors[:6]
        filename_full = "background_hyperParameters.txt"
        filename_min = "background_hyperParameters_noise.txt"
        self.__saveNumpyArray(self.__fullResultPath,filename_full,arr_full)
        self.__saveNumpyArray(self.__fullResultPath, filename_min, arr_min)
        return

    def __createNSMC_configuringParameters(self):
        arr = np.array([500,500,1000,1500,50,2.10,0.01,0.01]).transpose()
        filename = "NSMC_configuringParameters.txt"
        self.__saveNumpyArray(self.__fullResultPath, filename, arr)
        return

    def __createNyquistFrequency(self):
        arr = np.array([self.__nyq])
        filename = "NyquistFrequency.txt"
        self.__saveNumpyArray(self.__fullResultPath,filename,arr)
        return

    def __createXmeans_configuringParameters(self):
        arr = np.array([1,10]).transpose()
        arr.transpose()
        filename = "Xmeans_configuringParameters.txt"
        self.__saveNumpyArray(self.__fullResultPath,filename,arr)
        return

    def __saveNumpyArray(self,path,filename,array):
        with cd(path):
            np.savetxt(filename,array,fmt='%10.14f')

    def __createdata(self):
        filename = "KIC"+str(self.__kicID)+".txt"
        self.__saveNumpyArray(self.__dataFolder,filename,self.__powerSpectrum)
        return
