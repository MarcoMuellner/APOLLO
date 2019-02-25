import numpy as np
from scipy import optimize
from uncertainties import ufloat
from background.backgroundResults import BackgroundResults
from data_handler.signal_features import compute_periodogram, nyqFreq
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as pl
from plotter.plot_handler import plot_f_space, plot_delta_nu_acf,plot_delta_nu_fit
from fitter.fit_functions import gaussian_amp,scipyFit


def _findGaussBoundaries(data=None, cen=None, sigma=None):
    '''
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
    '''
    minima = 0
    maxima = 0
    deltaMinima = 1000
    deltaMaxima = 1000
    indexMin = 0
    indexMax = 0

    # iterating through the dataset
    for i in range(0, len(data[0]) - 1):
        if (abs(data[0][i] - (cen - 2 * sigma)) < deltaMinima):
            deltaMinima = abs(data[0][i] - (cen - 2 * sigma))
            minima = data[0][i]
            indexMin = i

        if (abs(data[0][i] - (cen + 2 * sigma)) < deltaMaxima):
            deltaMaxima = abs(data[0][i] - (cen + 2 * sigma))
            maxima = data[0][i]
            indexMax = i

    return (minima, maxima, indexMin, indexMax)

def _butter_lowpass_filtfilt(data, nyq, level, order=5):
    '''
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
    '''
    normal_cutoff = level / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y


def _estimateDeltaNu(nuMax=None):
    '''
    Gives an estimation of deltaNu using an empirical relation by Stello et al. (2009)
    :param nuMax: The frequency of maximum oscillation in the PSD
    :type nuMax:float
    :return:An estimation of where Delta nu should be.
    :rtype:float
    '''
    deltaNuEst = 0.267 * pow(nuMax, 0.760)
    return deltaNuEst


def autocorrelate(f_y):
    '''
    Restricts the data to the oscillating part and calculates the autoorrelation
    :return:y-Axis of the Autocorrelated data
    :rtype:1-D numpy array
    '''
    corrs2 = np.correlate(f_y, f_y, mode='full')
    N = len(corrs2)
    corrs = corrs2[N // 2:]
    lengths = range(N, N // 2, -1)
    corrs /= lengths
    corrs /= corrs2[0]
    return corrs

def perform_fit(x : np.ndarray,y : np.ndarray,kwargs):
    initY0 = np.mean(y)
    initWid = 0.05
    initCen = x[np.argmin(np.abs(y-np.amax(y)))]
    initAmp = (max(y)- initY0)*(np.sqrt(2 * np.pi) * initWid)

    popt,perr = scipyFit(x,y,gaussian_amp,[initY0,initAmp,initCen,initWid])

    return popt,perr




def get_delta_nu(data: np.ndarray, result: BackgroundResults, kwargs):
    model = result.createBackgroundModel()
    f_data = compute_periodogram(data,kwargs)

    background = np.sum(model[:4], axis=0)

    delta_nu = _estimateDeltaNu(result.nuMax.nominal_value)

    cleared_data = np.divide(f_data[1], background)
    cleared_data = _butter_lowpass_filtfilt(cleared_data, nyqFreq(data), delta_nu * 10)

    mask = np.logical_and(f_data[0] > (result.nuMax - 3 * result.sigma).nominal_value,
                          f_data[0] < (result.nuMax + 3 * result.sigma).nominal_value)

    f_x = f_data[0][mask]
    f_y = cleared_data[mask]

    plot_f_space(np.array((f_x, f_y)),
                 f_list=[(result.nuMax.nominal_value, "Nu Max")], plot_name="Oscillation_region", kwargs=kwargs)

    _,_,index_min,index_max = _findGaussBoundaries(np.array((f_x,f_y)),result.nuMax.nominal_value,result.sigma.nominal_value)

    corrs = autocorrelate(f_y)

    stepFreq = f_x[2] - f_x[1]
    deltaF = np.zeros(len(corrs))
    for i in range(0, len(deltaF)):
        deltaF[i] = i * stepFreq

    mask = np.logical_and(deltaF > delta_nu/1.4,deltaF < 1.5* delta_nu)
    plot_delta_nu_acf(np.array((deltaF[mask], corrs[mask])), delta_nu, kwargs)
    popt,perr = perform_fit(deltaF[mask], corrs[mask],kwargs)
    plot_delta_nu_fit(np.array((deltaF[mask], corrs[mask])),popt,kwargs)

    delta_nu = ufloat(popt[2],perr[2])

    return delta_nu
