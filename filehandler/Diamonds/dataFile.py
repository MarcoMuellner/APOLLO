from settings.settings import Settings
import glob
import numpy as np
from support.strings import *
import logging


class DataFile:
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
        dataFolder = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundDataPath).value
        self.logger = logging.getLogger(__name__)

        self._psdFile = glob.glob(dataFolder+'KIC{}.txt'.format(kicID))[0]
        self.kicID = kicID

    @property
    def kicID(self):
        '''
        Property for the KICId
        :return: The KICId of the star
        :rtype: string
        '''
        return self._kicID

    @kicID.setter
    def kicID(self,value):
        '''
        Setter property of the KICId. ReReads the data if it is not None
        :param value: the KICID of the star
        :type value: string
        '''
        self._kicID = value
        if self._kicID is not None:
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
        try:
            self._psd = np.loadtxt(self._psdFile).T
        except FileNotFoundError:
            self.logger.error("Cannot read PSD file, setting PSD to none")
            self._psd = None


