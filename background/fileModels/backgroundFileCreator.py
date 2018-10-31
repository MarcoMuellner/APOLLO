import logging

import numpy as np

from res.strings import *
from settings.settings import Settings
from support.directoryManager import cd


class BackgroundFileCreator:
    '''
    This class creates the files needed for a DIAMONDS run. It will create the paths, priors, NSMC configuring
    parameters, Nyquist frequency files and XMeans files. By instantiating this class, everything else
    will be handled internally
    '''
    def __init__(self,kicID,powerspectrum,nyquistFrequency,priors):
        '''
        Constructor for the fileCreater class.
        :param kicID: KICId for the star
        :type kicID: string
        :param powerspectrum: Powerspectraldensity of the star
        :type powerspectrum: 2-D numpy array
        :param nyquistFrequency: Nyquistfrequency of the Lightcurve
        :type nyquistFrequency: float
        :param priors: Priors for the DIAMONDS run. Will create the same priors for fullBackground and
        noiseOnly
        :type priors:9-D numpy array
        '''
        self.logger = logging.getLogger(__name__)
        self.dataFolder = Settings.ins().getSetting(strDiamondsSettings, strSectBackgroundDataPath).value
        self.resultsFolder = Settings.ins().getSetting(strDiamondsSettings, strSectBackgroundResPath).value

        self._kicID = kicID
        self._powerSpectrum = powerspectrum
        self._powerSpectrum = self._powerSpectrum.transpose()
        self._nyq = nyquistFrequency
        self._priors = priors

        self._createFolder()
        self._createData()
        self._createPriors()
        self._createNSMC_configuringParameters()
        self._createXmeans_configuringParameters()
        self._createNyquistFrequency()

    def _createFolder(self):
        '''
        creates the folder if it doesn't exist
        '''
        self.fullResultPath = self.resultsFolder + "KIC"+self._kicID
        if not os.path.exists(self.fullResultPath):
            os.makedirs(self.fullResultPath)

    def _createPriors(self):
        '''
        Writes the prior files to the appropiate place. Writes both fullBackground and noiseOnly
        '''
        arr_full = self._priors
        arr_min = self._priors[:7]
        filename_full = "background_hyperParameters.txt"
        filename_min = "background_hyperParameters_noise.txt"
        self._saveNumpyArray(self.fullResultPath,filename_full,arr_full,'14')
        self._saveNumpyArray(self.fullResultPath, filename_min, arr_min,'14')

    def _createNSMC_configuringParameters(self):
        '''
        Writes the nsmc configuring parameters
        '''
        arr = np.array([500,500,50000,1500,50,2.10,0.01,0.1]).transpose()
        filename = "NSMC_configuringParameters.txt"
        self._saveNumpyArray(self.fullResultPath, filename, arr)
        return

    def _createNyquistFrequency(self):
        '''
        Writes the nyquist frequency file
        '''
        arr = np.array([self._nyq])
        filename = "NyquistFrequency.txt"
        self._saveNumpyArray(self.fullResultPath,filename,arr)
        return

    def _createXmeans_configuringParameters(self):
        '''
        Writes the Xmeans file
        '''
        arr = np.array([1,10]).transpose()
        arr.transpose()
        filename = "Xmeans_configuringParameters.txt"
        self._saveNumpyArray(self.fullResultPath,filename,arr)
        return

    def _saveNumpyArray(self,path,filename,array,comma ='14'):
        '''
        Internally used class. Switches folder ans saves everything appropiatly
        :param path: Path where to save the file
        :type path: string
        :param filename: Filename of the file
        :type filename: string
        :param array: Data to set
        :type array: numpy array
        :param comma: How many decimal numbers will be written
        :type comma: string
        '''
        self.logger.info("Saving filename "+filename+" to "+path)
        with cd(path):
            np.savetxt(filename,array,fmt='%10.'+comma+'f')

    def _createData(self):
        '''
        Creates the data file
        '''
        filename = "KIC"+str(self._kicID) + ".txt"
        self._saveNumpyArray(self.dataFolder, filename, self._powerSpectrum)
        return
