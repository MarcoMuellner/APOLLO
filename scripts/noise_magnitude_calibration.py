import argparse
import os
from json import load
import re
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseEvent
import numpy as np
from uncertainties import ufloat_fromstr, unumpy as unp, ufloat, nominal_value, std_dev
from scipy.optimize import curve_fit
from os import makedirs
from shutil import rmtree
from typing import Union
from res.conf_file_str import internal_literature_value
import json
from scripts.helper_functions import load_results, get_val, recreate_dir, full_nr_of_runs
from scripts.helper_functions import f_max, full_background, delta_nu
from pandas import DataFrame
from res.conf_file_str import general_kic, internal_literature_value, internal_delta_nu, analysis_obs_time_value, \
    internal_mag_value, internal_teff,general_analysis_result_path,analysis_list_of_ids,cat_general,analysis_obs_time_value,cat_analysis
from data_handler.signal_features import background_model
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import kde
from data_handler.signal_features import noise
from json import load,dump
from matplotlib import rcParams
import matplotlib as mpl
from data_handler.signal_features import compute_periodogram

params = {
   'axes.labelsize': 16,
#   'text.fontsize': 8,
   'legend.fontsize': 18,
   'xtick.labelsize': 18,
   'ytick.labelsize': 18,
   'text.usetex': False,
   'figure.figsize': [4.5, 4.5]
   }

rcParams.update(params)

pl.rc('font', family='serif')


mag_list = np.array([
    7,
    7.4,
    8.1,
    8.7,
    9.1,
    9.95,
    10.5,
    11.1,
    11.5,
    12.5,
    12.9,
    13.5,
    14.1,
    14.7,
    15.15,
    15.75
])

w_list = np.array([
    0.28,
    0.4,
    0.7,
    1.01,
    1.92,
    3.3,
    5.9,
    10,
    13,
    43,
    83,
    180,
    330,
    610,
    1500,
    2100


])

def add_subplot_axes(ax,rect,axisbg='w'):
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
    height *= rect[3]  # <= Typo was here
    subax = fig.add_axes([x,y,width,height])
    x_labelsize = subax.get_xticklabels()[0].get_size()
    y_labelsize = subax.get_yticklabels()[0].get_size()
    x_labelsize *= rect[2]**0.5
    y_labelsize *= rect[3]**0.5
    subax.xaxis.set_tick_params(labelsize=x_labelsize)
    subax.yaxis.set_tick_params(labelsize=y_labelsize)
    return subax

def example1():
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(111)
    rect = [0.2,0.2,0.7,0.7]
    ax1 = add_subplot_axes(ax,rect)
    ax2 = add_subplot_axes(ax1,rect)
    ax3 = add_subplot_axes(ax2,rect)
    plt.show()

def get_w(mag_lit):
    idx  = np.argsort(np.abs(mag_list - mag_lit))[0]
    if mag_list[idx] > mag_lit:
        min_mag,max_mag = mag_list[idx-1],mag_list[idx]
        min_w,max_w = w_list[idx-1],w_list[idx]
    else:
        min_mag, max_mag = mag_list[idx], mag_list[idx+1]
        min_w, max_w = w_list[idx], w_list[idx+1]

    b = (np.log10(min_w) - np.log10(max_w))/(min_mag - max_mag)
    a = np.log10(min_w) - b*min_mag

    return 10**(a+b*mag_lit)

def get_mag(w):
    idx  = np.argsort(np.abs(w_list - w))[0]
    if w_list[idx] > w:
        min_mag,max_mag = mag_list[idx-1],mag_list[idx]
        min_w,max_w = w_list[idx-1],w_list[idx]
    else:
        min_mag, max_mag = mag_list[idx], mag_list[idx+1]
        min_w, max_w = w_list[idx], w_list[idx+1]

    b = (np.log10(min_w) - np.log10(max_w))/(min_mag - max_mag)
    a = np.log10(min_w) - b*min_mag

    return (np.log10(w) - a)/b


input_path = ["../results/apokasc_results_full"]
res_list = []

