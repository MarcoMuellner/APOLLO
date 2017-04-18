from settings.settings import Settings
import glob
import numpy as np
from support.strings import *


class DataFile():
    '''
    Creates an object representing one KIC file.
    '''
    m_kicID = None
    m_psd = None
    m_psdFile = None
    m_dataFolder = None

    def __init__(self,kicID = None):
        '''
        Constructor of DataFile. Creates an object containing the
        content of KIC Files
        :param kicID: The Identifier of the KIC File. Should be the numbers
                        passt 'KIC'
        '''
        self. m_kicID = kicID
        if kicID is not None:
            self.setkicID(kicID)

    def getPSD(self):
        '''
        Get Powerspectrum of KIC Files. Type is Numpy array with 2 columns
        :return: Numpy array containing data
        '''
        return self.m_psd

    def setkicID(self,kicID):
        '''
        Sets the used KIC File. Returns content
        :param kicID: The Identifier of the KIC File. Should be the numbers
                        passt 'KIC'
        :return: Numpy array containing data
        '''
        self. m_kicID = kicID
        self.m_dataFolder = Settings.Instance().getSetting(strDataSettings, strSectBackgroundDataPath).value
        self.m_psdFile = glob.glob(self.m_dataFolder+'KIC{}.txt'.format(kicID))[0]
        self.m_psd = np.loadtxt(self.m_psdFile).T
        return self.getPSD()

