import logging

import numpy as np
from astropy.io import fits

from res.strings import *
from settings.settings import Settings


class InputFileReader:
    """
    With this class you can easily read different kinds of files containing lightCurves. At the moment EPIC, fits and
    simple 2-D txt files are available for this class. After calling the constructor, the class will run the computation
    """

    def __init__(self, filename):
        """
        Constructor of the FileReader. Triggers the computation of the psd.
        :param filename: Filepath + filename of the lightcurve file that needs reading
        :type filename: str
        """
        self.logger = logging.getLogger(__name__)
        self.setFitsFile(filename)


    def setFitsFile(self, fileName):
        """
        This method is the entrypoint and the only public method. It triggers the reading of a file and the refinement
        of the data if necessary
        :param fileName: Filepath + filename of the lightcurve file that needs reading
        :type fileName: str
        :return: LightCurve of the file. 1st axis temporal axis in hours, 2nd axis flux
        :rtype: 2-D numpy array
        """
        self._rawData = self._readData(fileName)
        self.lightCurve = self._refineData(self._rawData)
        return self.lightCurve

    def _refineData(self, rawData):
        """
        Runs the fileContent through a refinement process. It will call the combining or cutting method, depending
        on the settings and than triggers the removement of the stray if the settings say so.
        :param rawData: Content of the file read by _readData()
        :type rawData: 2-D numpy array
        :return: Refined lightCurve
        :rtype: 2-D numpy array
        """
        splitMode = Settings.Instance().getSetting(strDataSettings, strSectLightCurveAlgorithm).value
        if splitMode == strLightCombining:
            lightCurve = self._refineDataCombiningMethod(rawData)
        elif splitMode == strLightCutting:
            lightCurve = self._refineDataCuttingMethod(rawData)
        else:
            self.logger.debug("Failed to find refine data method with: '" + splitMode + "'")
            raise ValueError

        if strRefineStray == Settings.Instance().getSetting(strDataSettings, strSectDataRefinement).value:
            lightCurve = self._removeStray(lightCurve[0],lightCurve[1])

        return lightCurve

    def _removeStray(self,x,y):
        """
        Removes the stray values of an array. For this it takes the mean of the flux, and removes all values above
        1.1*mean and below 0.9*mean
        :param x: temporal axis
        :type x:ndarray
        :param y:flux
        :type y:ndarray
        :return:2-D numpy array without the strays
        :rtype:2-D numpy array
        """

        x = x[y > np.mean(y) * 0.9]
        y = y[1][y > np.mean(y) * 0.9]

        x = x[y < np.mean(y) * 1.1]
        y = y[y < np.mean(y) * 1.1]
        y -= np.amin(y)
        return np.array((x, y))

    def _readData(self, filename):
        """
        Reads the raw data from the file depending on the type. The following modes are available:
        - fits files -> reads the data, expects a fits file with 2 arrays
        - EPIC data -> KIC data for young stars. Reads the 0th and 10th column
        - txt files -> assumes a simple 2-D numpy array in the KIC files
        :param filename: Filepath + filename of the lightcurve file that needs reading
        :type filename:str
        :return: The raw data of the file.
        """
        self.logger.debug("Reading file "+filename)
        if ".fits" in filename:
            hdulist = fits.open(filename)
            rawData = hdulist[0].data
            self._mode = "fits"
        elif ".dat.txt" in filename:
            rawData = np.loadtxt(filename, skiprows=1, usecols=(0, 10))
            self._mode = "txt"
        elif ".txt" in filename:
            rawData = np.loadtxt(filename)
            self._mode = "txt"
        else:
            self.logger.debug("File not recognised!")
            raise ValueError
        self.logger.debug("Ending is " + self._mode)
        return rawData

    # This method uses a combination of segments in lightcurves
    def _refineDataCombiningMethod(self, rawData):
        """
        This method creates a combination of segments in lightCurves. This is necessary if the data is split up, so
        that there are areas where no measurement took place. It removes this segment and simply appends the next
        segment. You can also split the segments up using _refineDataCuttingMethod
        :param rawData: The raw data of the file, read by _readData()
        :return: The combined version of rawData
        :rtype: 2-D numpy array
        """
        zeroTimeStamp = rawData[0][0]
        deltaTime = rawData[1][0] - rawData[0][0]

        self.logger.debug("Zero timestamp is '" + str(deltaTime) + "h'")
        self.logger.debug("Delta time between two points is '" + str(deltaTime) + "h'")

        arrays = []
        fluxArray = []
        timeArray = []
        lenTime = 0
        lenFlux = 0
        zeroValue = 0
        for i in range(0, rawData.shape[0] - 1):
            if abs(rawData[i][1]) < 10 ** -2:
                continue

            if (abs(rawData[i][0] - zeroTimeStamp - deltaTime) > 10 ** -1):
                self.logger.debug("Difference between two points is '" + str(rawData[i][0] - zeroTimeStamp - deltaTime) + "'")
                arrays.append((timeArray, fluxArray))
                lenTime += len(timeArray)
                lenFlux += len(fluxArray)
                timeArray = []
                fluxArray = []
                self.logger.debug("Raw data is '" + str(rawData[i][0]) + "'")
                self.logger.debug("Zero timestamp is '" + str(zeroTimeStamp) + "'")
                self.logger.debug("Delta time is '" + str(deltaTime) + "'")
                zeroValue = zeroValue + rawData[i][0] - zeroTimeStamp + deltaTime
                self.logger.debug("ZeroValue is '" + str(zeroValue) + "'")

            timeArray.append(rawData[i][0] - zeroValue)
            fluxArray.append(rawData[i][1])
            zeroTimeStamp = rawData[i][0]

        lenTime += len(timeArray)
        lenFlux += len(fluxArray)
        arrays.append((timeArray, fluxArray))

        resultTime = np.zeros(lenTime)
        resultFlux = np.zeros(lenFlux)
        prevlength = 0
        for i in arrays:
            self.logger.debug(min(i[0]))
            self.logger.debug(max(i[0]))
            resultTime[prevlength:prevlength + len(i[0])] = np.array(i[0])
            resultFlux[prevlength:prevlength + len(i[0])] = np.array(i[1])
            prevlength += len(i[0])

        return (resultTime, resultFlux)

    # This method cuts the lightcurve and returns every segment
    def _refineDataCuttingMethod(self, rawData):
        """
        This method cuts the data up into segments, and removes the areas where no observation took place. It will
        than return the dataset with the most datapoints. The second possibility is _refineDataCombiningMethod
        :param rawData: The raw data of the file read in _readData
        :return: The dataset with the most datapoints in the lightCurve
        :rtype: 2-D numpy array
        """

        self.logger.debug("First x value is " + str(rawData[0][0]))
        self.logger.debug("Second x value is " + str(rawData[1][0]))

        zeroTimeStamp = rawData[0][0]
        deltaTime = rawData[1][0] - rawData[0][0]
        self.logger.debug("Zero timestamp is '" + str(zeroTimeStamp) + "h'")
        self.logger.debug("Delta time is '" + str(deltaTime) + "h'")

        arrays = []
        fluxArray = []
        timeArray = []
        zeroValue = 0
        for i in range(0, rawData.shape[0] - 1):
            if abs(rawData[i][1]) < 10 ** -2:
                continue

            if (abs(rawData[i][0] - zeroTimeStamp - deltaTime) > 10 ** -1):
                self.logger.debug("Difference is '" + str(rawData[i][0] - zeroTimeStamp - deltaTime) + "'")
                arrays.append((timeArray, fluxArray))
                timeArray = []
                fluxArray = []
                zeroValue = rawData[i][0]

            timeArray.append(rawData[i][0] - zeroValue)
            fluxArray.append(rawData[i][1])
            zeroTimeStamp = rawData[i][0]

        arrays.append((timeArray, fluxArray))
        npArrays = []

        maxIndex = 0
        previousMaxLength = 0
        for it, (arrZero, arrOne) in enumerate(arrays):
            npArr = np.array((arrZero, arrOne))
            npArrays.append(npArr)

            if len(npArr[0]) > previousMaxLength and max(npArr[0]) < 150:
                maxIndex = it
                self.logger.debug("Previous length: '" + str(previousMaxLength) + "'")
                self.logger.debug("New Length: '" + str(len(npArr[0])) + "'")
                self.logger.debug("MaxIndex: '" + str(it) + "'")
                previousMaxLength = len(npArr[0])

        return npArrays[maxIndex]

    @property
    def lightCurve(self):
        """
        Property of the lightCurve. Only returns up to 300 000 datapoints
        :return: The lightcurve
        :rtype: 2-D numpy array
        """
        if len(self._lightCurve[0]) > 300000:
            return (self._lightCurve[0][0:300000],
                    self._lightCurve[1][0:300000])
        else:
            return self._lightCurve

    @lightCurve.setter
    def lightCurve(self,value):
        """
        Setter property for the lightCurve
        :param value: Value for the lightCurve
        :type value: 2-D numpy array
        """
        self._lightCurve = value
