import numpy as np
import pylab as pl
from scipy import optimize,stats
from sympy.ntheory import factorint
#local imports
from calculations.powerspectraCalculations import PowerspectraCalculator
from settings.settings import Settings
from support.strings import *
from plotter.plotFunctions import *
import logging

class NuMaxCalculator:
    """
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
    """
    def __init__(self,lightCurve):
        """
        The constructor takes the lightcurve of a given star. This lightcurve is then processed
        through the algorithm
        :param lightCurve: 2-Dimensional numpy array.
        """
        self.logger = logging.getLogger(__name__)
        self.__setLightCurve(lightCurve)

    def __setLightCurve(self,lightCurve):
        """
        Internal convenience function. Checks the lightcurve for sanity, rebases temporal axis to
        seconds and starts computation of initial NuMax. Only used within the constructor.
        :param lightCurve: 2-Dimensional numpy array
        :return: Float number representing the initial filter frequency
        """
        #sanity check
        if len(lightCurve) != 2:
            self.logger.error("Lightcurve must be of dimension 2")
            self.logger.error("Lightcurve dimension: '"+str(len(lightCurve))+"'")
            raise ValueError

        #normalize lightCurve and switch to seconds
        self.lightCurve = lightCurve
        self.lightCurve[0] -= self.lightCurve[0][0]
        self.lightCurve[0] *=3600*24

        #compute flicker Amplitude and initial filter frequency
        self.__calculateFlickerAmplitude(self.lightCurve)
        return self.__calculateInitFilterFrequency()

    def __calculateFlickerAmplitude(self,lightCurve):
        """
        This method computes the flicker Amplitude of a given lightcurve. The algorithm works as follows:
        - a "filter time" is chosen. This will serve as the bin size, on which we will compute the flicker
        - the flicker itself is computed by adding up the squared mean deviations from the mean of the lightcurve.
          The squareroot of the value represents a characteristic value, which using a certain empirical function
          can be transformed into the initial filter frequency.

        This method is only used internally in the class.
        :param lightCurve: 2-Dimensional numpy array
        :return: Float number, representing the flicker amplitude.
        """
        #find the new number of bins after the filter
        filterTime = 5
        self.elements = len(lightCurve[0])
        self.duty_cycle = np.mean(lightCurve[0][1:self.elements -1] - lightCurve[0][0:self.elements
                                                                          -2])
        self.logger.debug("Duty cycle is '"+str(self.duty_cycle) +"'" )
        normalized_bin = np.round(filterTime*3600/int(self.duty_cycle))
        self.logger.debug("Normalized Bin is '"+str(normalized_bin)+"'")
        bins = int(self.elements/normalized_bin)

        # Find out how many points are left
        n_points_left = self.elements - normalized_bin*bins
        index_shift = 0
        n_cols = 1

        if n_points_left > 1:
            factors=factorint(n_points_left,multiple=True)
            self.logger.debug(factors)
            if len(factors) > 1:
                index_shift = factors[0]**factors[1]
            else:
                index_shift = factors[0]
            n_cols = int(n_points_left/index_shift + 1)
        elif n_points_left == 1:
            n_cols = 2
            index_shift = 1

        self.logger.debug("Index shift is "+str(index_shift))
        self.logger.debug("n_cols is "+str(n_cols))


        amp_mean_array = np.zeros(n_cols)

        for k in range(0,n_cols):
            amp_rebin_array = np.zeros(int(self.elements-n_points_left))
            n_points_per_bin_array = np.zeros(int(self.elements-n_points_left))
            amp_substract_array = np.zeros(int(self.elements-n_points_left))

            i = k*index_shift

            for j in range(0,bins):
                bin_mean = 0.0
                ref_time = i
                count = 1

                while i < (self.elements-1) and (lightCurve[0][i] - lightCurve[0][ref_time])/(3600*24) <filterTime:
                    bin_mean +=lightCurve[1][i]
                    if lightCurve[1][i] != 0:
                        count +=1
                    i+=1

                bin_mean += lightCurve[1][i]
                if lightCurve[1][i] != 0:
                    count +=1
                count_float = float(count)

                if count > 1:
                    bin_mean /= (count_float-1)

                amp_rebin_array[ref_time - k*index_shift:(i-1)-k*index_shift] = bin_mean
                n_points_per_bin_array[ref_time - k*index_shift:(i-1) - k*index_shift] = count

            amp_substract_array = lightCurve[1][k*index_shift:k*index_shift+len(amp_rebin_array)] -amp_rebin_array
            amp_substract_array = amp_substract_array[n_points_per_bin_array>=normalized_bin/2]
            amp_mean_array[k] = np.mean(amp_substract_array)

        amp_mean = np.mean(amp_mean_array)

        self.logger.info("Mean is: '"+str(amp_mean)+"'")

        #Calculate Flicker Amplitude
        amp_substract_array = np.unique(amp_substract_array)
        amp_flic = 0
        for i in range(0,len(amp_substract_array)):
            amp_flic +=(amp_substract_array[i] - amp_mean)**2
        denominator = float(len(amp_substract_array))
        self.amp_flic = np.sqrt(amp_flic/denominator)

        self.logger.debug("Flicker amplitude is '"+str(amp_flic))

    def __calculateInitFilterFrequency(self):
        """
        This function computes the initial filter Frequency using an empirical function. More information in
        Kallinger (2016). Only used internally.
        """
        self.init_nu_filter = 10**(5.187)/(self.amp_flic**(1.560))
        self.logger.info("Nu filter is '"+str(self.init_nu_filter))
        self.marker = {}
        self.marker["InitialFilter"] = (self.init_nu_filter,'r')

    def computeNuMax(self):
        """
        This method triggers the computation of nuMax and all other necessary values.
        :return: Float value representing nuMax
        """
        self.lastFilter = 0
        self.marker["First Filter"] = (self.__iterativeFilter(self.init_nu_filter),'g')
        self.marker["Second Filter"] = (self.__iterativeFilter(self.lastFilter),'b')

        return self.lastFilter

    def __iterativeFilter(self,filterFrequency):
        """
        This method is called within computeNuMax 2 times, and will, using an ACF, compute the
        proper Numax. For this the signal is filtered at the input filterFrequency using a custom
        IDL-like Trismooth method, and then autocorrelated.
        :param filterFrequency: This frequency is used for filtering the intial signal contained in self.__lightcurve
        :return: The smoothed lightcurve. More importantly, it sets self.lastFilter
        """
        self.figAppendix = str("1st_Fit_" if self.lastFilter == 0 else "2nd_Fit_")  # needed for figure saving
        self.logger.debug("Filterfrequency for iterative filter is '"+str(filterFrequency)+"'")
        tau_filter = 1/(filterFrequency)
        tau_filter *= 10**6

        self.logger.debug("Tau Filter is '"+str(tau_filter)+"'")
        new_normalized_bin_size = int(np.round(tau_filter/self.duty_cycle))
        self.logger.debug("New normalized bin size is '"+str(new_normalized_bin_size)+"'")
        amp_smoothed_array = self.__trismooth(self.lightCurve[1],new_normalized_bin_size)
        amp_filtered_array = self.lightCurve[1]-amp_smoothed_array

        length = 1.5*tau_filter*4/self.duty_cycle
        if length > self.elements:
            length = 1.5*4/(10**-7*self.duty_cycle)-1
        if length > self.elements:
            length = self.elements - 1

        autocor = self.__calculateAutocorrelation(amp_filtered_array)
        autocor = autocor[0:int(length)]
        autocor = autocor**2

        #guess =tau_filter/8 if (filterFrequency == self.init_nu_filter) else tau_filter/4
        guess = tau_filter/2

        try:
            popt = self.__iterativeFit((self.lightCurve[0][0:int(length)]/4,autocor),guess)
        except RuntimeError as e:
            self.logger.error("Failed to fit Autocorrelation")
            self.logger.error("Tau guess is "+str(guess))
            self.logger.error(str(e))

            dataList = {'Autocorrelation': ('-',self.lightCurve[0][0:int(length)]/4,autocor), "Initial Guess": (
                '-', np.linspace(0, 20000, num=50000),
                self.__fit(np.linspace(0, 20000, num=50000), 1, 1 / 20, guess))}
            plotCustom(dataList,title="Failed fit result",showLegend=True,fileName=self.figAppendix+"Sinc_Fit_error.png")
            show()
            raise e
        except BaseException as e:
            self.logger.error("Scipy fit failed!")
            self.logger.error(str(e))
            raise e


        dataList = {}
        dataList['Autocorrelation'] = ('x',self.lightCurve[0][0:int(length)]/4,autocor)
        dataList['Initial Fit'] = ('-',np.linspace(0,20000,num=50000),self.__fit(np.linspace(0,20000,num=50000),1,1/20,guess))
        dataList['Corrected Fit'] = ('-',np.linspace(0,20000,num=50000),self.__fit(np.linspace(0,20000,num=50000),*popt))
        plotCustom(dataList,title="Final Fit",showLegend=True,fileName=self.figAppendix+"Final_fit_.png")
        show(2)

        tau_first_fit = popt[2]/60
        #this is total hack. FIXME
        if Settings.Instance().getSetting(strDataSettings, strSectStarType).value == strStarTypeYoungStar:
            tau_first_fit /=9

        self.logger.debug("Tau fit is "+str(tau_first_fit))

        self.compFilter = 10**(3.098)*1/(tau_first_fit**0.932)*1/(tau_first_fit**0.05)
        if Settings.Instance().getSetting(strDataSettings, strSectStarType).value == strStarTypeYoungStar:
            self.lastFilter = self.compFilter if (filterFrequency==self.init_nu_filter) else (10**6/popt[2])
        elif Settings.Instance().getSetting(strDataSettings, strSectStarType).value == strStarTypeRedGiant:
            self.lastFilter = self.compFilter if (filterFrequency==self.init_nu_filter) else (10**6*1.5/popt[2]) #This shouldn't be necessary FIXME
        self.logger.info("New Filter Frequency is '"+str(self.lastFilter)+"'(mu Hz)")
        return self.lastFilter

    def __trismooth(self,x,window_width,gauss=False):
        """
        This function is implemented to create a similar function to the Trismooth function of idl
        :param x: The array containg the data which should be filtered. In our case this represents the Flux within the
                  lightCurve
        :param window_width: The bin size which the function will look at
        :param gauss: Not in use
        :return: The smoothed variant of x
        """
        if window_width%2 != 0:
            window_width = window_width+1

        lend = len(x)-1
        if (lend+1) < window_width:
            self.logger.error("Vector too short!")
            self.logger.error("lend: '"+str(lend)+"'")
            self.logger.error("window_width: '"+str(window_width)+"'")
            raise

        halfWeights = np.arange(window_width/2)
        weights = np.append(halfWeights,[window_width/2])
        weights = np.append(weights,halfWeights[::-1])
        weights +=1
        tot = np.sum(weights)

        smoothed = np.zeros(lend+1)
        offset = int(window_width/2)
        local = np.zeros(window_width)

        self.logger.debug("Len smoothed "+str(len(smoothed)))
        self.logger.debug("Offset is "+str(offset))
        self.logger.debug("len local "+str(len(local)))

        for i in range(offset,lend-offset):
            smoothed[i]=np.sum(x[i-offset:i+offset+1]*weights)

        smoothed /=tot

        for i in range(0,offset):
            smoothed[i] = np.sum(x[0:i+offset+1]*weights[offset-i:]) / np.sum(weights[offset-i:])

        for i in range(lend-offset,lend-1,-1):
            smoothed[i] = np.sum(x[i-offset:]*weights[0:offset+(lend-i)]) / np.sum(weights[0:offset+(lend-i)])

        return smoothed

    def __calculateAutocorrelation(self,oscillatingData):
        """
        The numpy variant of computing the autocorrelation. See the documentation of the numpy function for more information
        :param oscillatingData: 1-D numpy array. The data that should be correlated (in our case the y function)
        :return: The correlation of oscillatingData
        """
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

    def __scipyFit(self,data,tauGuess):
        """
        Single fit variant (fits the total function all at ones to the data)
        :param data: 2-D numpy array. [0] -> temporal axis, [1] -> flux
        :param tauGuess: The initial Guess for Tau. The rest is fixed
        :return: a List with 3 entries (values for a,b, tau_acf)
        """
        y = data[1]
        x = data[0]

        self.logger.debug("Initial Guess is "+str(tauGuess))

        arr = [1.0,1/20,tauGuess]
        popt, pcov = optimize.curve_fit(self.__fit, x, y,p0=arr,maxfev=5000)
        perr = np.sqrt(np.diag(pcov))
        self.logger.debug("a = '" + str(popt[0]) + " (" + str(perr[0]) + ")'")
        self.logger.debug("b = '" + str(popt[1]) + " (" + str(perr[1]) + ")'")
        self.logger.debug("tau_acf = '" + str(popt[2]) + " (" + str(perr[2]) + ")'")

        return popt

    def __iterativeFit(self,data,tauGuess):
        """
        The iterative Fit approach. Fitting the sinc first, then the sin, subtracting the sin from the original signal and
        fitting the sinc again. Result is then returned
        :param data: 2-D numpy array. [0] -> temporal axis, [1] -> flux
        :param tauGuess: Initial Guess for Tau. The rest is fixed
        :return: a List with 3 entries (values for a,b, tau_acf)
        """
        y = data[1]#[0:int(len(data[1])/3)]
        x = data[0]#[0:int(len(data[0])/3)]

        self.logger.debug("Initial Guess is "+str(tauGuess))

        arr = [1,tauGuess]

        dataList = {'data':('x',x,y),"Initial Guess":(
        '-',np.linspace(0,20000,num=50000),self.__fit(np.linspace(0,20000,num=50000),1,1/20,tauGuess))}
        plotCustom(dataList,title='Initial Guess Fit',showLegend=True,fileName=self.figAppendix+"InitGuess.png")
        show(4)
        popt, pcov = optimize.curve_fit(self.__sinc,x,y,p0=arr,maxfev = 5000)

        #compute residuals

        dataList = {'data': ('x', x, y), "Fit": (
        '-', np.linspace(0, 20000, num=50000), self.__sinc(np.linspace(0, 20000, num=50000),*popt))}
        plotCustom(dataList, title='Initial Sinc fit', showLegend=True,fileName=self.figAppendix + "InitSincFit.png")
        show(4)

        residuals = y-self.__sinc(x,*popt)
        scaled_time_array = x / popt[1]
        cut = x[scaled_time_array<=2]
        residuals = residuals[scaled_time_array<=2]

        #fit sin to residual!
        arr = [1/20,popt[1]]

        popt,pcov = optimize.curve_fit(self.__sin,cut,residuals,p0=arr,maxfev=5000)
        b = popt[0]

        dataList = {"Residual data": ('x', cut, residuals), "Sin Fit": (
            '-', np.linspace(0,20000,num=50000),self.__sin(np.linspace(0,20000,num=50000),*popt))}
        plotCustom(dataList, title='Sin fit', showLegend=True, fileName=self.figAppendix + "SinFit.png")
        show(4)

        y =  y[scaled_time_array<=2] - self.__sin(cut,*popt)

        popt, pcov = optimize.curve_fit(self.__sinc,cut,y,p0=arr,maxfev = 5000)

        dataList = {"data": ('x', cut, y), "Sinc fit": (
            '-', np.linspace(0,20000,num=50000),self.__sinc(np.linspace(0,20000,num=50000),*popt))}
        plotCustom(dataList, title='Second Sinc fit', showLegend=True, fileName=self.figAppendix + "SecondSinc.png")
        show(4)

        returnList = [popt[0],b,popt[1]]

        return returnList


    def __sin(self,x,amp,tau):
        """
        Represents the used sin within our Fit
        :param x: 1-D numpy array
        :param amp: float, Amplitude of sin
        :param tau: float
        :return: the functional values for the array x
        """
        return amp*np.sin(2*np.pi*4*x/tau)

    def __sinc(self,x, a, tau_acf):
        """
        Represents the used sinc within our Fit
        :param x: 1-D numpy array
        :param a: float, amplitude of the sinc
        :param tau_acf: float
        :return: the functional value for the array x
        """
        return a * np.sinc((4* np.pi*x / tau_acf))**2

    def __fit(self,x,a,b,tau_acf):
        return self.__sinc(x,a,tau_acf) + self.__sin(x,b,tau_acf)

    def getNyquistFrequency(self):
        """
        Computes the Nyquist frequency for the lightcurve supplied in the constructor.
        :return:
        """
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
