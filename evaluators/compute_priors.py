# library imports
from typing import List, Dict,Tuple
# scientific imports
import numpy as np
# project imports
from data_handler.signal_features import noise
from data_handler.signal_features import compute_periodogram
from plotter.plot_handler import plot_f_space
from data_handler.signal_features import background_model, nyqFreq,boxcar_smoothing

'''
The prior calculator computes initial guesses for the priors, which then can be used as Priors for DIAMONDS.
Most of the equations here are taken from the paper by Kallinger(2014), others are determined empirically. All of
the values are initial guesses. Proper values can be determined by fitting the PSD
'''


def first_harvey(nu_max: float) -> float:
    """
    Computes first harvey frequency
    :param nu_max: nu_max value determined by pipe
    :return: First harvey
    """
    k = 19.51
    s = -0.071

    return k * pow(nu_max, s)


def second_harvey(nu_max: float) -> float:
    """
    Computes second harvey frequency
    :param nu_max: nu_max value determined by pipe
    :return: Second harvey
    """
    k = 0.317
    s = 0.970
    return k * pow(nu_max, s)


def third_harvey(nu_max: float) -> float:
    """
    Computes third harvey frequency
    :param nu_max: nu_max value determined by pipe
    :return: Third harvey
    """
    k = 0.948
    s = 0.992
    return k * pow(nu_max, s)


def harvey_amp(nu_max: float) -> float:
    """
    Computes harvey amplitude
    :param nu_max: nu_max value determined by pipe
    :return: amplitude of harvey
    """
    k = 3383
    s = -0.609

    return k * pow(nu_max, s)


def sigma(nu_max: float) -> float:
    """
    Computes envelope of oscillation
    :param nu_max: nu_max value determined by pipe
    :return: envelope of oscillation
    """

    k = 1.124
    s = 0.505

    return k * pow(nu_max, s)


def amp(nu_max: float, sigma: float, f_data: np.ndarray):
    """
    Computes amplitude by using the highest value in the oscillation region
    :param nu_max: nu_max determined by pipe
    :param sigma: envelope of signal
    :param f_data: f_data periodogram
    :return: amplitude of oscillation
    """
    f_data = boxcar_smoothing(f_data)
    x = f_data[0]
    y = f_data[1]
    region = y[np.logical_and(x > (nu_max - sigma), x < (nu_max + sigma))]
    return np.max(region)


def priors(nu_max: float, data: np.ndarray, kwargs: Dict):
    """
    Returns a List of priors for DIAMONDS.
    :param nu_max: nu_max determined by pipe
    :param photon_noise: photon_noise determined in signal_features
    :return: List of Lists of priors in correct order
    """
    f_data = compute_periodogram(data)

    bg_model = background_model(f_data, nyqFreq(data), noise(f_data), harvey_amp(nu_max), first_harvey(nu_max),
                                harvey_amp(nu_max), second_harvey(nu_max), harvey_amp(nu_max), third_harvey(nu_max),
                                nu_max, amp(nu_max, sigma(nu_max), f_data), sigma(nu_max))

    params = {
        'w':noise(f_data),
        'sigma_1':harvey_amp(nu_max),
        'b_1':first_harvey(nu_max),
        'sigma_2':harvey_amp(nu_max),
        'b_2':second_harvey(nu_max),
        'sigma_3':harvey_amp(nu_max),
        'b_3':third_harvey(nu_max),
        'nu_max':nu_max,
        'H_osc':amp(nu_max, 2*sigma(nu_max), f_data),
        'sigma':sigma(nu_max)
    }

    plot_f_space(f_data, kwargs, bg_model=bg_model,plot_name="PSD_guess")

    return [
        [0.5 * noise(f_data)                        , 5 * noise(f_data)],
        [0.6 * harvey_amp(nu_max)                   , 3 * harvey_amp(nu_max)],
        [0.2 * first_harvey(nu_max)                , 1.3 * first_harvey(nu_max)],
        [0.6 * harvey_amp(nu_max)                   , 3 * harvey_amp(nu_max)],
        [0.3 * second_harvey(nu_max)              , 1.2 * second_harvey(nu_max)],
        [0.6 * harvey_amp(nu_max)                   , 3 * harvey_amp(nu_max)],
        [0.2 * third_harvey(nu_max)                 , 1.4 * third_harvey(nu_max)],
        [0.7 * amp(nu_max, sigma(nu_max), f_data)  , 1.5 * amp(nu_max, sigma(nu_max), f_data)],
        [0.7 * nu_max                               , 1.3 * nu_max],
        [0.7 * sigma(nu_max)                       , 1.3 * sigma(nu_max)]
    ],params
