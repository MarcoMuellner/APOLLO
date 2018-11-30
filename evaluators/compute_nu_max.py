# standard imports
from typing import Tuple
# scientific imports
import numpy as np
from scipy.signal import argrelextrema
from scipy.optimize import curve_fit
# project imports
from fitter.fit_functions import trismooth, sinc, sin
from evaluators.compute_flicker import get_time_step


def f_to_t(f: float) -> float:
    """
    Convertrs frequency to time.
    :param f: Frequency in uHz
    :return: Time in seconds
    """
    return 10 ** 6 / f


def t_to_f(t: float) -> float:
    """
    Converts time to frequency
    :param t: Time in seconds
    :return: Frequency in uHz
    """
    return 10 ** 6 / t


def filter_lightcurve(data: np.ndarray, tau: float) -> np.ndarray:
    """
    Filters a given lightcurve with frequency f using trismooth.
    :param data: Lightcurve dataset
    :param tau: Tau in minutes
    :return: Filtered dataset
    """
    t = tau / (60*24)
    bin_size = int(np.round(tau / get_time_step(data)))
    filtered_y = data[1] - trismooth(data[1], bin_size)

    return np.array((data[0], filtered_y))


def compute_acf(data: np.ndarray) -> np.ndarray:
    """
    Computes the autocorrelation function from a given dataset by autocorrelating the data with itself. Assumption
    is that x-Axis is in days
    :param data: Dataset that is autocorrelated.
    :return: ACF signal. Time is in minutes!!
    """
    corr = np.correlate(data[1], data[1], mode='full')
    corr = corr[corr.size // 2:]
    corr /= max(corr)
    corr = corr ** 2
    return np.array((data[0][1:] * 24 * 60, corr))


def fit_acf(data: np.ndarray, tau_guess: float) -> Tuple[float, float, float]:
    """
    Tries to fit a*sinc^2(4*tau/tau_acf) + a_s*sin(2*pi*4*tau/tau_acf)
    :param data: Autocorrelated signal, t in minutes
    :param tau_guess: An initial guess for the tau_acf variable. In minutes!
    :return: Fit values for a,tau_acf and a_s
    """

    # restrict your fit range to be able to fit better!
    minima = argrelextrema(data[1], np.less)[0][0]
    minima_factor = np.round(30 * np.exp(-minima / 3) + minima)
    x = data[0][:minima_factor]
    y = data[1][:minima_factor]

    # start with maximum of y!
    x = x[int(np.where(y == max(y))[0]):]
    y = y[int(np.where(y == max(y))[0]):]

    p0_sinc_initial = [1, tau_guess]
    bounds = ([0, 0], [1, np.inf])

    # initial sinc fit
    sinc_initial_popt, _ = curve_fit(sinc, x, y, p0=p0_sinc_initial, bounds=bounds)
    residuals = y - sinc(x, *sinc_initial_popt)

    # use residuals of fit to determine sin fit
    p0 = [max(residuals), sinc_initial_popt[1]]
    sin_popt, _ = curve_fit(sin, x, residuals, p0=p0)

    # Subtract sin fit from original dataset and try to fit sinc again
    sin_residuals = y - sin(x, *sin_popt)
    p0_sinc_final = [1, p0_sinc_initial[1]]
    sinc_final_popt, _ = curve_fit(sinc, x, sin_residuals, p0=p0_sinc_final, bounds=bounds)

    return sinc_final_popt[0],sin_popt[0],sinc_final_popt[2]

def f_from_tau(tau : float) -> float:
    """
    Computes the frequencies from the tau of the ACF
    :param tau: Tau given by the acf in minutes
    :return: frequency in uHz
    """
    log_y = 3.098 - 0.932 * np.log10(tau) - 0.025 * (np.log10(tau)) ** 2
    return 10** log_y

def single_step_procedure(data : np.ndarray, tau : float) -> float:
    """
    Performs a single step from the iterative procedure described in Kallinger (2016)
    :param data: Dataset of the lightcurve.
    :param tau: Tau determined by a previous iteration or by flicker amplitude. In minutes!
    :return: Improved Tau
    """
    #filter lightcurve
    filtered_data = filter_lightcurve(data,tau)
    #compute acf
    acf = compute_acf(filtered_data)
    #fit acf
    _,_,tau_acf = fit_acf(acf,tau/60)
    return tau_acf

def compute_nu_max(data : np.ndarray, f_flicker : float) -> float:
    """
    Performs the full procedure introduced by Kallinger (2016)
    :param data: Full dataset from the lightcurve
    :param f_flicker: flicker frequency from the flicker amplitude. In uHz
    :return: guess for nu_max. In uHz
    """
    tau = single_step_procedure(data,f_to_t(f_flicker)/60)
    f = f_from_tau(tau)

    #repeat process twice
    for _ in range(0,2):
        tau = single_step_procedure(data,f_to_t(f)/60)
        f = f_from_tau(tau)

    return f





