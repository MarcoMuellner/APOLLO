# standard imports
from typing import Tuple, Dict, Union
# scientific imports
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
# project imports
from fitter.fit_functions import trismooth, sinc, sin, sinc_sin
from data_handler.signal_features import get_time_step
from plotter.plot_handler import plot_peridogramm_from_timeseries, plot_acf_fit, plot_nu_max_fit
from support.printer import print_int
from uncertainties import ufloat, unumpy as unp
from evaluators.compute_priors import noise
from fitter.fit_functions import quadraticPolynomial
from res.conf_file_str import internal_teff, internal_mag_value, internal_path
from data_handler.signal_features import compute_periodogram
from FLIPER.FLIPER import FLIPER, ML
from background_file_handler.backgroundResults import BackgroundResults
from evaluators.compute_delta_nu import _butter_lowpass_filtfilt, perform_fit
from data_handler.signal_features import nyqFreq,rebin
import warnings


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
    mask = data[0] < 100
    corr = np.correlate(data[1][mask], data[1][mask], mode='full')
    corr = corr[corr.size // 2:]
    corr /= max(corr)
    corr = corr ** 2
    return np.array((data[0][mask][1:] * 60, corr))


def interpolate_acf(x: np.ndarray, y: np.ndarray, points: int) -> Tuple[np.ndarray, np.ndarray]:
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

    return np.array(x_list), np.array(y_list)


def fliper_fit():
    popt = [4.49655352, -0.20225283, -0.21813857, 0.02360209]
    perr = [0.03963379, 0.04525751, 0.01511792, 0.00148213]
    return [ufloat(val, err) for val, err in zip(popt, perr)]


def compute_fliper_guess(f_data: np.ndarray, kwargs: Dict) -> Union[float, None]:
    if internal_teff in kwargs.keys():
        T_eff = kwargs[internal_teff]
    else:
        return None

    mask_high = f_data[0] < 277

    F_p_list = []
    for lower_f, weight in [(0.7, 78), (7, 8), (0.2, 7), (50, 4), (20, 2)]:
        mask = np.logical_and(f_data[0] > lower_f, mask_high)
        F_p = np.mean(f_data[1][mask]) - noise(np.array((f_data[0][mask], f_data[1][mask])))
        F_p_list.append((F_p, weight))

    F_p_list = np.array(F_p_list).T
    F_p = np.average(F_p_list.T[0], weights=F_p_list.T[1])

    log_g = quadraticPolynomial(np.log10(F_p), *fliper_fit())

    t_sun = 5778
    nu_max_sun = 3090
    logg_sun = 4.44

    nu_max = (10 ** log_g / 10 ** logg_sun) * 1 / unp.sqrt(T_eff / t_sun) * nu_max_sun
    return nu_max.nominal_value


def compute_fliper_exact(data: np.ndarray, kwargs: Dict) -> Union[float, None]:
    if internal_teff in kwargs.keys():
        T_eff = kwargs[internal_teff]
    else:
        return None

    if internal_mag_value in kwargs.keys():
        mag = kwargs[internal_mag_value]
    else:
        return None

    if np.median(data[0][1:] - data[0][:-1])*24*60 < 10: #arbitrary, far below 30 minutes, but a bit above 1
        temp_data = np.array((rebin(data[0],30),rebin(data[1],30)))
    else:
        temp_data = data

    data_f = compute_periodogram(temp_data, kwargs)

    mask = data_f[0] < 277
    mask_20 = np.logical_and(mask,data_f[0] > (10 ** 6 / (20 * 24 * 3600)))
    mask_80 = np.logical_and(mask,data_f[0] > (10 ** 6 / (80 * 24 * 3600)))
    data_f_new_20 = np.array((data_f[0][mask_20], data_f[1][mask_20]))
    data_f_new_80 = np.array((data_f[0][mask_80], data_f[1][mask_80]))
    data_f_new_20[0] /= 10 ** 6
    data_f_new_80[0] /= 10 ** 6

    Fliper_20_d = FLIPER(kwargs).Fp_20_days(data_f_new_20.T, mag)
    Fliper_80_d = FLIPER(kwargs).Fp_80_days(data_f_new_80.T, mag)
    Fp02 = Fliper_80_d.fp02[0]
    Fp07 = Fliper_20_d.fp07[0]
    Fp7 = Fliper_20_d.fp7[0]
    Fp20 = Fliper_20_d.fp20[0]
    Fp50 = Fliper_20_d.fp50[0]
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore",category=DeprecationWarning)
        numax = 10 ** (ML().PREDICTION(T_eff, mag, Fp02, Fp07, Fp7, Fp20, Fp50,
                                       f"{kwargs[internal_path]}/FLIPER/ML_numax_training_paper"))

    return float(numax[0])


def compute_fliper_nu_max(f_data: np.ndarray, kwargs: Dict) -> Union[float, None]:
    ret_dict = {}
    ret_dict["Fliper rough"] = compute_fliper_guess(f_data, kwargs)
    ret_dict["Fliper exact"] = compute_fliper_exact(f_data, kwargs)
    return ret_dict


def fit_acf(data: np.ndarray, kwargs: Dict) -> Tuple[float, float, float]:
    """
    Tries to fit a*sinc^2(4*tau/tau_acf) + a_s*sin(2*pi*4*tau/tau_acf)
    :param data: Autocorrelated signal, t in minutes
    :return: Fit values for a,tau_acf and a_s
    """

    # restrict your fit range to be able to fit better!
    peak, _ = find_peaks(data[1])
    tau_guess = 4 * data[0][peak[1]] / np.pi  # use first zero peak for a guess of tau!

    x = data[0][:peak[1]]  # restrict up to third peak
    y = data[1][:peak[1]]

    while np.abs(1 - y[0]) < 0.1 or np.any(y > 1):
        x = x[1:]
        y = y[1:]

    x_without_int = x
    y_without_int = y

    x, y = interpolate_acf(x, y, 1)  # interpolate acf to make fit work better

    plot_x = np.linspace(0, max(x), 4000)

    p0_sinc_initial = [max(y), tau_guess]
    bounds = ([0, 0], [1, np.inf])

    # initial sinc fit
    sinc_initial_popt, _ = curve_fit(sinc, x, y, p0=p0_sinc_initial, bounds=bounds)
    residuals = y - sinc(x, *sinc_initial_popt)

    # use residuals of fit to determine sin fit
    p0 = [max(residuals), sinc_initial_popt[1]]
    sin_popt, _ = curve_fit(sin, x, residuals, p0=p0, bounds=bounds)

    # Subtract sin fit from original dataset and try to fit sinc again
    sin_residuals = y - sin(x, *sin_popt)
    p0_sinc_final = [1, p0_sinc_initial[1]]
    sinc_final_popt, _ = curve_fit(sinc, x, sin_residuals, p0=p0_sinc_final, bounds=bounds)

    p0_full = [sinc_final_popt[0], sinc_final_popt[1], sin_popt[0]]
    bounds = ([0, 0, 0], [1, np.inf, 1])

    sinc_full_popt, _ = curve_fit(sinc_sin, x, y, p0=p0_full, bounds=bounds)

    full_fit = sinc_sin(plot_x, *sinc_full_popt)

    plot_acf_fit(np.array((x, y)), np.array((plot_x, full_fit)), sinc_final_popt[1], kwargs,
                 np.array((plot_x, sinc(plot_x, *p0_sinc_initial))))

    np.savetxt(f"ACF_{'%.2f' % f_from_tau(sinc_final_popt[1])}.txt", np.array((x_without_int, y_without_int)))
    np.savetxt(f"Fit_parameter_sinc_{'%.2f' % f_from_tau(sinc_final_popt[1])}.txt", np.array(sinc_final_popt))
    np.savetxt(f"Fit_parameter_sin_{'%.2f' % f_from_tau(sinc_final_popt[1])}.txt", np.array(sin_popt))

    return sinc_full_popt[0], sinc_full_popt[2], sinc_full_popt[1]


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


def compute_nu_max(data: np.ndarray, f_flicker: float, kwargs: Dict) -> Tuple[
    float, Dict[str, float], Union[float, None]]:
    """
    Performs the full procedure introduced by Kallinger (2016)
    :param data: Full dataset from the lightcurve
    :param f_flicker: flicker frequency from the flicker amplitude. In uHz
    :return: guess for nu_max. In uHz
    """

    f_fliper = compute_fliper_nu_max(compute_periodogram(data, kwargs), kwargs)
    if f_fliper != {}:
        if "Fliper exact" in f_fliper.keys():
            f = f_fliper["Fliper exact"]
        else:
            f = f_fliper["Fliper rough"]

        return f, {}, f_fliper

    f_list = []

    f_list.append((f_flicker, rf"F_flicker_{'%.2f' % f_flicker}$\mu Hz$"))
    plot_peridogramm_from_timeseries(data, kwargs, True, f_list)
    print_int(f"Flicker frequency {'%.2f' % f_flicker}", kwargs)

    tau = single_step_procedure(data, (f_to_t(f_flicker) / 60) + 5, kwargs)
    f = f_from_tau(tau)
    print_int(f"1. frequency {'%.2f' % f}", kwargs)

    f_list.append((f, rf"F_filter_0_{'%.2f' % f}$\mu Hz$"))
    plot_peridogramm_from_timeseries(data, kwargs, True, f_list)

    # for frequencies below 70 the first guess seems good enough
    n = 1

    # repeat process n-times
    for i in range(0, n):
        try:
            f_guess = np.amax([f_list[-2][0], f_list[-1][0]]) - (1 / 3) * np.abs(f_list[-1][0] - f_list[-2][0])
            tau = single_step_procedure(data, (f_to_t(f_guess) / 60), kwargs)
        except ValueError:
            break
        f_new = f_from_tau(tau)
        f = f_new

        print_int(f"{i + 2}. frequency {'%.2f' % f}", kwargs)

        f_list.append((f, rf"F_filter_{i + 1}_{'%.2f' % f}$\mu Hz$"))
        plot_peridogramm_from_timeseries(data, kwargs, True, f_list)

    print_int(f"Nu_max: {'%.2f' % f}", kwargs)

    f_list_ret = {}
    for val, name in f_list:
        f_list_ret[name] = val

    f_fliper = compute_fliper_nu_max(compute_periodogram(data, kwargs), kwargs)
    if f_fliper != {}:
        if "Fliper exact" in f_fliper.keys():
            f = f_fliper["Fliper exact"]
        else:
            f = f_fliper["Fliper rough"]

    return f, f_list_ret, f_fliper


def look_for_nu_max_osc_region(data: np.ndarray, kwargs: Dict) -> ufloat:
    result = BackgroundResults(kwargs, runID="FullBackground")
    model = result.createBackgroundModel()

    f_data = compute_periodogram(data, kwargs)

    background = np.sum(model[:3], axis=0)

    cleared_data = np.divide(f_data[1], background)
    cleared_data = _butter_lowpass_filtfilt(cleared_data, nyqFreq(data),
                                            0.267 * pow(result.nuMax.nominal_value, 0.760) * 10)

    mask = np.logical_and(f_data[0] > (result.nuMax - 1 * result.sigma).nominal_value,
                          f_data[0] < (result.nuMax + 1 * result.sigma).nominal_value)

    f_x = f_data[0][mask]
    f_y = cleared_data[mask]

    popt, perr = perform_fit(f_x, f_y, kwargs)

    plot_nu_max_fit(np.array((f_x, f_y)), popt, result.nuMax.nominal_value, kwargs)
    return ufloat(popt[2], (perr[2] + popt[3] + perr[3]))
