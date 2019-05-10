import glob
import logging
from typing import Dict

import numpy as np

from res.strings import *
from res.conf_file_str import general_background_data_path,internal_path
from support.printer import print_int

from background_file_handler.fileModels.backgroundBaseFileModel import BackgroundBaseFileModel


class BackgroundDataFileModel(BackgroundBaseFileModel):
    '''
    Represents the data file which diamonds will perform a fit on. This should either be
    already exist within the DIAMONDS file structure (i.e. in background/data/) or should
    have been created using the powerspectraCalculator. The file should contain in its
    first axis the frequencies in uHz and in its second axis the power in ppm^2
    '''
    def __init__(self,kwargs):
        '''
        Constructor for the DataFile class. Sets the KicID and kicks of reading of the file.
        :param kicID: The KICID of the star
        :type kicID: string
        '''
        self.logger = logging.getLogger(__name__)
        BackgroundBaseFileModel.__init__(self,kwargs)

        self._readData(kwargs)

    @property
    def powerSpectralDensity(self):
        '''
        Property for the PSD of the KICId.
        :return: Data of the PSD. 1st axis -> frequency in uHz,2nd axis -> PSD in ppm^2
        :rtype: 2-D numpy array
        '''
        return self._psd

    def _readData(self,kwargs : Dict):
        '''
        Internal reader function. Reads the file according to the settings
        '''
        if general_background_data_path in kwargs.keys():
            dataFolder = kwargs[general_background_data_path]
        else:
            dataFolder = kwargs[internal_path] + "/Background/data/"
        file = dataFolder+"KIC"+self.kicID+".txt"
        try:
            self._psd = np.loadtxt(file)
        except FileNotFoundError as e:
            print_int("Cannot read PSD file, setting PSD to none",kwargs)
            print_int("File is "+file,kwargs)
            print_int(e,kwargs)
            raise IOError("Cannot read PSD file, setting PSD to none")


