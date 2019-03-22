import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np
import os

from scripts.helper_functions import load_results, get_val
from scripts.helper_functions import f_max, full_background
from res.conf_file_str import general_kic, internal_literature_value
from uncertainties import ufloat_fromstr
from matplotlib import rcParams
from data_handler.signal_features import background_model

def plot_f_space(ax : Axes, f_data : np.ndarray,bg_model):
    ax.loglog(f_data[0], f_data[1], linewidth=1, color='k')

    ax.set_ylabel(r'PSD [ppm$^2$/$\mu$Hz]')
    ax.set_xlabel(r'Frequency [$\mu$Hz]')

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

input_path = ["../results/apokasc_results_full_27_days/"]
res_path = "../plots/both_models_full_27_days/"

try:
    os.makedirs(res_path)
except:
    pass

res_list = []

for i in input_path:
    res_list += load_results(i)

for path, result, conf in res_list:
    f_lit = ufloat_fromstr(result[internal_literature_value])
    f_max_f = get_val(result[full_background], f_max)
    bayes_factor = get_val(result, "Bayes factor")
    if np.abs(f_max_f - f_lit) >  0.5*f_lit.std_dev or bayes_factor > 5:
        continue
    kic_id = conf[general_kic]

    psd = np.load(f'{path}/psd.npy').T
    fit_res_full = result["Full Background result"]
    fit_res_noise = result["Noise Background result"]

    for key,value in fit_res_full.items():
        fit_res_full[key] = ufloat_fromstr(value).nominal_value

    for key,value in fit_res_noise.items():
        fit_res_noise[key] = ufloat_fromstr(value).nominal_value

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

    fig :Figure = pl.figure(figsize=(11,8))
    ax_full : Axes = fig.add_subplot(2,1,1)
    ax_bg : Axes= fig.add_subplot(2,1,2)

    ax_full.tick_params(
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False)

    fig.subplots_adjust(hspace=0)

    plot_f_space(ax_full,psd,full_model)
    plot_f_space(ax_bg, psd, noise_model)
    fig.savefig(f"{res_path}{kic_id}_{'%.2f' % (bayes_factor.nominal_value)}.pdf")
    pl.close(fig)