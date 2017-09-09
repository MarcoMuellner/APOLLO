from settings.settings import Settings
import glob
import numpy as np
from support.strings import *


class DataFile():

    def __init__(self,kicID = None):
        self. m_kicID = kicID
        if kicID is not None:
            self.setkicID(kicID)

    def getPSD(self):
        return self.m_psd

    def setkicID(self,kicID):
        self. m_kicID = kicID
        self.m_dataFolder = Settings.Instance().getSetting(strDiamondsSettings, strSectBackgroundDataPath).value
        self.m_psdFile = glob.glob(self.m_dataFolder+'KIC{}.txt'.format(kicID))[0]
        self.m_psd = np.loadtxt(self.m_psdFile).T
        return self.getPSD()

