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
    internal_teff
from pandas import DataFrame
from scipy.optimize import curve_fit
from uncertainties import ufloat, ufloat_fromstr
from matplotlib import gridspec
from matplotlib.ticker import FuncFormatter
from matplotlib import rcParams
import matplotlib as mpl
from uncertainties import unumpy as unp
from fitter.fit_functions import scipyFit
from itertools import cycle


def fit_fun(x, a, b, c, d):
    return a - b * np.tanh(c * x - d)

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

def gather_results(input_path,use_lowest_reference = False):
    res_list = load_results(input_path)

    mag_results = {}

    for path, result, conf in res_list:
        if conf[internal_mag_value] not in mag_results.keys():
            mag_results[conf[internal_mag_value]] = {
                'kic_id': [],
                'nu_max': [],
                'delta_nu': [],
                'nu_max_lit': [],
                'delta_nu_lit': [],
                'Bayes': [],
            }

        nu_max_lit = ufloat_fromstr(conf[internal_literature_value])
        delta_nu_lit = ufloat_fromstr(conf[internal_delta_nu])

        try:
            nu_max = get_val(result[full_background], f_max)
        except:
            continue
        delta_nu = get_val(result, 'Delta nu')
        if delta_nu is None or isinstance(delta_nu, str):
            delta_nu = ufloat(np.nan, np.nan)
        bayes_factor = get_val(result, "Bayes factor")

        if conf[general_kic] not in mag_results[conf[internal_mag_value]]['kic_id']:
            mag_results[conf[internal_mag_value]]['kic_id'].append(conf[general_kic])
            mag_results[conf[internal_mag_value]]['nu_max'].append([nu_max])
            mag_results[conf[internal_mag_value]]['delta_nu'].append([delta_nu])
            mag_results[conf[internal_mag_value]]['Bayes'].append([bayes_factor])
            if not use_lowest_reference:
                mag_results[conf[internal_mag_value]]['nu_max_lit'].append(nu_max_lit)
                mag_results[conf[internal_mag_value]]['delta_nu_lit'].append(delta_nu_lit)
        else:
            idx = int(np.where(np.array(mag_results[conf[internal_mag_value]]['kic_id']) == conf[general_kic])[0])
            mag_results[conf[internal_mag_value]]['nu_max'][idx].append(nu_max)
            mag_results[conf[internal_mag_value]]['delta_nu'][idx].append(delta_nu)
            mag_results[conf[internal_mag_value]]['Bayes'][idx].append(bayes_factor)

    for mag_val in mag_results.keys():
        keys = ['nu_max', 'delta_nu', 'Bayes']
        for key in keys:
            mag_results[mag_val][key] = [np.mean(i) for i in mag_results[mag_val][key]]

    min_mag_result = mag_results[min(mag_results.keys())]

    if use_lowest_reference:
        for mag_val in mag_results.keys():
            for kic_id in mag_results[mag_val]['kic_id']:
                try:
                    idx = int(np.where(np.array(min_mag_result['kic_id']) == kic_id)[0])
                except:
                    pass
                mag_results[mag_val]['nu_max_lit'].append(min_mag_result['nu_max'][idx])
                mag_results[mag_val]['delta_nu_lit'].append(min_mag_result['delta_nu'][idx])

    return mag_results

def get_bayes_result(input_path,use_lowest_reeference = False):
    mag_list = []
    bayes_list =[]
    mag_results = gather_results(input_path, use_lowest_reeference)
    for mag_val, data in mag_results.items():
        mag_list.append(mag_val)
        bayes_list.append(data['Bayes'])

    bayes_std = [np.std(unp.nominal_values(i))/np.sqrt(len(i)) for i in bayes_list]
    bayes_list = [np.mean(i) for i in bayes_list]
    bayes_list = [ufloat(i.nominal_value,i.std_dev + j) for i,j in zip(bayes_list,bayes_std)]

    return mag_list,bayes_list

