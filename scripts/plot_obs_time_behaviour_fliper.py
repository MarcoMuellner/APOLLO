import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib as  mpl
import numpy as np
import os

from scripts.helper_functions import load_results,get_val,full_nr_of_runs
from scripts.helper_functions import delta_nu
from res.conf_file_str import general_kic,internal_literature_value,internal_delta_nu,analysis_obs_time_value
from uncertainties import ufloat,ufloat_fromstr,unumpy as unp
from matplotlib.ticker import FuncFormatter
from fitter.fit_functions import scipyFit,gaussian
from matplotlib import rcParams

params = {
   'axes.labelsize': 20,
#   'text.fontsize': 8,
   'legend.fontsize': 18,
   'xtick.labelsize': 18,
   'ytick.labelsize': 18,
   'text.usetex': False,
   'figure.figsize': [4.5, 4.5]
   }
rcParams.update(params)

def append_val_to_dict(map,key,val):
    if key in map.keys() and val is not None:
        map[key].append(val)
    elif delta_nu is not None:
        map[key] = [val]

    return map

def perc_symbol(y, position):
    # Ignore the passed in position. This has the effect of scaling the default
    # tick locations.
    s = str(int(y))
    if y == 0 :
        return ""

    # The percent symbol needs escaping in latex
    if mpl.rcParams['text.usetex'] is True:
        return s + r'$\%$'
    else:
        return s + '%'


def to_percent(y, position):
    # Ignore the passed in position. This has the effect of scaling the default
    # tick locations.
    s = str(int(100 * y))
    if y == 0 :
        return ""

    # The percent symbol needs escaping in latex
    if mpl.rcParams['text.usetex'] is True:
        return s + r'$\%$'
    else:
        return s + '%'

def plot_distribution(vals,err,x_max,y_max,savefile):
    fig: Figure = pl.figure(figsize=(16, 10))
    fig.subplots_adjust(hspace=0)
    ax : Axes = fig.add_subplot(111)
    bins = np.linspace(-x_max, x_max, num=50)

    mean_err = None

    for i, ((key, value),(key_err, value_err)) in enumerate(zip(vals.items(),err.items())):
        try:
            arr  = unp.nominal_values(value)
            arr_err = unp.std_devs(value)
        except:
            arr = np.array(value)
            arr_err = np.array(value)

        lit_err =np.array(value_err)
        try:
            err_mask = np.logical_and(arr> -lit_err, arr< lit_err)
        except Warning:
            pass
        except:
            pass

        total_within_error = len(arr[err_mask])*100/len(arr)
        str_within_error = '%.2f' % total_within_error

        mask = np.logical_and(arr < x_max, arr > -x_max)
        if i == 0:
            val_hist,bins_hist,_ = ax.hist(arr[mask], bins, density=True, label=fr"$\nu_\mathrm{{max}}$ values FliPer",color='k',alpha=0.8,align='mid')
        else:
            val_hist,bins_hist,_ = ax.hist(arr[mask], bins, density=True, label=fr"$\nu_\mathrm{{max}}$ values FliPer",histtype='step',align='mid')

        p0 = [0,bins_hist[np.where(val_hist == np.amax(val_hist))],np.std(arr[mask])]
        popt,perr = scipyFit(bins_hist[1:],val_hist,gaussian,p0)

        x_plot_gauss = np.linspace(-x_max,x_max,num=1000)

        ax.plot(x_plot_gauss,gaussian(x_plot_gauss,*popt),color='green',linewidth=2,linestyle='dotted',label='Gaussian fit')
        print(f"Values centered: {'%.2f' % popt[1]}%, width: {'%.2f' % (popt[2])}%")

        if mean_err is None:
            mean_err = np.mean(arr_err+lit_err)

    ax.set_xlabel("Deviation to literature value")
    ax.set_ylabel("Percentage of values")
    ax.legend()
#    ax.set_ylim(0,y_max)
    formatter_y = FuncFormatter(to_percent)
    formatter_x = FuncFormatter(perc_symbol)
    ax.yaxis.set_major_formatter(formatter_y)
    ax.xaxis.set_major_formatter(formatter_x)
    fig.tight_layout()
    fig.savefig(savefile)


pl.rc('font', family='serif')

paths = [
    "../results/apokasc_results_full",
]

res_path = "../plots/"

try:
    os.makedirs(res_path)
except:
    pass

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

    res_list = res_list + results
    total[t] = total_runs

nr_of_successes = {}

delta_nu_max_to_lit = {}
delta_delta_nu_to_lit = {}

delta_nu_max_to_lit_err = {}
delta_delta_nu_to_lit_err = {}

delta_nu_max_FliPer_to_lit = {}

for path,result,conf in res_list:
    f_lit = ufloat_fromstr(conf[internal_literature_value])
    delta_nu_lit = ufloat_fromstr(conf[internal_delta_nu])
    """
    try:
        f_max_f = get_val(result,'nu_max_gauss')
        if f_max_f == None:
            f_max_f = get_val(result[full_background], f_max)
            f_max_f.std_dev = f_max_f.std_dev*4

        if np.isnan(f_max_f.std_dev):
            f_max_f = ufloat(f_max_f.nominal_value,0)
    except:
        f_max_f = get_val(result[full_background], f_max)
    """

    try:
        delta_nu = get_val(result, 'Delta nu')
        f_max_f = (delta_nu/0.267)**(1/0.760)
    except:
        continue
        delta_nu = None
    #f_max_f = get_val(result[full_background], f_max)

    f_guess = result["Nu max guess"]
    if analysis_obs_time_value in conf.keys():
        t = conf[analysis_obs_time_value]
    else:
        t = 1400
    if get_val(result,"Bayes factor") is None or get_val(result,"Bayes factor").nominal_value < 5:
        print(f"{t} days: Skpping {conf[general_kic]} --> bayes value: {get_val(result,'Bayes factor')}")
        continue

    append_val_to_dict(nr_of_successes,t,100/total[1400])
    append_val_to_dict(delta_nu_max_to_lit,t,(f_max_f - f_lit.nominal_value) * 100 / f_lit.nominal_value)
    append_val_to_dict(delta_nu_max_to_lit_err,t,f_lit.std_dev*100/f_lit.nominal_value)
    append_val_to_dict(delta_nu_max_FliPer_to_lit, t, (f_guess - f_lit.nominal_value) *100 / f_lit.nominal_value)

    if delta_nu is not None:
        try:
            append_val_to_dict(delta_delta_nu_to_lit,t,(delta_nu - delta_nu_lit.nominal_value) * 100 / delta_nu_lit.nominal_value)
            append_val_to_dict(delta_delta_nu_to_lit_err, t, delta_nu_lit.std_dev * 100 / delta_nu_lit.nominal_value)
        except:
            pass




for time,success_rate in nr_of_successes.items():
    print(f"{time}: {'%.2f' % np.sum(success_rate)}%")

plot_distribution(delta_nu_max_FliPer_to_lit,delta_nu_max_to_lit_err,30,0.20,f"{res_path}plot_FliPer_distribution.pdf")