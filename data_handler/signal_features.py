# standard imports
from typing import Dict,Tuple
# scientific imports
import numpy as np
from scipy.signal import periodogram, butter, filtfilt
from astropy.convolution import convolve, Box1DKernel
from astropy.stats import LombScargle
import matplotlib.pyplot as pl
from scipy.integrate import simps
from res.conf_file_str import internal_literature_value,internal_noise_value
from support.printer import print_int
from data_handler.parameters import priors_only
import time


# project imports

def window_function(df,nyq,ls,width = None, oversampling = 10):
    if width is None:
        width = 100 * df

    freq_cen = 0.5 * nyq
    Nfreq = int(oversampling * width /df)
    freq = freq_cen + (df / oversampling) * np.arange(-Nfreq, Nfreq, 1)

    x = 0.5 * np.sin(2 * np.pi * freq_cen * ls.t) + 0.5 * np.cos(2 * np.pi * freq_cen * ls.t)

    # Calculate power spectrum for the given frequency range:
    ls = LombScargle(ls.t, x, center_data=True)
    power = ls.power(freq, method='fast', normalization='psd', assume_regular_frequency=True)
    power /= power[int(len(power) / 2)]  # Normalize to have maximum of one

    freq -= freq_cen
    freq *= 1e6
    return freq, power

def fundamental_spacing_integral(df,nyq,ls):
    freq, window = window_function(df,nyq,ls,width=100*df, oversampling=5)
    df = simps(window, freq)
    return df*1e-6

def compute_periodogram(data: np.ndarray,kwargs : Dict) -> np.ndarray:
    """
    Computes a given periodogram from the lightcurve
    :param data: Lightcurve dataset
    :return: Periodogram from the dataset
    """
    indx = np.isfinite(data[1])
    df = 1 / (86400 * (np.amax(data[0][indx]) - np.amin(data[0][indx])))  # Hz
    ls = LombScargle(data[0][indx] * 86400, data[1][indx], center_data=True)
    nyq = 1/(2*86400*np.median(np.diff(data[0][indx])))

    df = fundamental_spacing_integral(df,nyq,ls)

    freq = np.arange(df ,nyq, df)
    power = ls.power(freq, normalization='psd', method='fast', assume_regular_frequency=True)

    N = len(ls.t)
    tot_MS = np.sum((ls.y - np.mean(ls.y)) ** 2) / N
    tot_lomb = np.sum(power)
    normfactor = tot_MS / tot_lomb
    freq *=10**6
    power *= normfactor/(df*10**6)

    if internal_literature_value in kwargs.keys() and internal_noise_value in kwargs.keys():
        prior_values = priors_only(kwargs[internal_literature_value].nominal_value,np.array((freq,power)),noise(np.array((freq,power))))
        #freq,power = reduce_signal(np.array((freq,power)),prior_values,nyqFreq(data),kwargs)

    return np.array((freq,power))

def get_time_step(data: np.ndarray) -> float:
    """
    Returns the most common time steps in the datapoints.
    :param data: Dataset of the lightcurve
    :return: Most common time diff
    """
    real_diff = data[0][1:len(data[0])] - data[0][0:len(data[0]) - 1]
    (values, counts) = np.unique(real_diff, return_counts=True)
    most_common = values[np.argmax(counts)]
    return most_common


def nyqFreq(data: np.ndarray) -> float:
    """
    Computes the nyquist frequency according to the nyquist theorem.
    :param data: Timeseries dataset. Time needs to be in days
    :return: Nyquist frequency in uHz
    """
    t_diff = get_time_step(data) * 24 * 3600  # convert mostcommon to seconds
    return 10 ** 6 / (2 * t_diff)  # return Nyquist

def nyqFreq_c_d(data: np.ndarray) -> float:
    """
    Computes the nyquist frequency according to the nyquist theorem.
    :param data: Timeseries dataset. Time needs to be in days
    :return: Nyquist frequency in uHz
    """
    t_diff = get_time_step(data)  # convert mostcommon to seconds
    return 1 / (2 * t_diff)  # return Nyquist


