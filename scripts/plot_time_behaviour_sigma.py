import argparse
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.image as mpimg
from matplotlib import cm
import matplotlib as  mpl
import numpy as np
from brokenaxes import brokenaxes
from typing import List

from scripts.helper_functions import load_results, get_val, recreate_dir, full_nr_of_runs
from scripts.helper_functions import f_max, full_background, delta_nu
from res.conf_file_str import general_kic, internal_literature_value, internal_delta_nu, analysis_obs_time_value
from pandas import DataFrame
from scipy.optimize import curve_fit
from uncertainties import ufloat, ufloat_fromstr, unumpy as unp
from matplotlib.ticker import FuncFormatter
from matplotlib import rcParams
from itertools import cycle

params = {
   'axes.labelsize': 17,
#   'text.fontsize': 8,
   'legend.fontsize': 10,
   'xtick.labelsize': 18,
   'ytick.labelsize': 18,
   'text.usetex': False,
   'figure.figsize': [4.5, 4.5]
   }
rcParams.update(params)


def append_val_to_dict(map, key, val):
    if key in map.keys() and val is not None:
        map[key].append(val)
    elif delta_nu is not None:
        map[key] = [val]

    return map


def to_percent(y, position):
    # Ignore the passed in position. This has the effect of scaling the default
    # tick locations.
    s = str(int(100 * y))
    if y == 0:
        return ""

    # The percent symbol needs escaping in latex
    if mpl.rcParams['text.usetex'] is True:
        return s + r'$\%$'
    else:
        return s + '%'

cycol = cycle('mcrgb')
def plot_distribution(ax : Axes,vals, x_max, y_max, y_appendix, savefile):
    bins = np.linspace(-x_max, x_max, num=x_max * 5)
    # bins = np.linspace(-x_max, x_max, num=x_max*5)

    for i, (key, value) in enumerate(vals.items()):
        try:
            arr = unp.nominal_values(value)
            arr_err = unp.std_devs(value) / unp.nominal_values(value)
        except:
            arr = np.array(value)
            arr_err = np.zeros(arr)

        try:
            err_mask = np.logical_and(arr > -1, arr < 1)
            err_mask_local = np.logical_and((arr + arr_err / arr) > -1, (arr - arr_err / arr) < 1)
        except Warning:
            pass
        except:
            pass

        total_within_error = len(arr[err_mask]) * 100 / len(arr)
        total_within_error_local = len(arr[err_mask_local]) * 100 / len(arr)
        str_within_error = '%.2f' % total_within_error
        str_within_error_local = '%.2f' % total_within_error_local

        mask = np.logical_and(arr < x_max, arr > -x_max)
        weight = np.ones_like(arr[mask]) / float(len(arr[mask]))
        if i == 0:
            ax.hist(arr[mask], bins, label=f"{key} days, {str_within_error}% ({str_within_error_local}%)$<1\sigma$", color='k', alpha=0.8, align='left',
                    weights=weight)
        else:
            ax.hist(arr[mask], bins, label=f"{key} days, {str_within_error}% ({str_within_error_local}%)$<1\sigma$", histtype='step', align='left',
                    weights=weight,color=next(cycol))

    ax.set_xlabel("Deviation to literature value ($\sigma$)")
    ax.set_ylabel(fr"Percentage of values of {y_appendix}")
    ax.axvline(x=-1, linestyle='dashed', color='red', label='1 $\sigma$ uncertainty')
    ax.axvline(x=1, linestyle='dashed', color='red')
    ax.legend()
    # ax.set_ylim(0,y_max)
    formatter = FuncFormatter(to_percent)
    ax.yaxis.set_major_formatter(formatter)


pl.rc('font', family='serif')
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')

res_path = "../plots/"

try:
    os.makedirs(res_path)
except:
    pass

paths = [
    "../results/apokasc_results_full",
    "../results/apokasc_results_full_356_days",
    "../results/apokasc_results_full_109_days",
    "../results/apokasc_results_full_82_days",
    "../results/apokasc_results_full_54_days",
    "../results/apokasc_results_full_27_days",
]

