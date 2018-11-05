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
        self.setFile(filename)



    def setFile(self, fileName):
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
        splitMode = Settings.ins().getSetting(strDataSettings, strSectLightCurveAlgorithm).value

        if splitMode == strLightCombining:
            lightCurve = self._refineDataCombiningMethod(rawData)
        elif splitMode == strLightCutting:
            lightCurve = self._refineDataCuttingMethod(rawData)
        elif splitMode == strLightInterpolating:
            lightCurve = self._refineDataInterpolation(rawData)
        else:
            raise ValueError("Failed to find refine data method with: '" + splitMode + "'")

        lightCurve = self._removeStray(lightCurve[0],lightCurve[1])

        if Settings.ins().getSetting(strDataSettings,strSectStarType).value == strStarTypeYoungStar:
            lightCurve = self._cutoffDataAtFrequency(30,lightCurve)

        return lightCurve

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
        plotData = {"Before Reduction":(np.array((x,y)), 'x')}
        sigma = 5

        bins = np.linspace(np.amin(y),np.amax(y),int((np.amax(y)-np.amin(y))/20))

        hist = np.histogram(y,bins=bins,density=True)[0]

        mids = (bins[1:]+bins[:-1])/2
        cen = np.average(mids,weights=hist)
        wid = np.sqrt(np.average((mids-cen)**2,weights=hist))

        p0 = [0,cen,wid]
        bins=bins[:-1]

        popt,__ = scipyFit(bins,hist,gaussian,p0)

        (cen,wid) = (popt[1],popt[2])

        lin = np.linspace(np.min(bins),np.max(bins),len(bins)*5)

        histogramPlotData = {"Histogramm":(np.array((bins,hist)),'-'),
                             "Initial Fit":(np.array((lin,gaussian(lin,*p0))),'-'),
                             "Fit":(np.array((lin,gaussian(lin,*popt))),'-'),
                             "Negative Boundary": (np.array(([cen - sigma * wid])), '|'),
                             "Positive Boundary": (np.array(([cen + sigma * wid])), '|')}

        plotCustom(self.kicID,self.kicID+"_histogramm",histogramPlotData ,"bins","counts",self.kicID+"_histogramm",5)

        data = []
        for i in [x,y]:
            data.append(i[np.logical_and(y > cen - sigma * wid, y < cen + sigma * wid)])

        x = data[0]
        y = data[1]

        plotData["After Reduction"] = (np.array((x, y)), 'x')
        plotCustom(self.kicID,self.kicID+"_reduction",plotData,"Time (d)","Flux (ppm)",self.kicID+"_reduction",5)

        y -= cen

        pl.rc('font', family='serif')
        #pl.rc('text', usetex=True)
        pl.rc('xtick', labelsize='x-small')
        pl.rc('ytick', labelsize='x-small')
        fig = pl.figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        ax.set_title(f"KIC{self.kicID}")
        rect = [0.7, 0.08, 0.3, 0.3]
        ax1 = add_subplot_axes(ax, rect)
        ax.plot(x, y, 'o', color='k', markersize=2)
        ax.set_facecolor('white')
        ax1.plot(bins, hist, 'x', color='k', markersize=4)
        ax1.plot(lin,gaussian(lin,*popt),color='k')
        ax1.axvline(cen - sigma * wid,ls='dashed',color='k')
        ax1.axvline(cen + sigma * wid, ls='dashed',color='k')
        ax.set_xlabel("Time (days)")
        ax.set_ylabel("Flux")
        ax1.set_xlabel('Delta F')
        ax1.set_ylabel(r'N')
        ax1.set_xlim((cen - sigma * wid*1.2),(cen +sigma * wid*1.2))
        ResultsWriter.getInstance(self.kicID).addImage(self.kicID,f"Lightcurve_KIC_{self.kicID}",fig)

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
            if rawData is None:
                rawData = hdulist[1].data
                rawData = np.array((rawData['TIME'],rawData['SAP_FLUX']))
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

        if gapIDs is None or not gapIDs.size :
            return rawData


        for i in gapIDs:
            rawData[0][i:] += rawData[0][i]-rawData[0][i+1]+ mostCommon

        x = rawData[0]
        y = rawData[1]

        y = y[x>0]
        x = x[x>0]

        rawData = np.array((x,y))

        return rawData

    def _refineDataCuttingMethod(self,rawData):
        rawData = rawData.T
        (gapIDs, mostCommon, rawData) = self._prepareRawAndSearchGaps(rawData)

        if gapIDs is None or not gapIDs.size:
            return rawData

        diffGap = gapIDs[1:len(gapIDs)] - gapIDs[0:len(gapIDs) - 1]
        idMaxDiff = np.argmax(diffGap)

        xArr = rawData[0][gapIDs[idMaxDiff]:gapIDs[idMaxDiff+1]]
        yArr = rawData[1][gapIDs[idMaxDiff]:gapIDs[idMaxDiff+1]]
        xArr = xArr[1:]
        yArr = yArr[1:]
        xArr -=xArr[0]

        arr =  np.array((xArr,yArr))
        return arr


    def _refineDataInterpolation(self,rawData):

        rawData = rawData.T

        (gapIDs,mostCommon,rawData) = self._prepareRawAndSearchGaps(rawData)

        if gapIDs is None or not gapIDs.size:
            return rawData

        incrementer = 0

        for i in gapIDs:
            #ident moves the ID after each
            ident = i+incrementer

            count = int(np.round((rawData[0][ident+1]-rawData[0][ident])/mostCommon))

            deltaY = (rawData[1][ident+1] - rawData[1][ident])/count
            lister = [(0,rawData[0],mostCommon),(1,rawData[1],deltaY)]
            data = []

            #inserts new block of data into the dataset for x and y
            for (id,raw,adder) in lister:
                insert = np.linspace(raw[ident]+adder,raw[ident+1]-adder,num=count-1)
                data.append(np.insert(raw, ident + 1, insert))

            rawData = np.array((data[0],data[1]))
            incrementer += count - 1

        return rawData


    def _prepareRawAndSearchGaps(self, rawData):
        x = rawData[0]
        diffX = np.round(x[1:len(x)] - x[0:len(x)-1],decimals=2)
        realDiffX = x[1:len(x)] - x[0:len(x) - 1]
        (values,counts) = np.unique(realDiffX,return_counts=True)
        mostCommon = values[np.argmax(counts)]

        rawData = np.array(((rawData[0]-rawData[0][0]),rawData[1]))

        gapIDs = np.where(diffX !=  np.round(mostCommon,decimals=2))
        if len(gapIDs[0]) == 0:
            gapIDs = None
        else:
            gapIDs = gapIDs[0]

        return (gapIDs,mostCommon,rawData)

    def _cutoffDataAtFrequency(self,f,lightCurve):
        tau = (10 ** 6 / f)/3600/24
        elements = len(lightCurve[0])
        t_step = np.mean(lightCurve[0][1:elements] - lightCurve[0][0:elements - 1])
        normalizedBinSize = int(np.round(tau / t_step))
        filteredLightCurve = lightCurve[1] - trismooth(lightCurve[1], normalizedBinSize)

        return np.array((lightCurve[0],filteredLightCurve))

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
