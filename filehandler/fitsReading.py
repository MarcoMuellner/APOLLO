import numpy as np
from astropy.io import fits

class FitsReader:
    def __init__(self,filename):
        self.setFitsFile(filename)
        return

    def __readData(self,filename):
        hdulist = fits.open(filename)
        print("Opening file '" + filename + "'")
        hdulist.info()
        scidata = hdulist[0].data
        return scidata

    def __refineData(self,scidata):
        time = np.zeros(scidata.shape[0])
        flux = np.zeros(scidata.shape[0])


        prevTime = scidata[0][0]
        intervall = scidata[1][0] - scidata[0][0]
        print("Intervall is '"+str(intervall)+"'")
        arrays = []
        fluxArray =[]
        timeArray = []
        zeroValue = 0
        for i in range(0, scidata.shape[0] - 1):
            if abs(scidata[i][1])<10**-6:
                continue

            if (abs(scidata[i][0]-prevTime - intervall) > 10**-6):
                print("Difference is '"+str(scidata[i][0]-prevTime - intervall)+"'")
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
            print(len(i[0]))
            npArr = np.array((i[0],i[1]))
            npArrays.append(npArr)

            if len(npArr[0]) > previousMaxLength and max(npArr[0])<150:
                maxIndex = counter
                print("Previous length: '" +str(previousMaxLength) +"'")
                print("New Length: '"+str(len(npArr[0]))+"'")
                print("MaxIndex: '"+str(counter)+"'")
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
        return self.__lightCurve

    def setFitsFile(self,fileName):
        self.__fileContent = self.__readData(fileName)
        self.__lightCurve = self.__refineData(self.__fileContent)
        return self.getLightCurve()

    def getNyquistFrequency(self):
        if self.__lightCurve is not None:
            self.__nyq = 2 * np.pi * self.__lightCurve[0].size / (2 * (self.__lightCurve[0][3] - self.__lightCurve[0][2]) * 24 * 3600)
            return self.__nyq
        else:
            print("Lightcure is None, therefore no calculation of nyquist frequency possible")
            return None
