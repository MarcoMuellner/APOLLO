import logging
import numpy as np

class BackgroundBaseFileModel:
    '''
    Base class for the background filereaders. Creates some properties for the kicIDs, units and provides an interface
    for some methods that have to be implemented
    '''
    def __init__(self,kicID = None,runID = None):
        '''
        Constructor of the Baseclass
        :param kicID: KICId of the star
        :type kicID: string
        :param runID: RunID of the star. Can be fullBackground/noiseOnly dependend on which file you want to read
        :type runID: string
        '''
        self.logger = logging.getLogger(__name__)
        self._kicID = kicID
        self._runID = runID

    def getData(self,*args):
        raise NotImplementedError

    def _readData(self):
        raise NotImplementedError

    @property
    def unit(self):
        try:
            return self._unit
        except NameError or AttributeError:
            self.logger.warning("Unit not set, setting to empty")
            self._unit = ""
            return self._unit

    def _getValueFromDict(self,dict,key):
        if key is None:
            return dict
        else:
            try:
                return dict[key]
            except:
                self.logger.warning("No value for key '"+key+"',returning full dict")
                return dict


    @property
    def kicID(self):
        return self._kicID

    @kicID.setter
    def kicID(self,value):
        self._kicID = self._wrapperRunIDKicID(value)
        self._checkReadAndRead()

    @property
    def runID(self):
        return self._runID

    @runID.setter
    def runID(self,value):
        self._runID = self._wrapperRunIDKicID(value)
        self._checkReadAndRead()

    def _wrapperRunIDKicID(self,value):
        if value is None:
            return ""
        else:
            return value

    def _checkReadAndRead(self):
        if self._kicID not in ["",None] and self._runID not in ["",None]:
            self._readData()

    def _readFile(self,file):
        try:
            data = np.loadtxt(file).T
        except FileNotFoundError as e:
            self.logger.error("Failed to open File "+file)
            self.logger.error(e)
            raise IOError("Failed to open file. "+file)
        return data
