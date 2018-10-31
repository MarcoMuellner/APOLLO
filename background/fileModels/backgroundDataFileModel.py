import glob
import logging

import numpy as np

from res.strings import *
from settings.settings import Settings

from background.fileModels.backgroundBaseFileModel import BackgroundBaseFileModel


class BackgroundDataFileModel(BackgroundBaseFileModel):
    '''
    Represents the data file which diamonds will perform a fit on. This should either be
    already exist within the DIAMONDS file structure (i.e. in background/data/) or should
    have been created using the powerspectraCalculator. The file should contain in its
    first axis the frequencies in uHz and in its second axis the power in ppm^2
    '''
    def __init__(self,kicID = None):
        '''
        Constructor for the DataFile class. Sets the KicID and kicks of reading of the file.
        :param kicID: The KICID of the star
        :type kicID: string
        '''
        self.logger = logging.getLogger(__name__)
        BackgroundBaseFileModel.__init__(self,kicID)

        if kicID is not None:
            self._readData()

    @property
    def powerSpectralDensity(self):
        '''
        Property for the PSD of the KICId.
        :return: Data of the PSD. 1st axis -> frequency in uHz,2nd axis -> PSD in ppm^2
        :rtype: 2-D numpy array
        '''
        return self._psd

    def _readData(self):
        '''
        Internal reader function. Reads the file according to the settings
        '''
        dataFolder = Settings.ins().getSetting(strDiamondsSettings, strSectBackgroundDataPath).value
        file = dataFolder+"KIC"+self.kicID+".txt"
        try:
            self._psd = np.loadtxt(file).T
        except FileNotFoundError as e:
            self.logger.error("Cannot read PSD file, setting PSD to none")
            self.logger.error("File is "+file)
            self.logger.error(e)
            raise IOError("Cannot read PSD file, setting PSD to none")


