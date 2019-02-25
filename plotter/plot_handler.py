# standard imports
from typing import Dict, List, Tuple
import os
# scientific imports
import numpy as np
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
# project imports
from res.conf_file_str import general_kic, plot_show, plot_save,internal_noise_value
from fitter.fit_functions import gaussian
from data_handler.signal_features import compute_periodogram, boxcar_smoothing
from background.backgroundResults import BackgroundResults
from fitter.fit_functions import gaussian_amp

pl.rc('font', family='serif')
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')

def get_appendix(kwargs : Dict):
    appendix = ""

    if general_kic in kwargs.keys():
        appendix += f"_{kwargs[general_kic]}_"

    if internal_noise_value in kwargs.keys():
        appendix += f"n_{kwargs[internal_noise_value]}_"

    return appendix


def add_subplot_axes(ax: Axes, rect: List[float]) -> Axes:
    """
    Adds a subplot axes within a given rect
    :param ax: axes to work from
    :param rect: rectangle
    :return: subaxis
    """
    fig = pl.gcf()
    box = ax.get_position()
    width = box.width
    height = box.height
    inax_position = ax.transAxes.transform(rect[0:2])
    transFigure = fig.transFigure.inverted()
    infig_position = transFigure.transform(inax_position)

    x = infig_position[0]
    y = infig_position[1]
    width *= rect[2]
    height *= rect[3]

    subax = fig.add_axes([x, y, width, height])
    subax.set_facecolor('white')

    x_labelsize = subax.get_xticklabels()[0].get_size()
    y_labelsize = subax.get_yticklabels()[0].get_size()

    x_labelsize *= rect[2] ** 0.5
    y_labelsize *= rect[3] ** 0.5

    subax.xaxis.set_tick_params(labelsize=x_labelsize)
    subax.yaxis.set_tick_params(labelsize=y_labelsize)
    return subax


def save_fig(fig: Figure, name: str):
    """
    Saves a given figure and closes it.
    :param fig: Figure
    :param name: Name of plot
    """
    try:
        os.mkdir("images")
    except FileExistsError:
        pass

    fig.savefig(f"images/{name}.png")

def plot_parameter_trend(data_dict : Dict[str,Tuple[np.ndarray,str]],kwargs : Dict):
    """
    Plots the parameter trend for all parameters
    :param data_dict: Data Dict containing name and values
    :param kwargs: Run conf
    """

    fig : Figure = pl.figure(figsize=(20, 9))
    y = len(data_dict) // 2 +1
    n = 1
    for name, (values, unit) in data_dict.items():
        try:
            ax : Axes = fig.add_subplot(2,y,n,sharex=ax)
        except UnboundLocalError:
            ax: Axes = fig.add_subplot(2, y, n)
        ax.plot(values,'o',color='k',markersize=1)
        ax.set_xlabel("Iteration")
        ax.set_ylabel(unit)
        ax.set_title(name)
        n+=1
    fig.suptitle(f"Parameter progression{get_appendix(kwargs)}")

    if plot_show in kwargs.keys() and kwargs[plot_show]:
        pl.show(fig)

    if plot_save in kwargs.keys() and kwargs[plot_save]:
        save_fig(fig, f"Parameter_trend_n={len(data_dict)}{get_appendix(kwargs)}")

    pl.close(fig)


def plot_marginal_distributions(data_dict : Dict[str,Tuple[np.ndarray,str]],kwargs : Dict):
    fig : Figure = pl.figure(figsize=(20, 9))
    y = len(data_dict) // 2 +1
    n = 1
    for name, ((par,marg,fill_x,fill_y,par_err,par_median), unit) in data_dict.items():
        try:
            ax : Axes = fig.add_subplot(2,y,n)
        except UnboundLocalError:
            ax: Axes = fig.add_subplot(2, y, n)

        if par_median is not None:
            ax.set_xlim(par_median-5*par_err,par_median+5*par_err)
        ax.set_ylim(0,max(marg)*1.2)
        ax.plot(par, marg,linewidth=2,c='k')
        if fill_x is not None and fill_y is not None:
            ax.fill_between(fill_x,fill_y,0,alpha=0.5,facecolor='green')
        if par_median is not None:
            ax.axvline(par_median,c='r')
        ax.set_xlabel(unit,fontsize=16)
        ax.set_title(name)
        n +=1

    if plot_show in kwargs.keys() and kwargs[plot_show]:
        pl.show(fig)

    if plot_save in kwargs.keys() and kwargs[plot_save]:
        save_fig(fig, f"Marginal_distibution_n={len(data_dict)}{get_appendix(kwargs)}")

    pl.close(fig)



