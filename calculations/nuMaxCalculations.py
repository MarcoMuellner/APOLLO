import numpy as np
from math import log10,log,exp
import time as t
from scipy.signal import butter, filtfilt
from scipy import optimize
from calculations.powerspectraCalculations import PowerspectraCalculator
from plotter.plotFunctions import *
import pylab as pl
import logging

class NuMaxCalculator:
    def __init__(self,lightCurve,powerSpectra):
        self.logger = logging.getLogger(__name__)
        self.__iterativeNuFilter = None
        self.setParameters(lightCurve,powerSpectra)
        return
    def __calculateFlickerAmplitude(self):
        #calculate Median Flux
        time = self.__lightCurve[0]
        #np.set_self.logger.debugoptions(threshold=np.inf)
        maxdif = 0
        mindif = 1000
        for i in (0,len(time)):
            try:
                if time[i+1] - time[i] > maxdif:
                    maxdif = time[i+1] - time[i]
                if time[i+1] - time[i] < mindif:
                    mindif = time[i+1] - time[i]
            except:
                self.logger.debug("endofloop")

        self.logger.debug("Max diff is '"+str(maxdif)+"'")
        self.logger.debug("Min diff is '" + str(mindif) + "'")
        #self.logger.debug(time)
        flux = self.__lightCurve[1]

        medianFlux = np.median(flux)
        meanTimeBin = np.amax(time)/len(time)
        if meanTimeBin <10**-3:
            flickerSize = 5/24 # size of flickertime. This is calibrated by Kallinger. Measured in days
        else:
            flickerSize = 4

        binSize = int(flickerSize/meanTimeBin) #calculate the binsize of one flicker!
        iterations = len(time)/binSize #The number of iterations needed to calculate all single Amplitudes

        cutoffMax = 0 #These two parameters define the cutoff of things in the lightcurve you probably don't want
        cutoffMin = 0

        self.logger.debug("Max Time is '"+str(np.amax(time))+"'")
        self.logger.debug("Length of time is '"+str(len(time)))
        self.logger.debug("Flickersize is '"+str(flickerSize)+"'")
        self.logger.debug("MeanTimeBin is '"+str(meanTimeBin)+"'")
        self.logger.debug("Iterations is '"+str(iterations)+"'")


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
            filteredFlux[multiplicator*binSize:(multiplicator+1)*binSize] = flux[multiplicator*binSize:(multiplicator+1)*binSize] - np.mean(fluxBin)

        #this is the final flickerAmplitude!
        self.__flickerAmplitude = np.std(filteredFlux)
        self.logger.debug("Calculated flicker amplitude is '"+str(self.__flickerAmplitude)+"'")

    def getNyquistFrequency(self):
        if self.__lightCurve is not None:
            self.logger.debug("Abtastfrequency is '"+str((self.__lightCurve[0][3] - self.__lightCurve[0][2])*24*3600)+"'")
            self.logger.debug("Size is '"+str(self.__lightCurve[0].size)+"'")
            self.__nyq = 2 * np.pi * self.__lightCurve[0].size / (2 * (self.__lightCurve[0][3] - self.__lightCurve[0][2]) * 24 * 3600)
            #TODO set fix here, see what it does
            #self.__nyq = 283.2116656017908


            return self.__nyq
        else:
            self.logger.debug("Lightcurve is None, therefore no calculation of nyquist frequency possible")
            return None

    def __calculateInitFilterFrequency(self):
        self.__initNuFilter = 10**(5.187-1.560*log10(self.__flickerAmplitude))
        self.logger.debug("Initial Nu Filter is '"+str(self.__initNuFilter)+"'")
        return self.__initNuFilter

    def calculateIterativeFilterFrequency(self):
        filterFrequency = self.__iterativeNuFilter if self.__iterativeNuFilter is not None else self.__initNuFilter
        smoothed = self.butter_lowpass_filtfilt(self.__lightCurve[1], filterFrequency, self.getNyquistFrequency())

        corr = self.calculateAutocorrelation(smoothed) #todo this seems to be a bottleneck here...
        corrTest = self.calculateAutocorrelation(self.__lightCurve[1])       

        stepFreq = self.__lightCurve[0][10] - self.__lightCurve[0][9]
        deltaF = np.zeros(len(corrTest))
        for i in range(0, len(deltaF)):
            deltaF[i] = i * stepFreq

        pl.plot(deltaF,corrTest,label='ACF^2')
        pl.ylim(-0.5,1)
        pl.xlim(0,1)
        pl.legend()

        corr = np.power(corr,2)
        stepFreq = self.__lightCurve[0][10] - self.__lightCurve[0][9]
        deltaF = np.zeros(len(corr))
        for i in range(0, len(deltaF)):
            deltaF[i] = i * stepFreq
        pl.figure()
        pl.plot(deltaF,corr,label='ACF^2')
        pl.ylim(-0.5,1)
        pl.xlim(0,1)
        pl.legend()
        pl.show()
        
        best_fit = self.scipyFit(np.array((deltaF, corr)))
        tauACF = best_fit[2]*24*60

        self.logger.debug("Tau_ACF is '"+str(tauACF)+"'")

        self.__iterativeNuFilter = 10**(3.098-0.932*log10(tauACF)-0.025*log10(tauACF)**2)
        self.__photonNoise = np.mean(self.__powerSpectra[1])*(1-best_fit[0]) if best_fit[0] < 1 else np.mean(self.__powerSpectra[1])
        self.logger.debug("Second iterative filter is '"+str(self.__iterativeNuFilter)+"'")
        self.logger.debug("Photon noise is '"+str(self.__photonNoise))
        return np.array((deltaF,corr)),best_fit

    def butter_lowpass_filtfilt(self,data, f, nyq, order=5):
        b, a = self.butter_lowpass(f, nyq, order=order)
        self.logger.debug("Filterparameter are "+str(b)+","+str(a))
        y = filtfilt(b, a, data)
        self.logger.debug("Final frequency is "+str(y))
        return y

    def butter_lowpass(self,cutoff, nyq, order=5):
        normal_cutoff = cutoff / nyq
        self.logger.debug("Cutoff Frequency for filtering is '"+str(normal_cutoff)+"'")
        self.logger.debug("Nyquist Frequency is '"+str(nyq)+"'")
        self.logger.debug("Input Cutoff is '"+str(cutoff)+"'")
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        return b, a

    def calculateAutocorrelation(self,oscillatingData):
        #this here is the actual correlation -> rest is just to crop down to
        #significant areas
        corrs2 = np.correlate(oscillatingData, oscillatingData, mode='same')
        #
        N = len(corrs2)
        corrs2 = corrs2[N // 2:]
        lengths = range(N, N // 2, -1)
        corrs2 /= lengths
        corrs2 /= corrs2[0]
        maxcorr = np.argmax(corrs2)
        corrs2 = corrs2 / corrs2[maxcorr]
        return corrs2

    def sinc(self,x, a,b, tau_acf):
        return a * np.sinc(4 * x / tau_acf)**2+b*np.sin(2*np.pi*x/tau_acf)

    def scipyFit(self,data):
        y = data[1] #todo this is fairly stupid! Need to calculate this properly (boundaries should be set until first 0 and a little bit further)
        x = data[0]

        self.__nearestIndex = self.find_first_index(y, 0)

        self.logger.debug(self.__nearestIndex[0][0])
        y = data[1][:self.__nearestIndex[0][0]+100]#todo this is fairly stupid! Need to calculate this properly (boundaries should be set until first 0 and a little bit further)
        x = data[0][:self.__nearestIndex[0][0]+100]

        self.logger.debug("Nearest index is '"+str(self.__nearestIndex)+"'")
        self.logger.debug("x-Value is '"+str(x[self.__nearestIndex]*24*60))
        self.logger.debug("y-Value is '"+str(x[self.__nearestIndex])+"'")

        initA = np.amax(y)
        initTau_acf = x[self.__nearestIndex[0]]
        initB = initA/20
        arr = [initA,initB, initTau_acf]

        bounds = ([initA - 0.1,initB/2, initTau_acf - 0.05]
                  , [initA + 0.1,initB*2, initTau_acf + 0.05])

        popt, pcov = optimize.curve_fit(self.sinc, x, y, p0=arr, bounds=bounds)
        perr = np.sqrt(np.diag(pcov))
        self.logger.debug("a = '" + str(popt[0]) + " (" + str(perr[0]) + ")'")
        self.logger.debug("b = '"+str(popt[1])+" ("+str(perr[1])+")'")
        self.logger.debug("tau_acf = '" + str(popt[2]) + " (" + str(perr[2]) + ")'")
        self.logger.debug(perr)

        return popt

    def find_first_index(self, array, value):
        delta = 0.01

        for i in array:
            if i < delta:
                return np.where(array==i)

    def setParameters(self,lightCurve,powerSpectra):
        if len(lightCurve) != 2 or len(powerSpectra) != 2:
            self.logger.debug("Lightcurve and Powerspectra need to be of dimension 2")
            self.logger.debug("Lightcurve dimension: '"+str(len(lightCurve))+"', Powerspectra dimension '"+str(len(powerSpectra))+"'")
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

