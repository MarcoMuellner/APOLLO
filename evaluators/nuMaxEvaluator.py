#local imports

from sympy.ntheory import factorint
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
        self.marker["First Filter"] = (self._iterativeFilter(self._init_nu_filter), 'g')
        self.marker["Second Filter"] = (self._iterativeFilter(self.lastFilter), 'b')

        return self.lastFilter

    def _iterativeFilter(self,filterFrequency):
        '''
        This method is called within computeNuMax 2 times, and will, using an ACF, compute the
        proper Numax. For this the signal is filtered at the input filterFrequency using a custom
        IDL-like Trismooth method, and then autocorrelated.
        :rtype: 1-D numpy array
        :type filterFrequency: float
        :param filterFrequency: This frequency is used for filtering the intial signal contained in self._lightcurve
        :return: The smoothed lightcurve. More importantly, it sets self.lastFilter
        '''
        #sanity check
        if not isinstance(filterFrequency,float) and not isinstance(filterFrequency,int):
            raise TypeError("Filter frequency has wrong type! Type: "+str(type(filterFrequency)))

        if filterFrequency == 0:
            raise ValueError("Filter frequency cannot be 0")

        self.figAppendix = str("1st_Fit_" if self.lastFilter == 0 else "2nd_Fit_")  # needed for figure saving
        self.logger.debug("Filterfrequency for iterative filter is '"+str(filterFrequency)+"'")
        tau_filter = 1/(filterFrequency)
        tau_filter *= 10**6

        self.logger.debug("Tau Filter is '"+str(tau_filter)+"'")
        new_normalized_bin_size = int(np.round(tau_filter / self.t_step))
        self.logger.debug("New normalized bin size is '"+str(new_normalized_bin_size)+"'")
        amp_smoothed_array = trismooth(self._lightCurve[1],new_normalized_bin_size)
        amp_filtered_array = self._lightCurve[1]-amp_smoothed_array

        length = 1.5*tau_filter*4/self.t_step
        if length > self.elements:
            length = 1.5 * 4 / (10 ** -7 * self.t_step) - 1
        if length > self.elements:
            length = self.elements - 1

        autocor = self._calculateAutocorrelation(amp_filtered_array)
        autocor = autocor[0:int(length)]
        autocor = autocor**2

        guess = tau_filter/2

        try:
            popt = self._iterativeFit((self._lightCurve[0][0:int(length)]/4,autocor),guess)
        except RuntimeError as e:
            self.logger.error("Failed to fit Autocorrelation")
            self.logger.error("Tau guess is "+str(guess))
            self.logger.error(str(e))

            dataList = {'Autocorrelation': ((self._lightCurve[0][0:int(length)]/4,autocor),geom_line,None),
                        'Fit':((np.linspace(0, 20000, num=50000),self._fit(np.linspace(0, 20000, num=50000))),geom_line,None)}

            plotCustom(self.kicID,"Failed fit result",dataList,r'Time','Autocorrelation'
                       ,self.figAppendix + "Sinc_Fit_error.png")
            show()
            raise e
        except BaseException as e:
            self.logger.error("Scipy fit failed!")
            self.logger.error(str(e))
            raise e


        dataList = {}
        dataList['Autocorrelation'] = ((self._lightCurve[0][0:int(length)]/4,autocor),geom_point,None)
        dataList['Initial Fit'] = ((np.linspace(0,20000,num=50000),self._fit(np.linspace(0,20000,num=50000),1,1/20,guess)),geom_line,None)
        dataList['Corrected Fit'] = ((np.linspace(0,20000,num=50000),self._fit(np.linspace(0,20000,num=50000),*popt)),geom_line,None)
        plotCustom(self.kicID,"Final Fit",dataList,r'Time','Autocorrelation',self.figAppendix+"Final_fit_.png",2)

        tau_first_fit = popt[2]/60
        #this is total hack. FIXME
        if Settings.Instance().getSetting(strDataSettings, strSectStarType).value == strStarTypeYoungStar:
            tau_first_fit /=9

        self.logger.debug("Tau fit is "+str(tau_first_fit))

        self.compFilter = 10**(3.098)*1/(tau_first_fit**0.932)*1/(tau_first_fit**0.05)
        if Settings.Instance().getSetting(strDataSettings, strSectStarType).value == strStarTypeYoungStar:
            self.lastFilter = self.compFilter if (filterFrequency == self._init_nu_filter) else (10 ** 6 / popt[2])
        elif Settings.Instance().getSetting(strDataSettings, strSectStarType).value == strStarTypeRedGiant:
            self.lastFilter = self.compFilter if (filterFrequency == self._init_nu_filter) else (10 ** 6 * 1.5 / popt[2]) #This shouldn't be necessary FIXME
        self.logger.info("New Filter Frequency is '"+str(self.lastFilter)+"'(mu Hz)")
        return self.lastFilter

    def _calculateAutocorrelation(self,oscillatingData):
        '''
        The numpy variant of computing the autocorrelation. See the documentation of the numpy function for more
        information
        :type oscillatingData: 1-D numpy array
        :rtype: 1-D numpy array
        :param oscillatingData:The data that should be correlated (in our case the y function)
        :return: The correlation of oscillatingData
        '''
        corrs2 = np.correlate(oscillatingData, oscillatingData, mode='same')
        N = len(corrs2)
        corrs2 = corrs2[N // 2:]
        lengths = range(N, N // 2, -1)
        corrs2 /= lengths
        corrs2 /= corrs2[0]
        maxcorr = np.argmax(corrs2)
        corrs2 = corrs2 / corrs2[maxcorr]
        return corrs2

    def _iterativeFit(self,data,tauGuess):
        '''
        The iterative Fit approach. Fitting the sinc first, then the sin, subtracting the sin from the original signal and
        fitting the sinc again. Result is then returned
        :rtype: List containing 3 elements
        :type tauGuess: float
        :type data: 2-D numpy array
        :param data:[0] -> temporal axis in seconds, [1] -> normalized flux
        :param tauGuess: Initial Guess for Tau. The rest is fixed
        :return: Values for a,b, tau_acf
        '''
        y = data[1]
        x = data[0]

        self.logger.debug("Initial Guess is "+str(tauGuess))

        arr = [1,tauGuess]

        dataList = {'Data':((x,y),geom_point,None),
                    "Initial Guess":((np.linspace(0,20000,num=50000),self._fit(np.linspace(0,20000,num=50000),1,1/20,tauGuess)),geom_line,None)}
        plotCustom(self.kicID,'Initial Guess Fit',dataList,r'Time','Autocorrelation',self.figAppendix+"InitGuess.png",4)
        popt, pcov = optimize.curve_fit(sinc,x,y,p0=arr,maxfev = 5000)

        #compute residuals

        dataList = {'Data': ((x, y),geom_point,None),
                    "Fit": ((np.linspace(0, 20000, num=50000), sinc(np.linspace(0, 20000, num=50000),*popt)),geom_line,None)}
        plotCustom(self.kicID,'Initial Sinc fit',dataList, r'Time','Autocorrelation',self.figAppendix+"InitSincFit.png",4)

        residuals = y-sinc(x,*popt)
        scaled_time_array = x / popt[1]
        cut = x[scaled_time_array<=2]
        residuals = residuals[scaled_time_array<=2]

        #fit sin to residual!
        arr = [1/20,popt[1]]

        popt,pcov = optimize.curve_fit(sin,cut,residuals,p0=arr,maxfev=5000)
        b = popt[0]

        dataList = {"Residual data": ((cut, residuals),geom_point,None),
                    "Sin Fit": ((np.linspace(0,20000,num=50000),sin(np.linspace(0,20000,num=50000),*popt)),geom_line,None)}
        plotCustom(self.kicID,'Sin fit',dataList,r"Time","Autocorrelation",self.figAppendix + "SinFit.png",4)

        y =  y[scaled_time_array<=2] - sin(cut,*popt)

        popt, pcov = optimize.curve_fit(sinc,cut,y,p0=arr,maxfev = 5000)

        dataList = {"data": ((cut, y),geom_point,None),
                    "Sinc fit": ((np.linspace(0,20000,num=50000),sinc(np.linspace(0,20000,num=50000),*popt)),geom_line,None)}
        plotCustom(self.kicID,'Second Sinc fit',dataList,r"Time","Autocorrelation",self.figAppendix + "SecondSinc.png",4)

        returnList = [popt[0],b,popt[1]]

        return returnList

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
