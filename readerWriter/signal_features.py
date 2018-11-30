# standard imports
from typing import Dict
# scientific imports
import numpy as np
from scipy.signal import periodogram,butter,filtfilt
from astropy.convolution import convolve, Box1DKernel
# project imports

def compute_periodogram(data : np.ndarray) -> np.ndarray:
    """
    Computes a given periodogram from the lightcurve
    :param data: Lightcurve dataset
    :param kwargs: Run configuration
    :return: Periodogram from the dataset
    """
    fs = 1 / ((data[0][10] - data[0][9]) * 24 * 3600)  # doesnt matter which timepoint is used.
    f, psd = periodogram(data[1], fs, scaling='density')
    f = f * 10 ** 6
    psd = np.divide(psd[1:], 10 ** 6)
    f = f[1:]
    return np.array((f, psd))

def get_time_step(data:np.ndarray) ->float:
    """
    Returns the most common time steps in the datapoints.
    :param data: Dataset of the lightcurve
    :return: Most common time diff
    """
    real_diff = data[0][1:len(data[0])] - data[0][0:len(data[0]) - 1]
    (values, counts) = np.unique(real_diff, return_counts=True)
    most_common = values[np.argmax(counts)]
    return most_common


def nyqFreq(data : np.ndarray) -> float:
    """
    Computes the nyquist frequency according to the nyquist theorem.
    :param data: Timeseries dataset. Time needs to be in days
    :return: Nyquist frequency in uHz
    """
    t_diff = get_time_step(data) * 24 *3600 #convert mostcommon to seconds
    return 10 ** 6/(2*t_diff) #return Nyquist

def boxcar_smoothing(data : np.ndarray,smooth : int =100) -> np.ndarray:
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
        return np.array((data[0],smoothed_signal))
    else:
        return smoothed_signal


def noise(data : np.ndarray) -> float:
    """
    Computes the noise according to Bugnet (2018)
    :param data: Periodogramm data.
    :return: noise value
    """
    median = np.median(data[1][-100:-1])
    return median*(1-2/18)**3 #relationship between mean and median for Chi^2 distribution
