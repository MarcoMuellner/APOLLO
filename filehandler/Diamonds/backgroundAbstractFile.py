import logging

class BaseBackgroundFile:
    """
    Base class for the background filereaders. Creates some properties for the kicIDs, units and provides an interface
    for some methods that have to be implemented
    """
    def __init__(self,kicID = None,runID = None):
        """
        Constructor of the Baseclass
        :param kicID: KICId of the star
        :type kicID: string
        :param runID: RunID of the star. Can be fullBackground/noiseOnly dependend on which file you want to read
        :type runID: string
        """
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


    @property
    def kicID(self):
        return self._kicID

    @kicID.setter
    def kicID(self,value):
        self._kicID = value
        if self._kicID is not None and self._runID is not None:
            self._readData()

    @property
    def runID(self):
        return self._runID

    @runID.setter
    def runID(self,value):
        self._runID = value
        if self._kicID is not None and self._runID is not None:
            self._readData()
