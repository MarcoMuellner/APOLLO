import numpy as np
from math import log10,log,exp
import time as t
from scipy.signal import butter, filtfilt
from scipy import optimize
from calculations.powerspectraCalculations import PowerspectraCalculator
from plotter.plotFunctions import *
import pylab as pl

class NuMaxCalculator:
    def __init__(self,lightCurve,powerSpectra):
        self.__iterativeNuFilter = None
        self.setParameters(lightCurve,powerSpectra)
        return
    def __calculateFlickerAmplitude(self):
        #calculate Median Flux
        time = self.__lightCurve[0]
        flux = self.__lightCurve[1]

        medianFlux = np.median(flux)
        meanTimeBin = np.amax(time)/len(time)
        flickerSize = 5/24 # size of flickertime. This is calibrated by Kallinger. Measured in days

        binSize = int(flickerSize/meanTimeBin) #calculate the binsize of one flicker!
        iterations = len(time)/binSize #The number of iterations needed to calculate all single Amplitudes

        cutoffMax = 20 #These two parameters define the cutoff of things in the lightcurve you probably don't want
        cutoffMin = 0

        print("Flickersize is '"+str(flickerSize)+"'")
        print("MeanTimeBin is '"+str(meanTimeBin)+"'")
        print("Iterations is '"+str(iterations)+"'")


        flickerFluxArray = np.zeros(int(iterations-cutoffMax-cutoffMin))
        flickerTimeArray = np.zeros(int(iterations - cutoffMax -cutoffMin))
        binningArray = np.zeros(int(iterations - cutoffMax -cutoffMin))

        filteredFlux = np.zeros(len(flux))
        #iterate over all bins
        for i in range(0,int(iterations-cutoffMax - cutoffMin)):
            multiplicator = i
            #find values within bin
            fluxBin = flux[multiplicator*binSize:(multiplicator+1)*binSize]
            #find mean value within bin
            binningArray[multiplicator] = np.mean(fluxBin)

            #find mean value of time
            medianTimeBin = np.mean(time[multiplicator * binSize:(multiplicator + 1) * binSize])
            flickerTimeArray[multiplicator] = medianTimeBin

            #subtract mean value from array
            #todo this can be done better, when just using slicing within array
            filteredFlux[multiplicator*binSize:(multiplicator+1)*binSize] = flux[multiplicator*binSize:(multiplicator+1)*binSize] - np.mean(fluxBin)

        #this is the final flickerAmplitude!
        self.__flickerAmplitude = np.std(filteredFlux)

        return

    def getNyquistFrequency(self):
        if self.__lightCurve is not None:
            self.__nyq = 2 * np.pi * self.__lightCurve[0].size / (2 * (self.__lightCurve[0][3] - self.__lightCurve[0][2]) * 24 * 3600)
            return self.__nyq
        else:
            print("Lightcure is None, therefore no calculation of nyquist frequency possible")
            return None

    def __calculateInitFilterFrequency(self):
        self.__initNuFilter = 10**(5.187-1.560*log10(self.__flickerAmplitude))
        print("Initial Nu Filter is '"+str(self.__initNuFilter)+"'")
        return self.__initNuFilter

    def calculateIterativeFilterFrequency(self):
        filterFrequency = self.__iterativeNuFilter if self.__iterativeNuFilter is not None else self.__initNuFilter
        smoothed = self.butter_lowpass_filtfilt(self.__lightCurve[1], filterFrequency, self.getNyquistFrequency())

        psd = PowerspectraCalculator(np.array((self.__lightCurve[0],smoothed)))

        corr = self.calculateAutocorrelation(smoothed) #todo this seems to be a bottleneck here...

        corr = np.power(corr,2)
        stepFreq = self.__lightCurve[0][10] - self.__lightCurve[0][9]
        deltaF = np.zeros(len(corr))
        for i in range(0, len(deltaF)):
            deltaF[i] = i * stepFreq

        best_fit = self.scipyFit(np.array((deltaF, corr)))
        tauACF = best_fit[1]*24*60

        #pl.plot(deltaF,corr)
        #pl.plot(deltaF,self.sinc(deltaF,*best_fit))
        #pl.show()

        print("Tau_ACF is '"+str(tauACF)+"'")

        self.__iterativeNuFilter = 10**(3.098-0.932*log10(tauACF)-0.025*log10(tauACF)**2)
        self.__photonNoise = np.mean(self.__powerSpectra[1])*(1-best_fit[0]) if best_fit[0] < 1 else np.mean(self.__powerSpectra[1])
        print("Second iterative filter is '"+str(self.__iterativeNuFilter)+"'")
        print("Photon noise is '"+str(self.__photonNoise))
        return np.array((deltaF,corr)),best_fit

    def butter_lowpass_filtfilt(self,data, f, nyq, order=5):
        b, a = self.butter_lowpass(f, nyq, order=order)
        y = filtfilt(b, a, data)
        print(y)
        return y

    def butter_lowpass(self,cutoff, nyq, order=5):
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        print("------------------------------------------")
        print(b, a)
        print("------------------------------------------")
        return b, a

    def calculateAutocorrelation(self,oscillatingData):
        corrs2 = np.correlate(oscillatingData, oscillatingData, mode='full')
        N = len(corrs2)
        corrs2 = corrs2[N // 2:]
        lengths = range(N, N // 2, -1)
        corrs2 /= lengths
        corrs2 /= corrs2[0]
        maxcorr = np.argmax(corrs2)
        corrs2 = corrs2 / corrs2[maxcorr]
        return corrs2

    def sinc(self,x, a, tau_acf):
        return a * np.sinc(4 * x / tau_acf)**2

    def scipyFit(self,data):
        y = data[1] #todo this is fairly stupid! Need to calculate this properly (boundaries should be set until first 0 and a little bit further)
        x = data[0]

        self.__nearestIndex = self.find_first_index(y, 0)

        print(self.__nearestIndex[0][0])
        y = data[1][:self.__nearestIndex[0][0]+100]#todo this is fairly stupid! Need to calculate this properly (boundaries should be set until first 0 and a little bit further)
        x = data[0][:self.__nearestIndex[0][0]+100]

        print("Nearest index is '"+str(self.__nearestIndex)+"'")
        print("x-Value is '"+str(x[self.__nearestIndex]*24*60))
        print("y-Value is '"+str(x[self.__nearestIndex])+"'")

        initA = np.amax(y)
        initTau_acf = x[self.__nearestIndex[0]]
        arr = [initA, initTau_acf]

        bounds = ([initA - 0.1, initTau_acf - 0.05]
                  , [initA + 0.1, initTau_acf + 0.05])

        popt, pcov = optimize.curve_fit(self.sinc, x, y, p0=arr, bounds=bounds)
        perr = np.sqrt(np.diag(pcov))
        print("a = '" + str(popt[0]) + " (" + str(perr[0]) + ")'")
        print("tau_acf = '" + str(popt[1]) + " (" + str(perr[1]) + ")'")
        print(perr)

        return popt

    def find_first_index(self, array, value):
        delta = 0.01

        for i in array:
            if i < delta:
                return np.where(array==i)

    def setParameters(self,lightCurve,powerSpectra):
        if len(lightCurve) != 2 or len(powerSpectra) != 2:
            print("Lightcurve and Powerspectra need to be of dimension 2")
            print("Lightcurve dimension: '"+str(len(lightCurve))+"', Powerspectra dimension '"+str(len(powerSpectra))+"'")
            raise ValueError

        self.__lightCurve = lightCurve
        self.__powerSpectra = powerSpectra

        self.__calculateFlickerAmplitude()
        return self.__calculateInitFilterFrequency()

    def getInitNuFilter(self):
        return self.__initNuFilter

    def getNuFilterFitted(self):
        return self.__iterativeNuFilter

    def getFirstFilteredPSD(self):
        return self.__firstFilteredPSD

    def getSecondFilteredPSD(self):
        return self.__secondFilteredPSD

    def getNearestIndex(self):
        return self.__nearestIndex[0]

    def getPhotonNoise(self):
        return self.__photonNoise

