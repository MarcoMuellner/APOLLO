from astropy.io import fits
import numpy as np
import pylab as pl
from settings.settings import Settings
from support.strings import *
import logging

class FitsReader:
    def __init__(self,filename):
        self.logger =logging.getLogger(__name__)
        self.setFitsFile(filename)
        return

    def __readData(self,filename):
        scidata = None
        if ".fits" in filename:
            hdulist = fits.open(filename)
            self.logger.debug("Opening fits file '" + filename + "'")
            hdulist.info()
            scidata = hdulist[0].data
            self.__mode = "fits"#todo in string
        elif ".txt" in filename:
            self.logger.debug("Opening txt file '" + filename + "'")
            scidata = np.loadtxt(filename)
            self.__mode = "txt" #todo in string
        else:
            self.logger.debug("File not recognised!")
            raise ValueError
        scidata = scidata.transpose()
        scidata = scidata.transpose()
        return scidata

    #This method uses a combination of segments in lightcurves
    def __refineDataCombiningMethod(self,scidata):
        prevTime = scidata[0][0]
        intervall = 0
        if self.__mode == "fits":#todo in string
            intervall = scidata[1][0] - scidata[0][0]
        elif self.__mode == "txt":#todo in string
            intervall = scidata[1][0] - scidata[0][0]
        self.logger.debug("Intervall is '"+str(intervall)+"'")
        arrays = []
        fluxArray =[]
        timeArray = []
        lenTime = 0
        lenFlux = 0
        zeroValue = 0
        for i in range(0, scidata.shape[0] - 1):
            if abs(scidata[i][1])<10**-2:
                continue

            if (abs(scidata[i][0]-prevTime - intervall) > 10**-1):
                self.logger.debug("Difference is '"+str(scidata[i][0]-prevTime - intervall)+"'")
                arrays.append((timeArray,fluxArray))
                lenTime += len(timeArray)
                lenFlux += len(fluxArray)
                timeArray = []
                fluxArray = []
                self.logger.debug("Scidata is '"+str(scidata[i][0])+"'")
                self.logger.debug("Prevtime is '"+str(prevTime)+"'")
                self.logger.debug("Intervall is '"+str(intervall)+"'")
                zeroValue = zeroValue+scidata[i][0] - prevTime+intervall
                self.logger.debug("ZeroValue is '"+str(zeroValue)+"'")


            timeArray.append(scidata[i][0] - zeroValue)
            fluxArray.append(scidata[i][1])
            prevTime = scidata[i][0]

        lenTime += len(timeArray)
        lenFlux += len(fluxArray)
        arrays.append((timeArray,fluxArray))

        resultTime = np.zeros(lenTime)
        resultFlux = np.zeros(lenFlux)
        prevlength = 0
        for i in arrays:
            self.logger.debug(min(i[0]))
            self.logger.debug(max(i[0]))
            resultTime[prevlength:prevlength + len(i[0])] = np.array(i[0])
            resultFlux[prevlength:prevlength + len(i[0])] = np.array(i[1])
            prevlength += len(i[0])

        return (resultTime,resultFlux)

    #This method cuts the lightcurve and returns every segment
    def __refineDataCuttingMethod(self,scidata):
        time = np.zeros(scidata.shape[0])
        flux = np.zeros(scidata.shape[0])


        prevTime = scidata[0][0]
        intervall = 0
        if self.__mode == "fits":#todo in string
            intervall = scidata[1][0] - scidata[0][0]
        elif self.__mode == "txt":#todo in string
            intervall = scidata[1][0] - scidata[0][0]
        self.logger.debug("Intervall is '"+str(intervall)+"'")
        arrays = []
        fluxArray =[]
        timeArray = []
        zeroValue = 0
        for i in range(0, scidata.shape[0] - 1):
            if abs(scidata[i][1])<10**-2:
                continue

            if (abs(scidata[i][0]-prevTime - intervall) > 10**-1):
                self.logger.debug("Difference is '"+str(scidata[i][0]-prevTime - intervall)+"'")
                arrays.append((timeArray,fluxArray))
                timeArray = []
                fluxArray = []
                zeroValue = scidata[i][0]

            timeArray.append(scidata[i][0] - zeroValue)
            fluxArray.append(scidata[i][1])
            prevTime = scidata[i][0]

        arrays.append((timeArray,fluxArray))
        npArrays = []


        maxIndex = 0
        previousMaxLength = 0
        counter = 0
        for i in arrays:
            npArr = np.array((i[0],i[1]))
            npArrays.append(npArr)

            if len(npArr[0]) > previousMaxLength and max(npArr[0])<150:
                maxIndex = counter
                self.logger.debug("Previous length: '" +str(previousMaxLength) +"'")
                self.logger.debug("New Length: '"+str(len(npArr[0]))+"'")
                self.logger.debug("MaxIndex: '"+str(counter)+"'")
                previousMaxLength = len(npArr[0])


            counter +=1
        # Removing Data where T=0
        # This doesn't hurt eitherway, and fixes data which is strange
        #nullID = np.where(time == 0.0)
        #time = np.delete(time, nullID[0])
        #flux = np.delete(flux, nullID[0])
        #time = time - np.amin(time)

        return npArrays[maxIndex]

    def getLightCurve(self):
        if len(self.__lightCurve[0]) > 300000:
            return (self.__lightCurve[0][0:300000],
                    self.__lightCurve[1][0:300000])
        else:
            return self.__lightCurve

    def setFitsFile(self,fileName):
        mode = Settings.Instance().getSetting(strDataSettings, strSectLightCurveAlgorithm).value
        self.logger.debug("Mode is '"+mode+"'")
        self.__fileContent = self.__readData(fileName)
        if mode == strLightCombining:
            self.__lightCurve = self.__refineDataCombiningMethod(self.__fileContent)
        elif mode == strLightCutting:
            self.__lightCurve = self.__refineDataCuttingMethod(self.__fileContent)
        else:
            self.logger.debug("Failed to find refine data method with: '" + mode+"'")
            raise ValueError
        self.logger.debug(len(self.getLightCurve()[0]))
        self.logger.debug(len(self.getLightCurve()[1]))
        pl.figure()
        #todo temporary
        return self.getLightCurve()

    def getNyquistFrequency(self):
        if self.__lightCurve is not None:
            self.__nyq = 2 * np.pi * self.__lightCurve[0].size / (2 * (self.__lightCurve[0][3] - self.__lightCurve[0][2]) * 24 * 3600)
            return self.__nyq
        else:
            self.logger.debug("Lightcure is None, therefore no calculation of nyquist frequency possible")
            return None