def plot_interpolation(data : np.ndarray, gap_list : List[int],kwargs : Dict):
    """
    Plots the interpolated points in a lightcurve
    :param data: dataset
    :param gap_list: list of gap ids that were filled
    :param kwargs: Run conf
    """
    fig: Figure = pl.figure(figsize=(10, 6))
    ax: Axes = fig.add_subplot(111)

    if general_kic in kwargs.keys():
        ax.set_title(f"KIC{kwargs[general_kic]}")

    ax.plot(data[0], data[1], 'o', color='k', markersize=2,label = "Datapoints")  # plot data
    ax.plot(data[0][gap_list], data[1][gap_list], 'o', color='red', markersize=2,label = "Interpolation")
    ax.set_xlabel("Time (days)")
    ax.set_ylabel("Flux")
    ax.legend()

    if plot_show in kwargs.keys() and kwargs[plot_show]:
        pl.show(fig)

    if plot_save in kwargs.keys() and kwargs[plot_save]:
        save_fig(fig, f"Lightcurve_interpolation{get_appendix(kwargs)}")

    pl.close(fig)
    # plot data

def plot_noise_residual(original_data : np.ndarray, noisy_data: np.ndarray, kwargs : Dict):
    fig: Figure = pl.figure(figsize=(10, 6))

    fig.suptitle(f"Noise residual{get_appendix(kwargs)}")
    ax: Axes = fig.add_subplot(1,3,1)

    ax.plot(original_data[0],original_data[1],'x',color='k',markersize=2)
    ax.set_title("Original lighcurve")
    ax.set_xlabel("Time (days)")
    ax.set_ylabel("Flux")

    ax: Axes = fig.add_subplot(1, 3, 2)
    ax.plot(noisy_data[0],noisy_data[1],'o',color='k',markersize=2)
    ax.set_title("Noisy lightcrurve")
    ax.set_xlabel("Time (days)")

    res = noisy_data[1] - original_data[1]
    ax: Axes = fig.add_subplot(1, 3, 3)
    ax.plot(original_data[0],res,'x',color='k',markersize=2)
    ax.set_title("Residual")
    ax.set_xlabel("Time(days")

    if plot_show in kwargs.keys() and kwargs[plot_show]:
        pl.show(fig)

    if plot_save in kwargs.keys() and kwargs[plot_save]:
        save_fig(fig, f"Lightcurve_noise_analysis{get_appendix(kwargs)}")

    pl.close(fig)




def plot_sigma_clipping(data: np.ndarray, bins: np.ndarray, hist: np.ndarray, popt: List[float], kwargs: Dict):
    """
    Plots the sigma clipping
    :param data: Dataset of lightcurve
    :param bins: bins from histogram
    :param hist: histogram values
    :param popt: fit from gaussian
    :param kwargs: Run configuration
    """
    fig: Figure = pl.figure(figsize=(10, 6))
    ax: Axes = fig.add_subplot(111)

    if general_kic in kwargs.keys():
        ax.set_title(f"KIC{get_appendix(kwargs)}")

    rect = [0.7, 0.08, 0.3, 0.3]
    ax1: Axes = add_subplot_axes(ax, rect)

    ax.plot(data[0], data[1], 'o', color='k', markersize=2)  # plot data
    ax.set_facecolor('white')

    ax1.plot(bins, hist, 'x', color='k', markersize=4)  # plot histogram

    lin = np.linspace(np.min(bins), np.max(bins), len(bins) * 5)
    ax1.plot(lin, gaussian(lin, *popt))

    (cen, wid) = (popt[1], popt[2])
    sigma = 5  # used by the fit!
    ax1.axvline(cen - sigma * wid, ls='dashed', color='k')
    ax1.axvline(cen + sigma * wid, ls='dashed', color='k')

    ax.set_xlabel("Time (days)")
    ax.set_ylabel("Flux")
    ax1.set_xlabel('Delta F')
    ax1.set_ylabel(r'N')

    ax1.set_xlim((cen - sigma * wid * 1.2), (cen + sigma * wid * 1.2))

    if plot_show in kwargs.keys() and kwargs[plot_show]:
        pl.show(fig)

    if plot_save in kwargs.keys() and kwargs[plot_save]:
        save_fig(fig, f"Lightcurve_sigma_clipping{get_appendix(kwargs)}")

    pl.close(fig)


