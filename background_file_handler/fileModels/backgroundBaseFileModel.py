import logging
import numpy as np
from res.conf_file_str import general_kic
from support.printer import print_int

class BackgroundBaseFileModel:
    '''
    Base class for the background filereaders. Creates some properties for the kicIDs, units and provides an interface
    for some methods that have to be implemented
    '''
    def __init__(self,kwargs,runID = None):
        '''
        Constructor of the Baseclass
        :param star_id: KICId of the star
        :type star_id: string
        :param runID: RunID of the star. Can be Oscillation/Noise dependend on which file you want to read
        :type runID: string
        '''
        self.logger = logging.getLogger(__name__)
        try:
            self._kicID = str(kwargs[general_kic])
        except:
            pass
        self._runID = runID

    def getData(self,*args):
        raise NotImplementedError

    def _readData(self,kwargs):
        raise NotImplementedError

    @property
    def unit(self):
        try:
            return self._unit
        except NameError or AttributeError:
            print_int("Unit not set, setting to empty",self.kwargs)
            self._unit = ""
            return self._unit

    def _getValueFromDict(self,dict,key):
        if key is None:
            return dict
        else:
            try:
                return dict[key]
            except:
                print_int("No value for key '"+key+"',returning full dict",kwargs)
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
            print_int("Failed to open File "+file,kwargs)
            print_int(e,kwargs)
            raise IOError("Failed to open file. "+file)
        return data

    @property
    def id(self):
        '''
        ID of the marginal distribution (between 0 and 9)
        :return: ID
        :rtype: int
        '''
        return self._id

    @id.setter
    def id(self,value):
        '''
        Sets the ID and rereads the data
        :param value: ID
        :type value: int
        '''
        if value is None:
            self._id = ""
        else:
            self._id = value
        if self.kicID not in ["",None] and self.runID not in ["",None] and self._id not in ["",None]:
            self._readData()
