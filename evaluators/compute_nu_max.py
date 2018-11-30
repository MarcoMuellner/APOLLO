# standard imports
from typing import Tuple, Dict
# scientific imports
import numpy as np
from scipy.signal import argrelextrema
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
# project imports
from fitter.fit_functions import trismooth, sinc, sin
from readerWriter.signal_features import get_time_step
from plotter.plot_handler import plot_peridogramm_from_timeseries, plot_acf_fit


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


def filter_lightcurve(data: np.ndarray, tau: float, kwargs: Dict) -> np.ndarray:
    """
    Filters a given lightcurve with frequency f using trismooth.
    :param data: Lightcurve dataset
    :param tau: Tau in minutes
    :return: Filtered dataset
    """
    t = tau / (60 * 24)
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
    return np.array((data[0][1:] * 60, corr))


def interpolate_acf(x : np.ndarray,y : np.ndarray, points: int) -> Tuple[np.ndarray,np.ndarray]:
    """
    Interpolates an acf signal with n given points between them
    :param x: time axis of ACF
    :param y: ACF values
    :param points: number of points to be added
    :return: x,y with new amount of points
    """
    x_list = [x[0]]
    y_list = [y[0]]

    divisor = (1 + points)
    for i in range(1, len(x)):
        for j in range(1, points + 2):  # first point, second point, ..., n-1 point and final point
            x_list.append(x[i - 1] + j * (x[i] - x[i - 1]) / divisor)
            y_list.append(y[i - 1] + j * (y[i] - y[i - 1]) / divisor)

    return np.array(x_list),np.array(y_list)


def fit_acf(data: np.ndarray,  kwargs: Dict) -> Tuple[float, float, float]:
    """
    Tries to fit a*sinc^2(4*tau/tau_acf) + a_s*sin(2*pi*4*tau/tau_acf)
    :param data: Autocorrelated signal, t in minutes
    :return: Fit values for a,tau_acf and a_s
    """

    # restrict your fit range to be able to fit better!
    peak,_ = find_peaks(data[1])
    tau_guess = 4*data[0][peak[1]]/np.pi #use first zero peak for a guess of tau!

    x = data[0][:peak[3]] #restrict up to third peak
    y = data[1][:peak[3]]

    x,y = interpolate_acf(x,y,2) #interpolate acf to make fit work better

    while np.abs(1 - y[0]) < 0.1 or np.any(y > 1):
        x = x[1:]
        y = y[1:]

    plot_x = np.linspace(0, max(x), 4000)

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

    full_fit = sinc(plot_x, *sinc_final_popt) + sin(plot_x, *sin_popt)

    plot_acf_fit(np.array((x, y)), np.array((plot_x,full_fit)), sinc_final_popt[1], kwargs,
                 np.array((plot_x, sinc(plot_x, *p0_sinc_initial))))

    return sinc_final_popt[0], sin_popt[0], sinc_final_popt[1]


def f_from_tau(tau: float) -> float:
    """
    Computes the frequencies from the tau of the ACF
    :param tau: Tau given by the acf in minutes
    :return: frequency in uHz
    """
    log_y = 3.098 - 0.932 * np.log10(tau) - 0.025 * (np.log10(tau)) ** 2
    return 10 ** log_y


def single_step_procedure(data: np.ndarray, tau: float, kwargs: Dict) -> float:
    """
    Performs a single step from the iterative procedure described in Kallinger (2016)
    :param data: Dataset of the lightcurve.
    :param tau: Tau determined by a previous iteration or by flicker amplitude. In minutes!
    :return: Improved Tau
    """
    # filter lightcurve
    filtered_data = filter_lightcurve(data, tau / 60 / 24, kwargs)
    plot_peridogramm_from_timeseries(filtered_data, kwargs, True)
    # compute acf
    acf = compute_acf(filtered_data)
    # fit acf
    _, _, tau_acf = fit_acf(acf, kwargs)
    return tau_acf


def compute_nu_max(data: np.ndarray, f_flicker: float, kwargs: Dict) -> float:
    """
    Performs the full procedure introduced by Kallinger (2016)
    :param data: Full dataset from the lightcurve
    :param f_flicker: flicker frequency from the flicker amplitude. In uHz
    :return: guess for nu_max. In uHz
    """
    f_list = []
    f_list.append((f_flicker, rf"F_flicker_{'%.2f' % f_flicker}$\mu Hz$"))
    plot_peridogramm_from_timeseries(data, kwargs, True, f_list)
    tau = single_step_procedure(data, f_to_t(f_flicker) / 60, kwargs)
    f = f_from_tau(tau)
    f_list.append((f, rf"F_filter_0_{'%.2f' % f}$\mu Hz$"))
    plot_peridogramm_from_timeseries(data, kwargs, True, f_list)

    # repeat process twice
    for i in range(0, 2):
        tau = single_step_procedure(data, f_to_t(f) / 60, kwargs)
        f = f_from_tau(tau)

        f_list.append((f, rf"F_filter_{i + 1}_{'%.2f' % f}$\mu Hz$"))
        plot_peridogramm_from_timeseries(data, kwargs, True, f_list)

    print(f)
    return f
