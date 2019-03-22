import argparse
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.image as mpimg
import numpy as np
import os

from scripts.helper_functions import load_results, get_val, recreate_dir, full_nr_of_runs
from scripts.helper_functions import f_max, full_background, delta_nu
from res.conf_file_str import general_kic, internal_literature_value, internal_delta_nu, internal_mag_value, \
    internal_teff,analysis_obs_time_value
from pandas import DataFrame
from scipy.optimize import curve_fit
from uncertainties import ufloat, ufloat_fromstr
from matplotlib import gridspec
from matplotlib.ticker import FuncFormatter
from matplotlib import rcParams
import matplotlib as mpl
from data_handler.signal_features import background_model
from typing import List

def plot_f_space(ax : Axes, f_data : np.ndarray,bg_model,t):
    ax.loglog(f_data[0], f_data[1], linewidth=1, color='k',label=f"{t} days")

    if bg_model is not None:
        ax.loglog(f_data[0], bg_model[0], color='b', linewidth=1, linestyle='--')  # harvey 1
        ax.loglog(f_data[0], bg_model[1], color='b', linewidth=1, linestyle='--')  # harvey 2
        ax.loglog(f_data[0], bg_model[2], color='b', linewidth=1, linestyle='--')  # harvey 3
        ax.loglog(f_data[0], bg_model[3], color='y', linewidth=1, linestyle=':')  # noise
        ax.loglog(f_data[0], np.sum(bg_model[0:4], axis=0), color='r', linewidth=1, linestyle='-')  # without Powerexcess
        if len(bg_model) == 5:
            ax.loglog(f_data[0], bg_model[4], color='c', linewidth=1, linestyle=':')  # power
            ax.loglog(f_data[0], np.sum(bg_model, axis=0), color='r', linewidth=1, linestyle='-')  # with Powerexcess

    ax.set_xlim(min(f_data[0]), max(f_data[0]))
    ax.set_ylim(min(f_data[1] * 0.95), max(f_data[1]) * 1.2)
    ax.legend()

params = {
   'axes.labelsize': 16,
#   'text.fontsize': 8,
   'legend.fontsize': 10,
   'xtick.labelsize': 18,
   'ytick.labelsize': 18,
   'text.usetex': False,
   'figure.figsize': [4.5, 4.5]
   }
rcParams.update(params)

input_path = [
    "../results/results_1_red_giants/apokasc_results_full",
    "../results/results_1_red_giants/apokasc_results_full_109_days",
#    "../results/results_1_red_giants/apokasc_results_full_54_days",
    "../results/results_1_red_giants/apokasc_results_full_27_days",
]
res_path = "../plots/"

try:
    os.makedirs(res_path)
except:
    pass

res_list = []

for i in input_path:
    results = load_results(i)

    res_list = res_list + results

fig ,ax_list = pl.subplots(2,3,True,figsize=(16,7))
fig :Figure
ax_list:List[List[Axes]]

n = 0

for path, result, conf in res_list:
    kic_id = conf[general_kic]
    if kic_id != 7266674:
        continue

    psd = np.load(f'{path}/psd.npy').T
    fit_res_full = result["Full Background result"]
    fit_res_noise = result["Noise Background result"]

    for key,value in fit_res_full.items():
        fit_res_full[key] = ufloat_fromstr(value).nominal_value

    for key,value in fit_res_noise.items():
        fit_res_noise[key] = ufloat_fromstr(value).nominal_value


    t = 1400 if analysis_obs_time_value not in conf.keys() else conf[analysis_obs_time_value]
    bayes_factor = get_val(result, "Bayes factor").nominal_value
    print(f"{t}: {'%.2f' % bayes_factor}")

    nyq = 288
    full_model = background_model(psd, nyq, fit_res_full['w'], fit_res_full["$\\sigma_\\mathrm{long}$"], fit_res_full["$b_\\mathrm{long}$"],
                                  fit_res_full["$\\sigma_\\mathrm{gran,1}$"], fit_res_full["$b_\\mathrm{gran,1}$"],
                                  fit_res_full["$\\sigma_\\mathrm{gran,2}$"],
                                  fit_res_full["$b_\\mathrm{gran,2}$"], fit_res_full["$f_\\mathrm{max}$ "],
                                  fit_res_full["$H_\\mathrm{osc}$"],
                                  fit_res_full["$\\sigma_\\mathrm{env}$"])

    noise_model = background_model(psd, nyq, fit_res_noise['w'], fit_res_noise["$\\sigma_\\mathrm{long}$"],
                                  fit_res_noise["$b_\\mathrm{long}$"],
                                  fit_res_noise["$\\sigma_\\mathrm{gran,1}$"], fit_res_noise["$b_\\mathrm{gran,1}$"],
                                  fit_res_noise["$\\sigma_\\mathrm{gran,2}$"],
                                  fit_res_noise["$b_\\mathrm{gran,2}$"])

    plot_f_space(ax_list[0][n],psd,full_model,t)
    plot_f_space(ax_list[1][n], psd, noise_model,t)

    ax_list[0][n].tick_params(axis='both', left=False, top=False, right=False, bottom=False, labelleft=False,
                              labeltop=False,
                              labelright=False, labelbottom=False)
    ax_list[1][n].tick_params(axis='both', left=False, top=False, right=False, bottom=False, labelleft=False,
                              labeltop=False,
                              labelright=False, labelbottom=False)

    n +=1

ax_total = fig.add_subplot(111, frameon=False)

ax_total.tick_params(axis='both', left=False, top=False, right=False, bottom=False, labelleft=False,
                          labeltop=False,
                          labelright=False, labelbottom=False)

pl.ylabel(r'PSD [ppm$^2$/$\mu$Hz]')
pl.xlabel(r'Frequency [$\mu$Hz]')

fig.tight_layout()
fig.subplots_adjust(wspace=0)
fig.subplots_adjust(hspace=0)
#fig.savefig(f"{res_path}bayes_value.pdf")
pl.show()