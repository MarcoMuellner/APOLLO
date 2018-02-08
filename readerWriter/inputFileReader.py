import logging

import numpy as np
from astropy.io import fits

from res.strings import *
from settings.settings import Settings
import pylab as pl
from fitter.fitFunctions import *
from plotter.plotFunctions import *
from plotnine import *


class InputFileReader:
    """
    With this class you can easily read different kinds of files containing lightCurves. At the moment EPIC, fits and
    simple 2-D txt files are available for this class. After calling the constructor, the class will run the computation
    """

    def __init__(self, filename,kicID):
        """
        Constructor of the FileReader. Triggers the computation of the psd.
        :param filename: Filepath + filename of the lightcurve file that needs reading
        :type filename: str
        """
        self.logger = logging.getLogger(__name__)
        self.kicID = kicID
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
        elif splitMode == strLightInterpolating:
            lightCurve = self._refineDataInterpolation(rawData)
        else:
            raise ValueError("Failed to find refine data method with: '" + splitMode + "'")

        return self._removeStray(lightCurve[0],lightCurve[1])

    def _removeStray(self,x,y):
        """
        Removes the stray values of a lightcurve. For this, a histogramm of the y-Values is created, and all values
        below/above 5 sigma are removed from the curve.
        :param x: temporal axis
        :type x:ndarray
        :param y:flux
        :type y:ndarray
        :return:2-D numpy array without the strays
        :rtype:2-D numpy array
        """
        plotData = {"Before Reduction":(np.array((x,y)), geom_point,None)}
        sigma = 5

        bins = np.linspace(np.amin(y),np.amax(y),int((np.amax(y)-np.amin(y))/20))

        hist = np.histogram(y,bins=bins)[0]
        bins = bins[0:len(bins)-1]

        cen = bins[np.where(hist==np.amax(hist))]
        wid = np.std(hist)
        if Settings.Instance().getSetting(strDataSettings, strSectStarType) == strStarTypeRedGiant:
            amp = (np.amax(hist))*np.sqrt(2*np.pi)*wid*np.exp(((cen/wid)**2)/2)
        else:
            amp = np.amax(hist)


        p0 = [0,amp,cen[0],wid]
        boundaries = ([-0.1,-np.inf,-np.inf,-np.inf],[0.1,np.inf,np.inf,np.inf])

        popt,__ = scipyFit(bins,hist,gaussian,p0,boundaries)

        (cen,wid) = (popt[2],popt[3])

        lin = np.linspace(np.min(bins),np.max(bins),len(bins)*100)

        histogramPlotData = {"Histogramm":(np.array((bins,hist)),geom_line,'solid'),
                             "Initial Fit":(np.array((lin,gaussian(lin,*p0))),geom_line,'solid'),
                             "Fit":(np.array((lin,gaussian(lin,*popt))),geom_line,'solid'),
                             "Negative Boundary": (np.array(([cen - sigma * wid])), geom_vline, 'dashed'),
                             "Positive Boundary": (np.array(([cen + sigma * wid])), geom_vline, 'dashed')}

        plotCustom(self.kicID,self.kicID+"_histogramm",histogramPlotData ,"bins","counts",self.kicID+"_histogramm",5)

        x = x[np.logical_and(y > cen - sigma * wid, y < cen + sigma * wid)]
        y = y[np.logical_and(y > cen - sigma * wid, y < cen + sigma * wid)]

        plotData["After Reduction"] = (np.array((x, y)), geom_point, None)
        plotCustom(self.kicID,self.kicID+"_reduction",plotData,"Time (d)","Flux (ppm)",self.kicID+"_reduction",5)

        y -= cen

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

    def _refineDataCombiningMethod(self,rawData):
        rawData = rawData.T
        (gapIDs, mostCommon, rawData) = self._prepareRawAndSearchGaps(rawData)

        if not gapIDs.size or gapIDs is None:
            return rawData


        for i in gapIDs:
            rawData[0][i:] += rawData[0][i]-rawData[0][i+1]+ mostCommon

        return rawData

    def _refineDataCuttingMethod(self,rawData):
        rawData = rawData.T
        (gapIDs, mostCommon, rawData) = self._prepareRawAndSearchGaps(rawData)

        if not gapIDs.size or gapIDs is None:
            return rawData

        diffGap = gapIDs[1:len(gapIDs)] - gapIDs[0:len(gapIDs) - 1]
        idMaxDiff = np.argmax(diffGap)

        return np.array((rawData[0][gapIDs[idMaxDiff]:gapIDs[idMaxDiff+1]],rawData[1][gapIDs[idMaxDiff]:gapIDs[idMaxDiff+1]]))

    def _refineDataInterpolation(self,rawData):

        rawData = rawData.T

        (gapIDs,mostCommon,rawData) = self._prepareRawAndSearchGaps(rawData)

        if not gapIDs.size or gapIDs is None:
            return rawData

        incrementer = 0

        for i in gapIDs:
            #ident moves the ID after each
            ident = i+incrementer

            count = int(np.round((rawData[0][ident+1]-rawData[0][ident])/mostCommon))

            deltaY = (rawData[1][ident+1] - rawData[1][ident])/count

            insertY = np.linspace(rawData[1][ident]+deltaY,rawData[1][ident+1]-deltaY,num=count-1)
            insertX = np.linspace(rawData[0][ident]+mostCommon,rawData[0][ident+1] - mostCommon,num=count-1)

            x = np.insert(rawData[0], ident + 1, insertX)
            y = np.insert(rawData[1], ident + 1, insertY)

            rawData = np.array((x,y))
            incrementer += count - 1


        return rawData


    def _prepareRawAndSearchGaps(self, rawData):
        x = rawData[0]
        diffX = np.round(x[1:len(x)] - x[0:len(x)-1],decimals=2)
        realDiffX = x[1:len(x)] - x[0:len(x) - 1]
        (values,counts) = np.unique(realDiffX,return_counts=True)
        mostCommon = values[np.argmax(counts)]

        rawData = np.array(((rawData[0]-rawData[0][0]),rawData[1]))
        return (np.where(diffX !=  np.round(mostCommon,decimals=2))[0],mostCommon,rawData)

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