def boxcar_smoothing(data: np.ndarray, smooth: int = 100) -> np.ndarray:
    """
    Performs boxcar smoothing on a given dataset
    :param data: temporal dataset
    :return: smoothed dataset
    """
    if len(data) != 1:
        y = data[1]
    else:
        y = data

    smoothed_signal = convolve(y, Box1DKernel(smooth))

    if len(data) != 1:
        return np.array((data[0], smoothed_signal))
    else:
        return smoothed_signal


def noise(data: np.ndarray) -> float:
    """
    Computes the noise according to Bugnet (2018)
    :param data: Periodogramm data.
    :return: noise value
    """
    median = np.median(data[1][-100:-1])
    return median * (1 - 2 / 18) ** 3  # relationship between mean and median for Chi^2 distribution


def background_model(psd: np.ndarray, nyq: float, w: float, sigma_long: float, freq_long: float,
                     sigma_gran1: float, freq_gran1: float,
                     sigma_gran2: float, freq_gran2: float, nu_max: float = None, amp: float = None,
                     sigma: float = None):
    '''
    Creates a full Background model
    :return: Background Model
    '''
    if nu_max is not None and amp is not None and sigma is not None:
        g = amp * np.exp(-(nu_max - psd[0]) ** 2 / (2. * sigma ** 2))  ## Gaussian envelope
    else:
        g = 0

    zeta = 2. * np.sqrt(2.) / np.pi  # !DPI is the pigreca value in double precision
    r = (np.sin(np.pi / 2. * psd[0] / nyq) / (
                np.pi / 2. * psd[0] / nyq)) ** 2  # ; responsivity (apodization) as a sinc^2

    ## Long-trend variations
    h_long = (sigma_long ** 2 / freq_long) / (1. + (psd[0] / freq_long) ** 4)

    ## First granulation component
    h_gran1 = (sigma_gran1 ** 2 / freq_gran1) / (1. + (psd[0] / freq_gran1) ** 4)

    ## Second granulation component
    h_gran2 = (sigma_gran2 ** 2 / freq_gran2) / (1. + (psd[0] / freq_gran2) ** 4)

    ## Global background model
    w = np.zeros_like(psd[0]) + w
    if nu_max is not None and amp is not None and sigma is not None:
        retVal = zeta * h_long * r, zeta * h_gran1 * r, zeta * h_gran2 * r, w, g * r
    else:
        retVal = zeta * h_long * r, zeta * h_gran1 * r, zeta * h_gran2 * r, w

    return retVal

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

def reduce_signal(f_data : np.ndarray,priors : Dict[str,float], nyq : float, kwargs : Dict)-> Tuple[np.ndarray,np.ndarray]:
    """
    Reduces the oscillation signal to a given level to hide it in the noise.
    :param f_data: PSD
    :param priors: priors determined using the literature value
    :param nyq: nyquist frequency
    :param kwargs: settings
    :return: frequency and power
    """
    bg_model = background_model(f_data, nyq, priors['w'], priors['sigma_1'], priors['b_1'], priors['sigma_2'],
                                priors['b_2'], priors['sigma_3'], priors['b_3'], priors['nu_max'], priors['H_osc'],
                                priors['sigma'])

    factor = (priors['H_osc']/priors['w'])/270 #empirically determined

    f_without_bg = f_data[1] / np.sum(bg_model[0:3]) #divide by background
    gauss = bg_model[4] / np.amax(bg_model[4]) #normalize gauss
    f_without_bg_gauss = f_without_bg * gauss #multiply signal with gauss
    f_without_bg -= f_without_bg_gauss #get residual
    f_without_bg_gauss /= ((kwargs[internal_noise_value]+1)*factor) #reduce by noise value
    f_without_bg += f_without_bg_gauss #add residual again
    f_without_bg *= np.sum(bg_model[0:3]) #multiply with
    return f_data[0],f_without_bg

