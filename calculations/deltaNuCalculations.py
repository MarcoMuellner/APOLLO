import numpy as np
from scipy import optimize
from scipy.signal import butter, filtfilt
import logging
from uncertainties import ufloat


class DeltaNuCalculator:
    """
    This class can fit Delta Nu given a fitted PSD. See Kjeldsen and Bedding (1995) for further information on Delta Nu.
    """

    def __init__(self, nuMax, sigma, psd, nyq, backGroundParameters, backGroundModel):
        """
        Constructor of the DeltaNuCalculator. Uses the parameters given as an input and performs an initial fit of these
        parameters. As a prequisit, a PSD where fitting was already done has to be provided. You need the full set of
        backgroundParameters as well as the backgroundModel
        :param nuMax:Frequency of maximum power. See Belkacem,Moser (2013)
        :type nuMax:float
        :param sigma:The standard deviation of the power excess in the fitted spectrum
        :type sigma:float
        :param psd:The Powerspectraldensity in uHz nad ppm
        :type psd:2-D numpy array
        :param nyq:The Nyquist frequency of the data
        :type nyq:float
        :param backGroundParameters:The background parameters provided by DIAMONDS. This probably needs to be adapted in
        case of a different Nested Sampling tool
        :type backGroundParameters:3-D numpy array
        :param backGroundModel:The computed background model containing all 9 parameters in the Fit
        :type backGroundModel:9-D numpy array
        """
        self._multiplicator = 2
        self._nuMax = nuMax
        self._sigma = sigma
        self._psd = psd
        self._backgroundModel = backGroundModel
        self._backgroundParameters = backGroundParameters
        self._nyq = nyq
        self.logger = logging.getLogger(__name__)

        self.calculateFit()

    def calculateFit(self):
        """
        Calculates the fit for the input parameters in the class. It will firstly divide the Data by its background,
        calls _calculateAutocorrelation to get the Autocorrelation of the oscillating area,
        compute an estimation using _estimateDeltaNu() and finally fit the data. This method is called within the
        constructor, so another call is only needed if one parameter
        is changed
        """
        background = np.sum(self._backgroundModel[0:4], axis=0)

        # Divide raw Spectrum by background
        clearedData = np.divide(self._psd[1], background)

        par_median, par_le, par_ue = self._backgroundParameters
        minima, maxima, indexMin, indexMax = self._findGaussBoundaries(self._multiplicator)  # get Boundaries of Gauss, 2-3 Sigma is recommended

        # Estimate Delta Nu from numax
        self._deltaNuEst = self._estimateDeltaNu()

        # smooth data
        clearedData = self._butter_lowpass_filtfilt(clearedData, self._nyq, self._deltaNuEst * 10)
        oscillatingData = np.vstack((self._psd[0][indexMin:indexMax], clearedData[indexMin:indexMax]))

        # calculate autocorrelation
        self._corrs = self._calculateAutocorrelation(oscillatingData)

        # Calculate stepsize and x-Axis for Autocorrelation
        stepFreq = self._psd[0][2] - self._psd[0][1]
        self._deltaF = np.zeros(len(self._corrs))
        for i in range(0, len(self._deltaF)):
            self._deltaF[i] = i * stepFreq

        self._corrs = self._butter_lowpass_filtfilt(self._corrs, self._nyq, 30 * abs(np.log10(self._deltaNuEst)))#Calculation of cutoff frequency purely on gueswork

        # calculate Fit
        self._scipyFit(np.array((self._deltaF, self._corrs)), self._deltaNuEst)

    def _findGaussBoundaries(self, data = None, cen = None, sigma = None):
        """
        Convinience function. Finds the boundaries of a gaussian within a certain dataset. Both used for the fitting and
        the initial restriction of the data.
        :param data:The dataset where one would find a gauss like peak
        :type data:2-D numpy array
        :param cen:The maxima of the peak which should be fitted
        :type cen:float
        :param sigma:The standard deviation of the gaussian
        :type sigma:float
        :return:Four values representing the minima and maxima and its corresponding indizes in the data
        :rtype:4-D tuple
        """
        minima = 0
        maxima = 0
        deltaMinima = 1000
        deltaMaxima = 1000
        indexMin = 0
        indexMax = 0
        #changing none to members if needed
        psd = data if data is not None else self._psd
        cen = cen if cen is not None else self._nuMax
        sigma = sigma if sigma is not None else self._sigma

        #iterating through the dataset
        for i in range(0, len(psd[0]) - 1):
            if (abs(psd[0][i] - (cen - self._multiplicator*sigma)) < deltaMinima):
                deltaMinima = abs(psd[0][i] - (cen  - self._multiplicator*sigma))
                minima = psd[0][i]
                indexMin = i

            if (abs(psd[0][i] - (cen  + self._multiplicator*sigma)) < deltaMaxima):
                deltaMaxima = abs(psd[0][i] - (cen  + self._multiplicator*sigma))
                maxima = psd[0][i]
                indexMax = i

        self.logger.info("Final minima: '" + str(minima) + "', final maxima: '" + str(maxima) + "', numax: '"
              + str(cen ) + "', sigma: '" + str(sigma) + "'")

        self._gaussBoundaries = (minima, maxima, indexMin, indexMax)
        return self._gaussBoundaries

    def _butter_lowpass_filtfilt(self, data, nyq, level, order=5):
        """
        Smoothing function to make the fitting easier. Filters out high frequencies of the signal.
        The the butter function in scipy.signal
        :param data:The autocorrelated dataset from the initial PSD
        :type data:2-D numpy array
        :param nyq:The nyquist frequency of the data
        :type nyq:float
        :param level:The cutoff frequency which should be filtered
        :type level:float
        :param order:Order of the filter. Defines the "steepness". Probably not necessary to adapt
        :type order:int
        :return:The y-axis of the dataset. This data is filtered using the frequencies.
        :rtype:1-D numpy array
        """
        normal_cutoff = level / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        y = filtfilt(b, a, data)
        return y

    def _calculateAutocorrelation(self):
        """
        Restricts the data to the oscillating part and calculates the autoorrelation
        :return:y-Axis of the Autocorrelated data
        :rtype:1-D numpy array
        """
        psd = self._psd
        backgroundModel = self._backgroundModel
        background = np.sum(backgroundModel[0:4],axis=0)
        clearedData = np.divide(psd[1], background)

        oscillatingData = np.vstack((psd[0][self._gaussBoundaries[2]:self._gaussBoundaries[3]],
                                     clearedData[self._gaussBoundaries[2]:self._gaussBoundaries[3]]))


        corrs2 = np.correlate(oscillatingData[1], oscillatingData[1], mode='full')
        N = len(corrs2)
        self._corrs = corrs2[N // 2:]
        lengths = range(N, N // 2, -1)
        self._corrs /= lengths
        self._corrs /= corrs2[0]
        return self._corrs

    def _estimateDeltaNu(self, nuMax = None):
        """
        Gives an estimation of deltaNu using an empirical relation by Stello et al. (2009)
        :param nuMax: The frequency of maximum oscillation in the PSD
        :type nuMax:float
        :return:An estimation of where Delta nu should be.
        :rtype:float
        """
        nuMax = nuMax if nuMax is not None else self._nuMax
        self._deltaNuEst = 0.263 * pow(nuMax, 0.772)
        return self._deltaNuEst

    def gaussian(self,x, y0, amp, cen, wid):
        """
        Fitting function used. Fits a Gaussian using the following function:
        .. math::
            y(x)=y_0+\frac{amp}{\sqrt{2\pi wid}}\text{exp}(-\frac{(x-cen)^2}{2*wid^2})
        :param x:x-Axis against which we will approximate the function
        :type x:1-D numpy array
        :param y0:y-Offset of the function
        :type y0:float
        :param amp:Amplitude of the gaussian
        :type amp:float
        :param cen:x-Value of center of distribution
        :type cen:float
        :param wid:Standard deviation of the distribution
        :type wid:float
        :return:y-Array of a gaussian distribution
        :rtype:1-D numpy array
        """
        return y0 + (amp / (np.sqrt(2 * np.pi) * wid)) * np.exp(-(x - cen) ** 2 / (2 * wid ** 2))

    def _scipyFit(self, data, deltaNuEst):
        """
        Performs the fit of the gaussian in the autocorrelated dataset
        :param data: The dataset which should be fitted
        :type data: 1-D numpy array
        :param deltaNuEst:A first approximation, probably gained through _estimateDeltaNu()
        :type deltaNuEst:float
        :return:Fitting parameters including errors. First parameter is y0, second amplitude, third center, fourth
        standard deviation
        :rtype:List containing 4 parameters
        """
        y = data[1]
        x = data[0]
        minima, maxima, indexMin, indexMax = self._findGaussBoundaries(self._multiplicator, data, deltaNuEst, 0.2 * deltaNuEst)
        self.logger.debug(indexMin,indexMax)
        index = np.where(y == np.amax(y[indexMin:indexMax]))

        initY0 = np.mean(y[indexMin:indexMax])
        initWid = 0.05
        initAmp = (np.amax(y[indexMin:indexMax]) - initY0)*(np.sqrt(2 * np.pi) * initWid)
        initCen = data[0][index[0]]
        arr = [initY0, initAmp, initCen, initWid]
        self._initFit = arr

        bounds = (  #LowerBound
                    [ np.mean(y[indexMin:indexMax]) - 0.05,
                    (np.amax(y[indexMin:indexMax]) - initY0) / 8,
                    initCen - 0.05,
                    0.05],
                    #UpperBound
                    [np.mean(y[indexMin:indexMax]) + 0.05,
                    (np.amax(y[indexMin:indexMax]) - initY0) / 2,
                    initCen + 0.01,
                    0.3]
                )

        self._popt, pcov = optimize.curve_fit(self.gaussian, x, y, p0=arr, bounds=bounds)
        self._perr = np.sqrt(np.diag(pcov))

        #x0_err = np.sqrt(pow(self._perr[2],2) + pow(self._popt[3],2))
        x0_err = np.sqrt(pow(self._perr[2], 2))

        self._y0 = ufloat(self._popt[0],self._perr[0])
        self._amp = ufloat(self._popt[1],self._perr[1])
        self._cen = ufloat(self._popt[2],x0_err)
        self._wid = ufloat(self._popt[3],self._perr[3])

        self.logger.debug("y0 = '" + str(self._y0) + "'")
        self.logger.debug("amp = '" + str(self._amp) + "'")
        self.logger.debug("deltaNu = '" + str(self._cen) + "'")
        self.logger.debug("wid = '" + str(self._wid) + "'")

        return self._popt

    @property
    def deltaNu(self):
        """
        :return: Computed Delta Nu
        :rtype:float
        """
        return self._cen

    @property
    def deltaNuEst(self):
        """
        :return:Computed first approximation of delta Nu
        :rtype:float
        """
        return self._deltaNuEst

    @property
    def deltaF(self):
        """
        :return: x-Axis for autocorrelation
        :rtype: 1-D numpy array
        """
        return self._deltaF

    @property
    def bestFit(self):
        return self._popt

    @property
    def correlations(self):
        return self._corrs

    @property
    def nuMax(self):
        return self._nuMax

    @nuMax.setter
    def nuMax(self,value):
        self._nuMax = value
        self.calculateFit()

    @property
    def sigma(self):
        return self._sigma

    @sigma.setter
    def sigma(self,value):
        self._sigma = value
        self.calculateFit()

    @property
    def psd(self):
        return self._psd

    @psd.setter
    def psd(self,value):
        self._psd = value
        self.calculateFit()

    @property
    def backgroundModel(self):
        return self._backgroundModel

    @backgroundModel.setter
    def backgroundModel(self,value):
        self._backgroundModel = value
        self.calculateFit()


    
    
