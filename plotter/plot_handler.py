# standard imports
from typing import Dict, List, Tuple
import os
# scientific imports
import numpy as np
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
# project imports
from res.conf_file_str import general_kic, plot_show, plot_save
from fitter.fit_functions import gaussian
from data_handler.signal_features import compute_periodogram, boxcar_smoothing
from background.backgroundResults import BackgroundResults

pl.rc('font', family='serif')
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')


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

    fig.savefig(f"images/{name}.pdf")


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
        ax.set_title(f"KIC{kwargs[general_kic]}")

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
        save_fig(fig, "Lightcurve_sigma_clipping")

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
        ax.set_title(f"KIC{kwargs[general_kic]}")

    ax.set_ylabel(r'PSD [ppm$^2$/$\mu$Hz]')
    ax.set_xlabel(r'Frequency [$\mu$Hz]')

    if add_smoothing:
        name += "_smoothed"
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

    color = iter(pl.cm.rainbow(np.linspace(0, 1, 10)))
    if f_list is not None:
        for f, f_name in f_list:
            name += f"_f{'%.2f' % f}_n_{len(f_list)}"
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
    f_space = compute_periodogram(data)
    plot_f_space(f_space, kwargs, add_smoothing, f_list,bg_model,plot_name)


def plot_acf_fit(acf: np.ndarray, fit: np.ndarray, tau: float, kwargs: Dict, guess: np.ndarray = None):
    fig: Figure = pl.figure(figsize=(10, 6))
    ax: Axes = fig.add_subplot(111)

    if general_kic in kwargs.keys():
        ax.set_title(f"KIC{kwargs[general_kic]}")

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
        save_fig(fig, f"Fit_{10 ** 6 / tau}")
    pl.close(fig)
