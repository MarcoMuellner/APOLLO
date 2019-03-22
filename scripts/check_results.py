import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np
from uncertainties import ufloat_fromstr

from scripts.helper_functions import load_results, get_val, touch
from scripts.helper_functions import f_max, full_background
from res.conf_file_str import general_kic, internal_literature_value
from data_handler.signal_features import background_model
from typing import List
from data_handler.signal_features import boxcar_smoothing

pl.rc('font', family='serif')
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')

input_path = ["../results/apokasc_results_full"]

res_list = load_results(input_path[0], ["checked.txt"])

def plot_f_space(ax : Axes, f_data : np.ndarray,bg_model):
    ax.loglog(f_data[0], f_data[1], linewidth=1, color='k')

    ax.set_ylabel(r'PSD [ppm$^2$/$\mu$Hz]')
    ax.set_xlabel(r'Frequency [$\mu$Hz]')

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

    ax.set_xlim(min(f_data[0]), max(f_data[0]))
    ax.set_ylim(min(f_data[1] * 0.95), max(f_data[1]) * 1.2)


class b:
    button_pressed = None


def press(event):
    print('press', event.key)
    b.button_pressed = event.key


path_list = []

print(len(res_list))
sigma = 0.5

redo_list = []

fig, ax_list = pl.subplots(1, 2, True, True, figsize=(20, 12))

fig: Figure
ax_list: List[Axes]

n = 0
for path, result, conf in res_list:
    try:
        f_lit = ufloat_fromstr(result[internal_literature_value])

    except:
        f_lit = result["Literature value"]
    f_max_f = get_val(result[full_background], f_max)
    f_guess = result["Nu max guess"]
    if (np.abs(f_max_f - f_lit) - f_max_f.std_dev).nominal_value  > f_lit.std_dev:
        n +=1

print(f"To check: {n}")

for path, result, conf in res_list:
    ax_list[0].cla()
    ax_list[1].cla()
    f_max_f = get_val(result[full_background], f_max)
    f_guess = result["Nu max guess"]
    if get_val(result,"Bayes factor").nominal_value < 5:
        print(f"Skpping {conf[general_kic]} --> bayes value: {get_val(result,'Bayes factor')}")
        continue
    try:
        f_lit = ufloat_fromstr(result[internal_literature_value])

    except:
        f_lit = result["Literature value"]

    if np.abs(f_max_f - f_lit) - f_max_f.std_dev  < f_lit.std_dev:
        continue

    psd = np.load(f'{path}/psd.npy').T
    fit_res_full = result["Full Background result"]
    for key,value in fit_res_full.items():
        fit_res_full[key] = ufloat_fromstr(value).nominal_value
    guess_fit = result["Determined params"]

    nyq = 288

    full_model = background_model(psd, nyq, fit_res_full['w'], fit_res_full["$\\sigma_\\mathrm{long}$"], fit_res_full["$b_\\mathrm{long}$"],
                                  fit_res_full["$\\sigma_\\mathrm{gran,1}$"], fit_res_full["$b_\\mathrm{gran,1}$"],
                                  fit_res_full["$\\sigma_\\mathrm{gran,2}$"],
                                  fit_res_full["$b_\\mathrm{gran,2}$"], fit_res_full["$f_\\mathrm{max}$ "],
                                  fit_res_full["$H_\\mathrm{osc}$"],
                                  fit_res_full["$\\sigma_\\mathrm{env}$"])

    guess_model = background_model(psd, nyq, guess_fit['w'], guess_fit["sigma_1"], guess_fit["b_1"],
                                  guess_fit["sigma_2"], guess_fit["b_2"],
                                  guess_fit["sigma_3"],
                                  guess_fit["b_3"], guess_fit["nu_max"],
                                  guess_fit["H_osc"],
                                  guess_fit["sigma"])

    plot_f_space(ax_list[1],psd,full_model)
    plot_f_space(ax_list[0], psd, guess_model)

    ax_list[0].set_title("Guess")
    ax_list[1].set_title("Full fit")
    ax_list[1].text(0.5, -0.1, rf"$\nu_{{max,guess}}$={f_guess},$\nu_{{max,fit}}$={f_max_f},$\nu_{{max,literature}}$={f_lit}",
                  size=14, ha='center', transform=pl.gca().transAxes)

    fig.canvas.mpl_connect('key_press_event', press)
    fig.subplots_adjust(wspace=0)
    fig.suptitle(f"KIC{conf[general_kic]}")
    pl.draw()
    pl.pause(1)

    while b.button_pressed != "y" and b.button_pressed != "n":
        pl.waitforbuttonpress()
        print()

    if b.button_pressed == "n":
        touch(f"{path}/ignore.txt")
    elif b.button_pressed == "y":
        touch(f"{path}/checked.txt")

    pl.close
    b.button_pressed = None

print(redo_list)

#with open("redo.txt",'w') as f:
#    for kic_id, f_lit in redo_list:
#        f.write(f"{kic_id} {f_lit}\n")
#np.savetxt('redo.txt',np.array(redo_list))