def plot_f_space(f_data: np.ndarray, kwargs: dict, add_smoothing: bool = False, f_list: List[Tuple[float, str]] = None,
                 bg_model: List[np.ndarray] = None, plot_name: str = None):
    """
    Plots the psd.
    :param f_data: Frequency domain data
    :param kwargs: Run configuration
    :param add_smoothing: Show smoothing
    :param f_list: List of frequency markers
    """
    fig: Figure = pl.figure(figsize=(10, 6))
    ax: Axes = fig.add_subplot(111)
    ax.loglog(f_data[0], f_data[1], linewidth=1, color='k')

    if plot_name is None:
        name = "PSD"
    else:
        name = plot_name

    if general_kic in kwargs.keys():
        ax.set_title(f"KIC{get_appendix(kwargs)}")

    ax.set_ylabel(r'PSD [ppm$^2$/$\mu$Hz]')
    ax.set_xlabel(r'Frequency [$\mu$Hz]')

    if add_smoothing:
        smoothed_data = boxcar_smoothing(f_data, 700)
        ax.loglog(smoothed_data[0], smoothed_data[1], linewidth=1, color='green', alpha=0.5)

    if bg_model is not None:
        ax.loglog(f_data[0], bg_model[0], color='b', linewidth=1, linestyle='--')  # harvey 1
        ax.loglog(f_data[0], bg_model[1], color='b', linewidth=1, linestyle='--')  # harvey 2
        ax.loglog(f_data[0], bg_model[2], color='b', linewidth=1, linestyle='--')  # harvey 3
        ax.loglog(f_data[0], bg_model[3], color='y', linewidth=1, linestyle=':')  # noise
        ax.loglog(f_data[0], np.sum(bg_model[0:4], axis=0), color='r', linewidth=1, linestyle='-')  # without Powerexcess
        if len(bg_model) == 5:
            ax.loglog(f_data[0], bg_model[4], color='c', linewidth=1, linestyle=':')  # power
            ax.loglog(f_data[0], np.sum(bg_model, axis=0), color='r', linewidth=1, linestyle='-')  # with Powerexcess
            name += f"_full_fit"
        else:
            name += f"_noise_fit"

    name +=get_appendix(kwargs)

    color = iter(pl.cm.rainbow(np.linspace(0, 1, 10)))
    if f_list is not None:
        name += f"_n_{len(f_list)}"
        for f, f_name in f_list:
            ax.axvline(x=f, linestyle='--', linewidth=1, label=f_name, color=next(color))

    if f_list is not None:
        pl.legend()
    ax.set_xlim(min(f_data[0]), max(f_data[0]))
    ax.set_ylim(min(f_data[1] * 0.95), max(f_data[1]) * 1.2)

    if plot_show in kwargs.keys() and kwargs[plot_show]:
        pl.show(fig)

    if plot_save in kwargs.keys() and kwargs[plot_save]:
        save_fig(fig, name)
    pl.close(fig)


def plot_peridogramm_from_timeseries(data: np.ndarray, kwargs: dict, add_smoothing: bool = False,
                                     f_list: List[Tuple[float, str]] = None,
                                     bg_model: List[np.ndarray] = None, plot_name: str = None):
    """
    Directly converts a timeseries and plots it in frequency space
    :param data: Timeseries
    :param kwargs: Run configuration
    :param add_smoothing: Show smoothing
    :param f_list: List of frequency markers
    """
    f_space = compute_periodogram(data,kwargs)
    plot_f_space(f_space, kwargs, add_smoothing, f_list,bg_model,plot_name)


