import numpy as np
from settings.settings import Settings
from support.strings import *
from scipy import signal
import logging

class PowerspectraCalculator:


    def __init__(self,lightCurve = None,powerSpectrum = None,kicID = ''):
        self.logger = logging.getLogger(__name__)
        self.lightCurve = lightCurve
        self.powerSpectrum = powerSpectrum
        self._nyq = 0
        self.kicID = kicID
        self._smoothedData = None

        self._powerSpectrumMode = Settings.Instance().getSetting(strCalcSettings, strSectPowerMode).value

        if self._lightCurve is not None and self.powerSpectrum is None:
            self.powerSpectrum = self.lightCurveToPowerspectra(self.lightCurve)

        self.photonNoise = np.mean(self.powerSpectrum[1][int(0.9*len(self.powerSpectrum[1])):len(self.powerSpectrum[1])-1])


    def lightCurveToPowerspectra(self,lightCurve):
        if len(lightCurve) != 2:
            self.logger.debug("Lightcurve should be of dimension 2!")
            raise ValueError

        if self._powerSpectrumMode == strPowerModeNumpy:
            return self._lightCurveToPowerspectraFFT(lightCurve)
        elif self._powerSpectrumMode == strPowerModeSciPy:
            return self._lightCurveToPowerspectraPeriodogramm(lightCurve)
        else:
            self.logger.debug("No available Mode named '"+self._powerSpectrumMode+"'")
            raise KeyError

    def lightCurveToPowerspectraFFT(self,lightCurve): #todo this doesn't seem to calculate it correctly!
        psd = np.fft.fft(lightCurve[1])
        psd = np.square(abs(psd))

        freq = np.fft.fftfreq(lightCurve[1].size,d=(lightCurve[0][3]-lightCurve[0][2])*24*3600)

        self.powerSpectrum = np.array((freq,psd))
        return self.powerSpectrum

    def lightCurveToPowerspectraPeriodogramm(self,lightCurve):
        fs = 1 / ((lightCurve[0][10] - lightCurve[0][9]) * 24 * 3600) #doesnt matter which timepoint is used.
        f, psd = signal.periodogram(lightCurve[1], fs,scaling='spectrum')
        f = f*10**6
        self.powerSpectrum = np.array((f,psd))
        return self.powerSpectrum

    def __butter_lowpass_filtfilt(self,data,order=5):
        normal_cutoff = 0.7 / self.nyq #TODO 0.7 is only empirical, maybe change this
        b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
        psd = data
        return signal.filtfilt(b, a,psd)

    @property
    def smoothedData(self):
        if self._smoothedData is None:
            self._smoothedData =self.__butter_lowpass_filtfilt(self.powerSpectrum[1])
        return self._smoothedData

    @property
    def nyqFreq(self):
        if self.lightCurve is not None:
            self.logger.debug(
                "Abtastfrequency is '" + str((self._lightCurve[0][3] - self._lightCurve[0][2]) * 24 * 3600) + "'")
            self._nyq = 10 ** 6 / (2 * (self._lightCurve[0][200] - self._lightCurve[0][199]))
            self.logger.debug("Nyquist frequency is '" + str(self._nyq) + "'")
        else:
            self.logger.error("LightCurve is None therfore no calculation of nyquist frequency possible")

        return self._nyq


    @property
    def lightCurve(self):
        if self._lightCurve is None:
            self.logger.warning("Lightcurve is None!")

        return self._lightCurve

    @lightCurve.setter
    def lightCurve(self,data):
        if data is None or len(data) == 2:
            self._lightCurve = data
        else:
            self.logger.error("Lightcurve should have 2 dimensions (time,flux)")
            raise ValueError
    @property
    def powerSpectrum(self):
        if self._powerSpectrum is None:
            self.logger.warning("Powerspectra is None!")

        return np.array((self._powerSpectrum[0][1:], self._powerSpectrum[1][1:]))

    @powerSpectrum.setter
    def powerSpectrum(self,data):
        if data is None or len(data) == 2:
            self._powerSpectrum = data
        else:
            self.logger.error("Powerspectra should have 2 dimesions (frequency,power)")
            raise ValueError

    @property
    def photonNoise(self):
        return self._photonNoise

    @photonNoise.setter
    def photonNoise(self,value):
        self._photonNoise = value
        
    @property
    def kicID(self):
        return self._kicID

    @kicID.setter
    def kicID(self,value):
        self._kicID = value