def get_magnitude_result(input_path,use_lowest_reference = False):
    mag_list = []
    nr_of_successes = []
    nr_of_successes_err_upper = []
    nr_of_successes_err_lower = []
    nr_of_successes_w_bayes = []
    nr_of_successes_w_bayes_err = []
    nr_of_successes_w_lit_check = []
    nr_of_successes_w_lit_check_err = []

    mag_results = gather_results(input_path,use_lowest_reference)

    for mag_val, data in mag_results.items():

        lit_mask = np.abs(unp.nominal_values(data['nu_max']) - unp.nominal_values(data['nu_max_lit'])) < unp.std_devs(
            data['nu_max_lit'])

        lit_mask_err_upper = np.abs(unp.nominal_values(data['nu_max']) - unp.nominal_values(data['nu_max_lit'])) < unp.std_devs(
            data['nu_max_lit']) + unp.std_devs(data['nu_max'])
        lit_mask_err_lower = np.abs(
            unp.nominal_values(data['nu_max']) - unp.nominal_values(data['nu_max_lit'])) + unp.std_devs(data['nu_max']) < unp.std_devs(
            data['nu_max_lit'])

        bayes_mask = unp.nominal_values(data['Bayes']) > np.log10(5)
        bayes_mask_err = unp.nominal_values(data['Bayes']) + unp.std_devs(data['Bayes']) > np.log10(5)
        mask = np.logical_and(lit_mask, bayes_mask)
        mask_err_upper = np.logical_and(lit_mask_err_upper, bayes_mask_err)
        mask_err_lower = np.logical_and(lit_mask_err_lower, bayes_mask_err)

        mag_list.append(mag_val)

        total = len(mag_results[min(mag_results.keys())]['kic_id'])
        total_local = len(data['nu_max'])
        print(f"{mag_val}: {total_local}/{total}")

        succ_nur = len(np.array(data['nu_max'])[mask])
        succ_nr_w_bayes = len(np.array(data['nu_max'])[lit_mask])
        succ_nr_w_lit = len(np.array(data['nu_max'])[bayes_mask])

        succ_nur_err_upper = np.abs(len(np.array(data['nu_max'])[mask_err_upper]) - succ_nur)/np.sqrt(len(np.array(data['nu_max'])[mask_err_upper]))
        succ_nur_err_lower = np.abs(len(np.array(data['nu_max'])[mask_err_lower]) - succ_nur)/np.sqrt(len(np.array(data['nu_max'])[mask_err_upper]))
        succ_nr_w_bayes_err = len(np.array(data['nu_max'])[lit_mask_err_upper]) - succ_nr_w_bayes
        succ_nr_w_lit_err = len(np.array(data['nu_max'])[bayes_mask_err]) - succ_nr_w_lit

        nr_of_successes.append(succ_nur * 100 / total)
        nr_of_successes_w_bayes.append(succ_nr_w_bayes * 100 / total)
        nr_of_successes_w_lit_check.append(succ_nr_w_lit * 100 / total)

        nr_of_successes_err_upper.append(succ_nur_err_upper * 100 / total)
        nr_of_successes_err_lower.append(succ_nur_err_lower * 100 / total)
        nr_of_successes_w_bayes_err.append(succ_nr_w_bayes_err * 100 / total)
        nr_of_successes_w_lit_check_err.append(succ_nr_w_lit_err * 100 / total)

    nr_of_successes_err = [nr_of_successes_err_lower, nr_of_successes_err_upper]

    return mag_list,nr_of_successes,nr_of_successes_err

input_paths = [
    "../results/mag_356.2",
    "../results/mag_109.6",
    "../results/mag_82.2",
    "../results/mag_54.8",
    "../results/mag_27.4",
#"../results/11.5_mag_boundary/mag_54.8"
#    "../results/11.5_mag_boundary/mag_54.8",

#    "../results/mag_109.6",
#    "../results/11.5_mag_boundary/mag_356.2",
       ]
cycol = cycle('mcrgb')
fig = pl.figure(figsize=(16,10))
ax = pl.subplot(1,1,1)
for input_path in input_paths:
    time = input_path.split("_")[-1]
    c = next(cycol)
    mag_list,nr_of_successes,nr_of_successes_err = get_magnitude_result(input_path,False)
    sort = np.argsort(mag_list)
    lower = np.array(nr_of_successes)[sort] - np.array(nr_of_successes_err[0])[sort]
    upper = np.array(nr_of_successes)[sort] + np.array(nr_of_successes_err[1])[sort]
    pl.fill_between(np.array(mag_list)[sort],lower,upper,label=f"{time} days",alpha=0.2,color=c)
    pl.plot(mag_list,nr_of_successes,'o',color=c)

formatter = FuncFormatter(perc_symbol)
ax.yaxis.set_major_formatter(formatter)
pl.xlabel("Kepler magnitude")
pl.ylabel("Percentage of successful values")
pl.legend()

"""
ax = fig.add_subplot(1,1,1)
pl.errorbar(mag_list, nr_of_successes, nr_of_successes_err, fmt='o',capsize=5,color='k')
pl.xlabel("Kepler magnitude")
pl.ylabel(r"Percentage of values within 1$\sigma$")


pl.tight_layout()
pl.savefig("../plots/magnitude_dependency.pdf")
"""
#pl.errorbar(mag_list, nr_of_successes_w_bayes, nr_of_successes_w_bayes_err, fmt='o')

#pl.errorbar(mag_list, nr_of_successes_w_lit_check, nr_of_successes_w_lit_check_err, fmt='v')
# pl.figure()
# pl.hist(lit_data[1])
pl.tight_layout()
pl.savefig("../plots/magnitude_dependency_percentage.pdf")

cycol = cycle('mcrgb')
fig = pl.figure(figsize=(16,10))
ax = pl.subplot(1,1,1)
for input_path in input_paths:
    time = input_path.split("_")[-1]
    c = next(cycol)
    mag_list,bayes_list= get_bayes_result(input_path,False)
    sort = np.argsort(mag_list)
    lower = np.array(unp.nominal_values(bayes_list) - unp.std_devs(bayes_list))[sort]
    upper = np.array(unp.nominal_values(bayes_list) + unp.std_devs(bayes_list))[sort]
    pl.fill_between(np.array(mag_list)[sort],lower,upper,label=f"{time} days",alpha=0.2,color=c)
    pl.plot(mag_list,unp.nominal_values(bayes_list),'o',color=c)

pl.xlabel("Kepler magnitude")
pl.ylabel(r"$\ln(O_\mathrm{{fbm,nom}})$")
pl.axhline(y=np.log(5),color='k', linestyle='dashed',label='Significance boundary')
pl.legend()
pl.tight_layout()
pl.savefig("../plots/magnitude_dependency_bayes.pdf")
pl.show()
