#local imports

from sympy.ntheory import factorint
from scipy.signal import argrelextrema
import numpy as np

# local imports
from plotter.plotFunctions import *
from fitter.fitFunctions import *
from plotnine import *


class NuMaxEvaluator:
    '''
    This class autocorrelates the lightcurve, in such a way that it will provide all the necessary
    values to continue computation (i.e. Background noise, Nyquist frequency, nuMax). To compute
    these values, simply provide a 2-D numpy array, where [0] is the x-Axis (i.e. temporal axis)
    and the y-Axis is the flux. Strays should have been removed before giving this class a lightcurve.

    This class represents one calculator for such a lightcurve. It is not possible to reset the
    lightcurve. If you want to compute the values for other lightcurves, you need to create a new
    object.

    Additionally this class contains "marker" representing the filter frequencies. This can be used
    for plotting capabilities.

    To compute NuMax, it is necessary to call computeNuMax(), which will then give you nuMax.

    For more information see Kallinger (2016) on the algorithm used here.
    '''
    def __init__(self, kicID,data):
        '''
        The constructor takes the lightcurve of a given star. This lightcurve is then processed
        through the algorithm. The flicker amplitude and initial Filter frequency are computed
        while setting the lightCurve
        :type lightCurve: ndarray
        :param lightCurve: Data containing the lightCurve. 1st axis -> temporal axis in days,
        2nd Axis -> Flux
        '''
        self.logger = logging.getLogger(__name__)
        self.lastFilter = None
        self.lightCurve = data
        self.kicID = kicID

    def _calculateFlickerAmplitude(self):
        '''
        This method computes the flicker Amplitude of a given lightcurve. The algorithm works as follows:
        - a "filter time" is chosen. This will serve as the bin size, on which we will compute the flicker
        - the flicker itself is computed by adding up the squared mean deviations from the mean of the lightcurve.
          The squareroot of the value represents a characteristic value, which using a certain empirical function
          can be transformed into the initial filter frequency.

        This method is only used internally in the class.
        '''
        #find the new number of bins after the filter
        filterTime = 5 *24 * 3600 #in days
        self.elements = len(self.lightCurve[0])
        self.t_step = np.mean(self.lightCurve[0][1:self.elements] - self.lightCurve[0][0:self.elements- 1])

        boxSize = np.round(filterTime/int(self.t_step))
        binCount = int(self.elements/boxSize)
        pointsLeft = self.elements - boxSize*binCount

        self.logger.debug("Duty cycle is '" + str(self.t_step) + "'")
        self.logger.debug("Box Size is '" + str(boxSize) + "'")
        self.logger.debug("Number of bins is '" + str(binCount) + "'")

        indexShift,cols = self._getIndexShift(pointsLeft)

        meanArray,subtractArrayAmplitude = self._getFlickerArrays(cols,indexShift,boxSize,filterTime)

        meanAmplitude = np.mean(meanArray)

        self.logger.info("Mean is: '"+str(meanAmplitude)+"'")

        #Calculate Flicker Amplitude
        subtractArrayAmplitude = np.unique(subtractArrayAmplitude)
        flicAmplitude = 0

        for i in range(0,len(subtractArrayAmplitude)):
            flicAmplitude +=(subtractArrayAmplitude[i] - meanAmplitude)**2

        denominator = float(len(subtractArrayAmplitude))
        self._amp_flic = np.sqrt(flicAmplitude / denominator)

        self.logger.debug("Flicker amplitude is '"+str(flicAmplitude))

    def _calculateInitFilterFrequency(self):
        '''
        This function computes the initial filter Frequency using an empirical function. More information in
        Kallinger (2016). Only used internally.
        '''
        if self._amp_flic is None:
            self.logger.debug("Flicker amplitude is None, calculating it first")
            self._calculateFlickerAmplitude()

        self._init_nu_filter = 10 ** (5.187) / (self._amp_flic ** (1.560))
        self.logger.info("Nu filter is '" + str(self._init_nu_filter))
        self.marker = {"InitialFilter":(self._init_nu_filter, 'r')}

    def computeNuMax(self):
        '''
        This method triggers the computation of nuMax and all other necessary values.
        :return: Float value representing nuMax
        '''
        self.lastFilter = 0
        tauInitFilter = self._iterativeFilter(self._init_nu_filter)
        itFilter = self._computeFilterFrequency(tauInitFilter)
        tauTwo = self._iterativeFilter(itFilter)
        itFilter2 = self._computeFilterFrequency(tauTwo)
        tauFinal = self._iterativeFilter(itFilter2)
        nu_final = self._computeFinalFrequency(tauFinal)

        self.marker["Initial Filter"] = (self._init_nu_filter,'r')
        self.marker["Second Filter"] = (itFilter,'g')
        self.marker["Third Filter"] = (itFilter2, 'c')
        self.marker["Final nuMax"] = (nu_final,'b')

        self.lastFilter = nu_final

        return self.lastFilter

    def _computeFilterFrequency(self,tau):
        """
        Computes second filter frequency
        :param tau: tau in minutes
        :return: filterfrequency in uHz
        """
        log_y = 3.098 - 0.932 * np.log10(tau) - 0.025 * (np.log10(tau)) ** 2
        return 10 ** log_y

    def _computeFinalFrequency(self,tau):
        """
        Computes the final nuMax
        :param tau: Tau in minutes
        :return: frequency in uHz
        """
        return 10 ** 6 /(tau*60)

    def _iterativeFilter(self,filterFrequency):
        if not isinstance(filterFrequency,float) and not isinstance(filterFrequency,int):
            raise TypeError("Filter frequency has wrong type! Type: "+str(type(filterFrequency)))

        if filterFrequency == 0:
            raise ValueError("Filter frequency cannot be 0")

        self.logger.info(f"Running filter for {filterFrequency}")
        self.fitAppendix = filterFrequency

        tau = 10 ** 6 / filterFrequency
        normalizedBinSize = int(np.round(tau / self.t_step))
        filteredLightCurve = self._lightCurve[1] - trismooth(self._lightCurve[1], normalizedBinSize)

        corr = self._calculateAutocorrelation(filteredLightCurve)

        fitData = np.array((self._lightCurve[0][1:]/60,corr[1:])) #lightCurve x in minutes, as well as remove firstpoint

        tau_fit = self._iterativeFit(fitData, tau / 60)
        return tau_fit

    def _calculateAutocorrelation(self,oscillatingData):
        '''
        The numpy variant of computing the autocorrelation. See the documentation of the numpy function for more
        information
        :type oscillatingData: 1-D numpy array
        :rtype: 1-D numpy array
        :param oscillatingData:The data that should be correlated (in our case the y function)
        :return: The correlation of oscillatingData
        '''
        corr = np.correlate(oscillatingData, oscillatingData, mode='full')
        corr = corr[corr.size // 2:]
        corr /= max(corr)
        corr = corr ** 2
        return corr

    def _iterativeFit(self,data,tauGuess):
        minima = argrelextrema(data[1], np.less)[0][0]
        minimaFactor = int(30 * np.exp(-minima / 3) + minima)  # kinda arbitrary, just need enough points
        y = data[1][:minimaFactor]
        x = data[0][:minimaFactor] - data[0][0]
        plotX = np.linspace(0, max(x), num=max(x) * 5)

        x = x[int(np.where(y == max(y))[0]):]
        y = y[int(np.where(y == max(y))[0]):]

        p0SincOne = [1, tauGuess]
        bounds = (
            [0, 0], [1, np.inf]
        )

        sincPopt, pcov = optimize.curve_fit(sinc, x, y, p0=p0SincOne, bounds=bounds)

        residuals = y - sinc(x, *sincPopt)

        p0 = [max(residuals), sincPopt[1]]

        sinPopt, pcov = optimize.curve_fit(sin, x, residuals, p0=p0)

        sinResiduals = y - sin(x, *sinPopt)

        p0 = [1, sincPopt[1]]

        lastSincPopt, pcov = optimize.curve_fit(sinc, x, sinResiduals, p0=p0, bounds=bounds)

        dataList = {"Autocorrelation": ((x, y), geom_point, None),
                    "Initial Data": ((plotX, sinc(plotX, *p0SincOne)), geom_line, None),
                    "Final Sinc Fit": ((plotX, sinc(plotX, *lastSincPopt)), geom_line, None)}

        plotCustom(self.kicID, 'Sinc fit', dataList, r"Time", "Autocorrelation", f"{self.fitAppendix}  SincFit.png", 4)

        return lastSincPopt[1]

    def _fit(self,x,a,b,tau_acf):
        return sinc(x,a,tau_acf) + sin(x,b,tau_acf)

    @property
    def lightCurve(self):
        '''
        Property of lightCurve.
        :return: Normalized data of lightCurve. 1st Axis -> temporal axis in seconds. 2nd axis -> normalized flux
        :rtype: 2-D numpy array
        '''
        return self._lightCurve

    @lightCurve.setter
    def lightCurve(self, value):
        '''
        Setter function for lightCurve. Checks the data for sanity, rebases temporal axis (1st axis)
        to seconds and starts computation of initial numax.
        :param value: Represents the lightCurve of a star. 1st axis -> temporal axis in days
        2nd axis -> flux
        :type value: 2-D numpy array
        :return: Initial Filter frequency
        :rtype: float
        '''
        # sanity check
        # check if type is correct
        if not isinstance(value,np.ndarray):
            raise TypeError("LightCurve must be of type ndarray! Type: "+str(type(value)))

        #check if shape is correct
        if value is not None and len(value) != 2:
            self.logger.error("Lightcurve must be of dimension 2")
            self.logger.error("Lightcurve data: "+str(value))
            self.logger.error("Lightcurve dimension: '" + str(len(value)) + "'")
            raise ValueError("Value of lightcurve is not correct!")

        #check if the lightcurve was provided in days
        if any(i > 10**7 for i in value[0]):
            self.logger.error("You need to provide a lightCurve in days, not seconds!")
            raise ValueError("Temporal axis is in wrong unit")

        # normalize lightCurve and switch to seconds
        self._lightCurve = value
        self._lightCurve[0] -= self._lightCurve[0][0]
        self._lightCurve[0] *= 3600 * 24

        # compute flicker Amplitude and initial filter frequency
        self._calculateFlickerAmplitude()
        self._calculateInitFilterFrequency()

    @property
    def kicID(self):
        return self._kicID

    @kicID.setter
    def kicID(self,value):
        self._kicID = value
        
    def _getIndexShift(self,pointsLeft):
        """
        Depending on how many points are left in the array from the binsize, this method will return the according
        indexShift for the data as well as the amount of cols whereover these have to be iterated
        :param pointsLeft: Restpoints after binning
        :return: indexShift,cols
        """
        indexShift = 0
        cols = 1

        if pointsLeft > 1:

            factors=factorint(pointsLeft,multiple=True)

            if len(factors) > 1:
                indexShift = factors[0]**factors[1]
            else:
                indexShift = factors[0]

            cols = int(pointsLeft/indexShift + 1)

        elif pointsLeft == 1:
            cols = 2
            indexShift = 1

        self.logger.debug("Index shift is "+str(indexShift))
        self.logger.debug("n_cols is "+str(cols))

        return indexShift,cols


    def _getFlickerArrays(self,cols,indexShift,boxSize,filterTime):
        """
        This method, depending on the indexshift, boxsize and filtertime creates the appropiate arrays, for which the
        flicker amplitude is calculated. It calculates the mean of every box for the boxsize
        """
        binCount = int(self.elements/boxSize)
        pointsLeft = self.elements - boxSize*binCount

        arrayMean = np.zeros(cols)

        for k in range(0,cols):
            arrayRebin = np.zeros(int(self.elements-pointsLeft))
            nPointsBinArray = np.zeros(int(self.elements-pointsLeft))

            i = k*indexShift

            for j in range(0,binCount):
                meanBin = 0.0
                timeReference = i
                count = 1

                while i < (self.elements-1) and (self.lightCurve[0][i] - self.lightCurve[0][timeReference])/(3600*24) <filterTime:
                    meanBin +=self.lightCurve[1][i]
                    if self.lightCurve[1][i] != 0:
                        count +=1
                    i+=1

                meanBin += self.lightCurve[1][i]
                if self.lightCurve[1][i] != 0:
                    count +=1

                if count > 1:
                    meanBin /= count-1

                arrayRebin[timeReference - k*indexShift:(i-1)-k*indexShift] = meanBin
                nPointsBinArray[timeReference - k*indexShift:(i-1) - k*indexShift] = count

            subtractArrayAmplitude = self.lightCurve[1][k*indexShift:k*indexShift+len(arrayRebin)] -arrayRebin
            subtractArrayAmplitude = subtractArrayAmplitude[nPointsBinArray>=boxSize/2]
            arrayMean[k] = np.mean(subtractArrayAmplitude)

        return arrayMean,subtractArrayAmplitude
