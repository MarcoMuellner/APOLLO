import numpy as np
from settings.settings import Settings
from support.strings import *
from scipy import signal

class PowerspectraCalculator:

    def __init__(self,lightCurve = None,powerSpectra = None,kicID = ''):
        self.setLightCurve(lightCurve)
        self.setPowerspectra(powerSpectra)
        self.setKicID(kicID)
        self.__powerSpectraMode = Settings.Instance().getSetting(strCalcSettings, strSectPowerMode).value

        if self.__lightCurve is not None and self.__powerSpectra is None:
            self.setPowerspectra(self.lightCurveToPowerspectra(self.__lightCurve))
        elif self.__powerSpectra is not None and self.__lightCurve is None:
            self.setLightCurve(self.powerspectraToLightcurve(self.__powerSpectra))

        self.getNyquistFrequency()

    def lightCurveToPowerspectra(self,lightCurve):
        if len(lightCurve) != 2:
            print("Lightcurve should be of dimension 2!")
            raise ValueError

        if self.__powerSpectraMode == strPowerModeNumpy:
            return self.lightCurveToPowerspectraFFT(lightCurve)
        elif self.__powerSpectraMode == strPowerModeSciPy:
            return self.lightCurveToPowerspectraPeriodogramm(lightCurve)
        else:
            print("No available Mode named '"+self.__powerSpectraMode+"'")
            raise KeyError

    def lightCurveToPowerspectraFFT(self,lightCurve): #todo this doesn't seem to calculate it correctly!
        psd = np.fft.fft(lightCurve[1])
        psd = np.square(abs(psd))

        freq = np.fft.fftfreq(lightCurve[1].size,d=(lightCurve[0][3]-lightCurve[0][2])*24*3600)

        self.setPowerspectra(np.array((freq,psd)))
        return self.getPowerspectra()

    def lightCurveToPowerspectraPeriodogramm(self,lightCurve):
        fs = 1 / ((lightCurve[0][10] - lightCurve[0][9]) * 24 * 3600) #doesnt matter which timepoint is used.
        f, psd = signal.periodogram(lightCurve[1], fs,scaling='spectrum')
        f = f*10**6
        self.setPowerspectra(np.array((f,psd)))
        return self.getPSD()


    def powerspectraToLightcurve(self,powerSpectra): #todo
        return

    def __butter_lowpass_filtfilt(self,data,order=5):
        b, a = self.__butter_lowpass(0.7, order=order) # todo 0.7 is just empirical, this may work better with something else?
        psd = data
        self.m_smoothedData = signal.filtfilt(b, a,psd)
        return self.m_smoothedData

    def __butter_lowpass(self,cutoff, order=5):#todo these should be reworked and understood properly!
        normal_cutoff = cutoff / self.__nyq
        b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def getLightcurve(self):
        if self.__lightCurve is None:
            print("Lightcurve is None!")

        return self.__lightCurve

    def getPSD(self):
        if self.__powerSpectra is None:
            print("Powerspectra is None!")

        return np.array((self.__powerSpectra[0][1:],self.__powerSpectra[1][1:]))

    def getSmoothing(self):
        return self.__butter_lowpass_filtfilt(self.__powerSpectra[1])

    def getKicID(self):
        return self.__kicID

    def setLightCurve(self,lightCurve):
        if lightCurve is None or len(lightCurve) == 2:
            self.__lightCurve = lightCurve
        else:
            print("Lightcurve should have 2 dimensions (time,flux)")
            raise ValueError
        return self.__lightCurve

    def setPowerspectra(self,powerSpectra):
        if powerSpectra is None or len(powerSpectra) == 2:
            self.__powerSpectra = powerSpectra
        else:
            print("Powerspectra should have 2 dimesions (frequency,power)")
            raise ValueError
        return self.__powerSpectra

    def setKicID(self,kicID):
        self.__kicID = kicID

    def getNyquistFrequency(self):
        if self.__lightCurve is not None:
            self.__nyq = 2 * np.pi * self.__lightCurve[0].size / (2 * (self.__lightCurve[0][3] - self.__lightCurve[0][2]) * 24 * 3600)
            return self.__nyq
        else:
            print("Lightcure is None, therefore no calculation of nyquist frequency possible")
            return None