for i in input_path:
    res_list += load_results(i)

mag_lit_list = []
w_lit_list = []
mag_expected_list = []

for path, result, conf in res_list:
    psd = f"{path}/psd.npy"
    f_data = np.load(psd).T
    lc = np.load(f"{path}/lc.npy")
    f_data_new = compute_periodogram(lc,conf)
    fig,ax_list = pl.subplots(1,2,figsize=(16,8),sharex=True,sharey=True)
    ax_list[0].loglog(f_data[0],f_data[1],'o',markersize=2)
    ax_list[0].set_title("original")
    ax_list[1].loglog(f_data_new[0], f_data_new[1],'o',markersize=2)
    ax_list[1].set_title("new")
    pl.draw()
    pl.pause(1)
    pl.waitforbuttonpress()
    pl.close()


    try:
        nu_max = get_val(result[full_background], f_max).nominal_value
    except:
        continue

    nu_max_lit = ufloat_fromstr(conf[internal_literature_value]).nominal_value

    noise_val = noise(f_data)

    mag_expected = get_mag(noise_val)
    mag_lit = conf[internal_mag_value]

    if mag_lit < 6:
        continue

    w_expected = get_w(mag_lit)
    mag_expected_list.append(mag_expected)
    mag_lit_list.append(mag_lit)
    w_lit_list.append(noise_val)

print(f"{len(w_lit_list)}/{len(res_list)}")

w = np.array(w_lit_list)
mag = np.array(mag_lit_list)
mag_exp = np.array(mag_expected_list)
mask_included = np.logical_and(np.abs(mag - mag_exp) < 0.4,np.logical_and(mag > 11.6, mag < 12))
#mask_included = np.logical_and(np.abs(mag - mag_exp) < 0.2,mag < 11.5)
print(f"Total size: {len(w[mask_included])}")

fig : Figure = pl.figure(figsize=(16,10))
axis : Axes = pl.subplot(1,1,1)
subpos = [0.7,0.05,0.3,0.3]
subax1 : Axes = add_subplot_axes(axis,subpos)

axis.plot(w_list,mag_list,marker='o',color='k')
axis.plot(w,mag,'o',markersize=3,alpha=0.3,color='k')
axis.plot(w[mask_included],mag[mask_included],'o',markersize=3,alpha=0.5,color='red')
axis.fill_between(w_list,mag_list + 0.4,mag_list - 0.4,color='grey',alpha=0.2)
axis.hlines(y=11.6,linestyle='dashed',color='grey',alpha=0.8,xmin=min(w),xmax=max(w))
axis.hlines(y=12,linestyle='dashed',color='grey',alpha=0.8,xmin=min(w),xmax=max(w))
axis.set_xscale('log')
axis.set_xlabel("White noise (ppm$^2$/$\mathrm{{\mu}}$Hz)")
axis.set_ylabel("Kepler magnitude")

subax1.plot(w_list,mag_list,marker='o',color='k')
subax1.plot(w,mag,'o',markersize=3,alpha=0.3,color='k')
subax1.plot(w[mask_included],mag[mask_included],'o',markersize=3,alpha=0.5,color='red')
subax1.fill_between(w_list,mag_list + 0.4,mag_list - 0.4,color='grey',alpha=0.2)
subax1.hlines(y=11.6,linestyle='dashed',color='grey',alpha=0.8,xmin=min(w),xmax=max(w))
subax1.hlines(y=12,linestyle='dashed',color='grey',alpha=0.8,xmin=min(w),xmax=max(w))
subax1.set_xscale('log')
subax1.set_xlim(0.9*min(w[mask_included]),1*max(w[mask_included]))
subax1.set_ylim(0.95*min(mag[mask_included]),1.05*max(mag[mask_included]))
subax1.set_xticklabels('')
subax1.set_yticklabels('')
subax1.yaxis.set_ticks_position('none')

pl.tight_layout()
pl.savefig("../plots/magnitude_noise_relation.pdf")
pl.show()