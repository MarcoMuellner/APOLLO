#standard imports
from typing import Dict,List
import os
#scientific imports
import numpy as np
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
#project imports
from res.conf_file_str import general_kic,plot_show,plot_save
from fitter.fit_functions import gaussian

pl.rc('font', family='serif')
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')

def add_subplot_axes(ax : Axes,rect : List[float]) -> Axes:
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
    inax_position  = ax.transAxes.transform(rect[0:2])
    transFigure = fig.transFigure.inverted()
    infig_position = transFigure.transform(inax_position)

    x = infig_position[0]
    y = infig_position[1]
    width *= rect[2]
    height *= rect[3]

    subax = fig.add_axes([x,y,width,height])
    subax.set_facecolor('white')

    x_labelsize = subax.get_xticklabels()[0].get_size()
    y_labelsize = subax.get_yticklabels()[0].get_size()

    x_labelsize *= rect[2]**0.5
    y_labelsize *= rect[3]**0.5

    subax.xaxis.set_tick_params(labelsize=x_labelsize)
    subax.yaxis.set_tick_params(labelsize=y_labelsize)
    return subax

def save_fig(fig : Figure, name : str):
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

def plot_sigma_clipping(data: np.ndarray,bins : np.ndarray, hist: np.ndarray, popt : List[float], kwargs : Dict):
    """
    Plots the sigma clipping
    :param data: Dataset of lightcurve
    :param bins: bins from histogram
    :param hist: histogram values
    :param popt: fit from gaussian
    :param kwargs: Run configuration
    """
    fig : Figure = pl.figure(figsize=(10,6))
    ax : Axes = fig.add_subplot(111)

    if general_kic in kwargs.keys():
        ax.set_title(f"KIC{kwargs[general_kic]}")

    rect = [0.7,0.08,0.3,0.3]
    ax1 : Axes = add_subplot_axes(ax,rect)

    ax.plot(data[0],data[1],'o',color='k',markersize=2) #plot data
    ax.set_facecolor('white')

    ax1.plot(bins, hist, 'x', color='k', markersize = 4) #plot histogram

    lin = np.linspace(np.min(bins), np.max(bins), len(bins) * 5)
    ax1.plot(lin,gaussian(lin, *popt))

    (cen, wid) = (popt[1], popt[2])
    sigma = 5 #used by the fit!
    ax1.axvline(cen - sigma * wid, ls='dashed', color='k')
    ax1.axvline(cen + sigma * wid, ls='dashed', color='k')

    ax.set_xlabel("Time (days)")
    ax.set_ylabel("Flux")
    ax1.set_xlabel('Delta F')
    ax1.set_ylabel(r'N')

    ax1.set_xlim((cen - sigma * wid * 1.2), (cen + sigma * wid * 1.2))

    if plot_show in kwargs.keys() and plot_show:
        pl.show(fig)

    if plot_save in kwargs.keys() and plot_save:
        save_fig(fig,"Lightcurve_sigma_clipping")

    pl.close(fig)