"""
paths = [
    "../results/results_1_red_giants/apokasc_results_full",
    "../results/results_1_red_giants/apokasc_results_full_356_days",
    "../results/results_1_red_giants/apokasc_results_full_109_days",
    "../results/results_1_red_giants/apokasc_results_full_54_days",
    "../results/results_1_red_giants/apokasc_results_full_27_days",
]

paths = [
    "../results/results_1_red_giants/apokasc_results_full",
    "../results/results_1_red_giants/apokasc_results_full_356_days",
    "../results/results_1_red_giants/apokasc_results_full_109_days",
    "../results/results_1_red_giants/apokasc_results_full_54_days",
    "../results/results_1_red_giants/apokasc_results_full_27_days",
]


paths = [
    "../results/legacy_sample_lund",
    "../results/legacy_sample_lund_356",
    "../results/legacy_sample_lund_109",
    "../results/legacy_sample_lund_54",
    "../results/legacy_sample_lund_27",
]
"""
total = {

}

res_list = []
for i in paths:
    results = load_results(i)
    total_runs = full_nr_of_runs(i)

    if analysis_obs_time_value in results[0][2].keys():
        t = results[0][2][analysis_obs_time_value]
    else:
        t = 1400

    print(f"{t}: {len(results)}")

    res_list = res_list + results
    total[t] = total_runs

nr_of_successes = {}
nr_of_successes_delta_nu = {}

delta_nu_max_to_lit = {}
delta_delta_nu_to_lit = {}

delta_nu_max_to_lit_err = {}
delta_delta_nu_to_lit_err = {}

delta_nu_max_FliPer_to_lit = {}

for path, result, conf in res_list:
    f_lit = ufloat_fromstr(conf[internal_literature_value])
    delta_nu_lit = ufloat_fromstr(conf[internal_delta_nu])

    try:
        delta_nu = get_val(result, 'Delta nu')
        # f_max_f = (delta_nu/0.267)**(1/0.760)
    except:
        continue
        delta_nu = None
    f_max_f = get_val(result[full_background], f_max)

    f_guess = result["Nu max guess"]
    if analysis_obs_time_value in conf.keys():
        t = conf[analysis_obs_time_value]
    else:
        t = 1400
    if get_val(result, "Bayes factor") is None or get_val(result, "Bayes factor").nominal_value < 5:
        print(f"{t} days: Skpping {conf[general_kic]} --> bayes value: {get_val(result, 'Bayes factor')}")
        continue

    append_val_to_dict(nr_of_successes, t, 100 / total[1400])
    append_val_to_dict(delta_nu_max_to_lit, t, (f_max_f - f_lit.nominal_value) / (f_lit.std_dev))
    append_val_to_dict(delta_nu_max_FliPer_to_lit, t, (f_guess - f_lit.nominal_value) / f_lit.std_dev)

    if delta_nu is not None:
        try:
            append_val_to_dict(delta_delta_nu_to_lit, t,
                               (delta_nu - delta_nu_lit.nominal_value) / (delta_nu_lit.std_dev))
            append_val_to_dict(nr_of_successes_delta_nu, t, 100 / total[1400])
        except:
            pass
    else:
        append_val_to_dict(delta_delta_nu_to_lit, t, np.nan)
        append_val_to_dict(nr_of_successes_delta_nu, t, 0)

print("nu_max")
for time, success_rate in nr_of_successes.items():
    print(f"{time}: {'%.2f' % np.sum(success_rate)}%")

print("Delta nu")
for time, success_rate in nr_of_successes_delta_nu.items():
    print(f"{time}: {'%.2f' % np.sum(success_rate)}%")

fig,ax_list = pl.subplots(1,2,figsize=(20,10))
fig : Figure
ax_list : List[Axes]

plot_distribution(ax_list[0],delta_nu_max_to_lit, 5, 0.90, r"$\nu_\mathrm{{max,LCA}}$", "")
plot_distribution(ax_list[1],delta_delta_nu_to_lit, 5, 0.90, r"$\Delta\nu_\mathrm{{LCA}}$", "")
# plot_distribution(delta_nu_max_FliPer_to_lit,15,0.90,"$nu_\mathrm{{max,LCA}}$","")
fig.tight_layout()
fig.savefig(f"{res_path}time_distribution.pdf")
#pl.show()
