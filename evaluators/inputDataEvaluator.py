import logging

import numpy as np
from scipy import signal
from plotnine import *

from res.strings import *
from settings.settings import Settings
from fitter.fitFunctions import *
from plotter.plotFunctions import *


class InputDataEvaluator:
    '''
    The PowerspectraCalculator represents the basic information about a LightCurve. Provided a lightCurve it will
    calculate its PSD using FFT, its Nyquist frequency, photonNoise and some smoothing of the PSD.
    This class is also used in various other places, like different plotters, which will extract the necessary
    information automatically. After reading a lightCurve from a file this should be your first point of entry.

    There are some pitfalls that may occur when using this class though. These are:
    - If you set a lightCurve and a powerSpectralDensity at initialization of the object, another set of the lightCurve
    will not overwrite the powerSpectralDensity
    - If you only set a powerSpectralDensity either at initialization or later via assigning to powerSpectralDensity it
    will not calculate the lightCurve from it, as we are working with a squared version of the PSD and an inverse
    function is not really feasible.
    - A change of the kicID will not result in a recomputation of the powerSpectralDensity when the lightCurve is set
    '''


    def __init__(self, lightCurve = None, powerSpectralDensity = None, kicID =''):
        '''
        The constructor of the lightCurve. All parameters are optional and can be set on a later point in the code, not
        necessarily at runtime. Computes the PSD automatically when only a lightCurve is provided.
        :param lightCurve: Represents the lightCurve. 1st Axis represents temporal axis in days, 2nd axis represents
        flux of lightCurve
        :type lightCurve:2-D numpy array
        :param powerSpectralDensity: Represents the PSD of a lightCurve. 1st axis represents frequency, 2nd axis
        represents ppm^2
        :type powerSpectralDensity:2-D numpy array
        :param kicID:The name of the input dataset
        :type kicID:string
        '''
        self.logger = logging.getLogger(__name__)
        self.photonNoise = None
        self.lightCurve = lightCurve
        self.powerSpectralDensity = powerSpectralDensity
        self.kicID = kicID
        self._smoothedData = None

        self._powerSpectrumMode = Settings.Instance().getSetting(strCalcSettings, strSectPowerMode).value

        if self.lightCurve is not None and self.powerSpectralDensity is None:
            self.powerSpectralDensity = self.lightCurveToPowerspectra(self.lightCurve)
        elif self.lightCurve is None and self.powerSpectralDensity is not None:
            self.logger.warning("Cannot create Lightcurve from PSD alone")

        self._nyq = None


    def lightCurveToPowerspectra(self,lightCurve):
        '''
        Wrapper function that contains the different possibilities to compute the PSD. This can also be used externally,
        no class members are set within this method. It is recommended to use the SciPy method for computing the PSD.
        :param lightCurve: Represents a lightCurve. 1st axis -> temporal axis in days, 2nd axis -> flux
        :type lightCurve:2-D numpy array
        :return:The PSD computed accordingly to the settings. 1st axis -> frequency in uHz, 2nd axis -> ppm^2
        :rtype:2-D numpy array
        '''
        if len(lightCurve) != 2 or not isinstance(lightCurve,np.ndarray):
            self.logger.error("Lightcurve should be of dimension 2 and ndarray!")
            raise ValueError("Type is "+str(type(lightCurve)))

        if self._powerSpectrumMode == strPowerModeNumpy:
            return self.lightCurveToPowerspectraFFT(lightCurve)
        elif self._powerSpectrumMode == strPowerModeSciPy:
            return self.lightCurveToPowerspectraPeriodogramm(lightCurve)
        else:
            self.logger.error("No available Mode named '"+self._powerSpectrumMode+"'")
            raise KeyError

    def lightCurveToPowerspectraFFT(self,lightCurve):
        '''
        Numpy method of computing the PSD. Uses a pure fast fourier transformation to compute the signal.
        :param lightCurve: Represents a lightCurve. 1st axis -> temporal axis in days, 2nd axis -> flux
        :type lightCurve: 2-D numpy array
        :return: Returns the PSD using a fft method provided by numpy
        :rtype: 2-D numpy array
        '''
        psd = np.fft.fft(lightCurve[1])
        psd = np.square(abs(psd))

        freq = np.fft.fftfreq(lightCurve[1].size,d=(lightCurve[0][3]-lightCurve[0][2])*24*3600)

        return np.array((freq,psd))

    def lightCurveToPowerspectraPeriodogramm(self,lightCurve):
        '''
        Scipy method of computing the PSD. It computes a real PSD directly when provided data in the time domain.
        :param lightCurve: Represents a lightCurve. 1st axis -> temporal axis in days, 2nd axis -> flux
        :type lightCurve: 2-D numpy array
        :return: Returns the PSD using a fft method provided by numpy
        :rtype: 2-D numpy array
        '''
        fs = 1 / ((lightCurve[0][10] - lightCurve[0][9]) * 24 * 3600) #doesnt matter which timepoint is used.
        f, psd = signal.periodogram(lightCurve[1], fs,scaling='density')
        f = f*10**6
        psd = np.divide(psd[1:],10**6)

        f = f[1:]
        if Settings.Instance().getSetting(strDataSettings,strSectStarType).value == strStarTypeYoungStar:
            psd = psd[f > 30]
            f = f[f > 30]
        return np.array((f,psd))

    def __butter_lowpass_filtfilt(self,data,order=5):
        '''
        Internal method of smoothing a dataset. Uses a butterworth filter to filter out fast variations in the signal
        of the PSD.
        :param data:Dataset that should be filtered. Both time domain, and PSDs can be provided, although the filter is
        calibrated only for a PSD
        :type data:1-D numpy array
        :param order:Reactiveness of the filter. Optional
        :type order:int
        :return:Returns a smoothed variant of the input dataset
        :rtype:1-D numpy array
        '''
        normal_cutoff = 0.5 / self.nyqFreq #TODO 0.7 is only empirical, maybe change this
        b, a = signal.butter(5, normal_cutoff, btype='low', analog=False)
        return signal.filtfilt(b, a,data)

    @property
    def smoothedData(self):
        '''
        Property of the smoothed PSD. Will calculate it when used for the first time.
        :return:The smoothed variant of the 2nd axis of the PSD
        :rtype:1-D numpy array
        '''
        if self._smoothedData is None:
            self._smoothedData =self.__butter_lowpass_filtfilt(self.powerSpectralDensity[1])
        return self._smoothedData

    @property
    def nyqFreq(self):
        '''
        The property of the nyquist frequency of the lightCurve when such was provided.
        Will calculate it when used for the first time
        :return: The nyquist frequency
        :rtype: float
        '''
        if self.lightCurve is not None and self._nyq is None:
            self.logger.debug(
                "Abtastfrequency is '" + str((self._lightCurve[0][3] - self._lightCurve[0][2]) * 24 * 3600) + "'")
            self._nyq = 10 ** 6 / (2 * (self._lightCurve[0][200] - self._lightCurve[0][199])*3600*24)
            self.logger.info("Nyquist frequency is '" + str(self._nyq) + "'")
        elif self.lightCurve is None:
            self.logger.error("LightCurve is None therfore no calculation of nyquist frequency possible")
            raise ValueError

        return self._nyq


    @property
    def lightCurve(self):
        '''
        The property of the lightCurve. This can be none, if none was provided during initialization or by setting it.
        :return: The lightCurve. 1st axis -> temporal axis, 2nd axis -> flux
        :rtype: 2-D numpy array
        '''
        if self._lightCurve is None:
            self.logger.warning("Lightcurve is None!")

        return self._lightCurve

    @lightCurve.setter
    def lightCurve(self,data):
        '''
        Setter property for the lightCurve. Will compute the PSD if it was not set up to this point.
        :param data: LightCurve for the class. 1st axis -> temporal axis in days, 2nd axis -> flux
        :type data: 2-D numpy array
        '''
        if data is None or (len(data) == 2 and isinstance(data,np.ndarray)):
            self._lightCurve = data
            try:
                if self.powerSpectralDensity is None:
                    self.powerSpectralDensity = self.lightCurveToPowerspectra(data)
            except AttributeError:
                self.logger.debug("Powerspectrum has not been set yet, skipping")
        else:
            self.logger.error("Lightcurve should have 2 dimensions (time,flux) and should be a numpy array")
            raise TypeError("Type is "+str(type(data)))
    @property
    def powerSpectralDensity(self):
        '''
        Property for the PSD
        :return: Returns the PSD. 1st axis -> frequency in uHz, 2nd axis -> ppm^2
        :rtype: 2-D numpy array
        '''
        if self._powerSpectrum is None:
            self.logger.warning("Powerspectra is None!")
            return self._powerSpectrum

        return self._powerSpectrum

    @powerSpectralDensity.setter
    def powerSpectralDensity(self, data):
        '''
        Setter proprty for the PSD. Will overwrite any computationally determined PSD set to the class up to this point
        :param data: PSD for the class. 1st axis -> frequency in uHz, 2nd axis -> ppm^2
        :type data: 2-D numpy array
        '''
        if data is None or (len(data) == 2 and isinstance(data,np.ndarray)):
            self._powerSpectrum = data
        else:
            self.logger.error("Powerspectra should have 2 dimensions (frequency,power) and should be a numpy array")
            raise TypeError("Type is "+str(type(data)))

    @property
    def photonNoise(self):
        '''
        Property for the photon noise. Will compute it when used for the first time but only if a PSD is set inside the
        class. This can be achieved using the lightCurve setter function if no PSD was directly set, through
        initialization or by directly setting the PSD.

        Computation occurs by computing the mean of the last 10% of the data of the PSD. This value is only an
        approximation, to compute it properly you need to fit the PSD.
        :return: The approximation of the photonNoise of the PSD
        :rtype: float
        '''
        if self._photonNoise == None and self.powerSpectralDensity is not None:
            bins = np.linspace(np.amin(self.powerSpectralDensity), np.amax(self.powerSpectralDensity),
                               int((np.amax(self.powerSpectralDensity) - np.amin(self.powerSpectralDensity)) / 20))
            hist = np.histogram(self.powerSpectralDensity, bins=bins)[0]
            bins = bins[0:len(bins) - 1]

            p0 = [0, hist[0], 0]
            boundaries = ([- 0.1, -np.inf, -np.inf], [+ 0.1, np.inf, np.inf])

            popt, __ = scipyFit(bins, hist, exponentialDistribution, p0, boundaries)
            self.photonNoise = 1/popt[2]

            self.logger.info("Expected value for photon noise is " + str(1 / popt[2]))

            lin = np.linspace(np.min(bins), np.max(bins), len(bins) * 100)
            histogramPlotData = {"Histogramm": (np.array((bins, hist)), geom_line, 'solid'),
                                 "Initial Fit": (np.array((lin, exponentialDistribution(lin, *p0))), geom_line, 'solid'),
                                 "Fit": (np.array((lin, exponentialDistribution(lin, *popt))), geom_line, 'solid'),
                                 "Photon Noise": (np.array(([self.photonNoise])), geom_vline, 'dashed')}

            plotCustom(self.kicID, self.kicID + "_psd_histogramm", histogramPlotData
                       , "bins", "counts", self.kicID + "_psd_histogramm", 5)

        return self._photonNoise

    @photonNoise.setter
    def photonNoise(self,value):
        '''
        Setter property for the photon noise. You can set the correct value here after fitting if you so desire.
        :param value: The value on which the photonNoise should be set
        :type value: float
        '''
        self._photonNoise = value
        
    @property
    def kicID(self):
        '''
        Property of the KICId
        :return: KICId of the star
        :rtype: string
        '''
        return self._kicID

    @kicID.setter
    def kicID(self,value):
        '''
        Setter Property of the KICId
        :param value: KICId of the star
        :type value: string
        '''
        self._kicID = value

