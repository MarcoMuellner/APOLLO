import numpy as np
from settings.settings import Settings
from support.strings import *
from scipy import signal
import logging

class PowerspectraCalculator:

    def __init__(self,lightCurve = None,powerSpectra = None,kicID = ''):
        self.logger = logging.getLogger(__name__)
        self.setLightCurve(lightCurve)
        self.setPowerspectra(powerSpectra)
        self.setKicID(kicID)
        self.powerSpectraMode = Settings.Instance().getSetting(strCalcSettings, strSectPowerMode).value

        if self.lightCurve is not None and self.powerSpectra is None:
            self.setPowerspectra(self.lightCurveToPowerspectra(self.lightCurve))
        elif self.powerSpectra is not None and self.lightCurve is None:
            self.setLightCurve(self.powerspectraToLightcurve(self.powerSpectra))

        self.photonNoise = np.mean(self.getPSD()[1][int(0.9*len(self.getPSD()[1])):len(self.getPSD()[1])-1])

        self.getNyquistFrequency()

    def lightCurveToPowerspectra(self,lightCurve):
        if len(lightCurve) != 2:
            self.logger.debug("Lightcurve should be of dimension 2!")
            raise ValueError

        if self.powerSpectraMode == strPowerModeNumpy:
            return self.lightCurveToPowerspectraFFT(lightCurve)
        elif self.powerSpectraMode == strPowerModeSciPy:
            return self.lightCurveToPowerspectraPeriodogramm(lightCurve)
        else:
            self.logger.debug("No available Mode named '"+self.powerSpectraMode+"'")
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
        normal_cutoff = cutoff / self.nyq
        b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def getLightCurve(self):
        if self.lightCurve is None:
            self.logger.debug("Lightcurve is None!")

        return self.lightCurve

    def getPSD(self):
        if self.powerSpectra is None:
            self.logger.debug("Powerspectra is None!")

        return np.array((self.powerSpectra[0][1:],self.powerSpectra[1][1:]))

    def getSmoothing(self):
        return self.__butter_lowpass_filtfilt(self.powerSpectra[1])

    def getKicID(self):
        return self.kicID

    def setLightCurve(self,lightCurve):
        if lightCurve is None or len(lightCurve) == 2:
            self.lightCurve = lightCurve
        else:
            self.logger.debug("Lightcurve should have 2 dimensions (time,flux)")
            raise ValueError
        return self.lightCurve

    def setPowerspectra(self,powerSpectra):
        if powerSpectra is None or len(powerSpectra) == 2:
            self.powerSpectra = powerSpectra
        else:
            self.logger.debug("Powerspectra should have 2 dimesions (frequency,power)")
            raise ValueError
        return self.powerSpectra

    def setKicID(self,kicID):
        self.kicID = kicID

    def getNyquistFrequency(self):
        if self.lightCurve is not None:
            self.logger.debug("Abtastfrequency is '"+str((self.lightCurve[0][3] - self.lightCurve[0][2])*24*3600)+"'")
            self.nyq = 10**6/(2*(self.lightCurve[0][200] -self.lightCurve[0][199]))
            self.logger.debug("Nyquist frequency is '"+str(self.nyq)+"'")

            return self.nyq
        else:
            self.logger.debug("Lightcurve is None, therefore no calculation of nyquist frequency possible")
            return None
    def getPhotonNoise(self):
        return self.photonNoise