def plot_acf_fit(acf: np.ndarray, fit: np.ndarray, tau: float, kwargs: Dict, guess: np.ndarray = None):
    fig: Figure = pl.figure(figsize=(10, 6))
    ax: Axes = fig.add_subplot(111)

    if general_kic in kwargs.keys():
        ax.set_title(f"KIC{get_appendix(kwargs)}")

    pl.plot(acf[0], acf[1], 'x', color='k', markersize=2)
    pl.plot(fit[0], fit[1], color='red', linewidth=1.5, label="Fit")
    if guess is not None:
        pl.plot(guess[0], guess[1], color='green', linewidth=1.5, label='Guess')

    pl.xlabel("Time(min)")
    pl.ylabel("ACF")
    pl.legend()
    if plot_show in kwargs.keys() and kwargs[plot_show]:
        pl.show(fig)

    if plot_save in kwargs.keys() and kwargs[plot_save]:
        save_fig(fig, f"Fit_{10 ** 6 / tau}{get_appendix(kwargs)}")
    pl.close(fig)

def plot_delta_nu_acf(data : np.ndarray,delta_nu : float,kwargs):
    fig: Figure = pl.figure(figsize=(10, 6))
    ax: Axes = fig.add_subplot(111)

    if general_kic in kwargs.keys():
        ax.set_title(f"KIC{get_appendix(kwargs)}")

    pl.plot(data[0],data[1],color='k',linewidth=2)
    pl.axvline(x=delta_nu,linestyle='dashed',color='red',linewidth=2)
    pl.xlabel("Frequency ($\mu$Hz)")
    pl.ylabel("ACF")
    if plot_show in kwargs.keys() and kwargs[plot_show]:
        pl.show(fig)

    if plot_save in kwargs.keys() and kwargs[plot_save]:
        save_fig(fig, f"ACF_Delta_nu_{get_appendix(kwargs)}")
    pl.close(fig)

def plot_delta_nu_fit(data : np.ndarray, popt : List[float],kwargs : Dict):
    fig: Figure = pl.figure(figsize=(10, 6))
    ax: Axes = fig.add_subplot(111)

    if general_kic in kwargs.keys():
        ax.set_title(f"KIC{get_appendix(kwargs)}")

    pl.plot(data[0],data[1],color='k',linewidth=2)
    pl.plot(data[0],gaussian_amp(data[0],*popt),color='red',linewidth=2)
    pl.axvline(x=popt[2],linestyle='dashed',color='blue',linewidth=2)
    pl.xlabel("Frequency ($\mu$Hz)")
    pl.ylabel("ACF")
    if plot_show in kwargs.keys() and kwargs[plot_show]:
        pl.show(fig)

    if plot_save in kwargs.keys() and kwargs[plot_save]:
        save_fig(fig, f"ACF_fit_delta_nu{get_appendix(kwargs)}")
    pl.close(fig)

def plot_nu_max_fit(data : np.ndarray, popt : List[float],old_nu_max :float,kwargs : Dict):
    fig: Figure = pl.figure(figsize=(10, 6))
    ax: Axes = fig.add_subplot(111)

    if general_kic in kwargs.keys():
        ax.set_title(f"KIC{get_appendix(kwargs)}")

    pl.plot(data[0],data[1],color='k',linewidth=2)
    pl.plot(data[0],gaussian_amp(data[0],*popt),color='red',linewidth=2)
    pl.axvline(x=popt[2],linestyle='dashed',color='blue',linewidth=2,label=fr"Nu max fitted = {'%.2f' % popt[2]}$\mu$Hz")
    pl.axvline(x=old_nu_max, linestyle='dashed', color='green', linewidth=2, label=fr"Nu max Diamonds = {'%.2f' % old_nu_max}$\mu$Hz")
    pl.xlabel("Frequency ($\mu$Hz)")
    pl.ylabel(r'PSD [ppm$^2$/$\mu$Hz]')
    pl.legend()
    if plot_show in kwargs.keys() and kwargs[plot_show]:
        pl.show(fig)

    if plot_save in kwargs.keys() and kwargs[plot_save]:
        save_fig(fig, f"Nu_max_fit_gaussian{get_appendix(kwargs)}")
    pl.close(fig)