import argparse
import os
from json import load
import re
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseEvent
import numpy as np
from uncertainties import ufloat_fromstr,unumpy as unp,ufloat
from scipy.optimize import curve_fit
from os import makedirs
from shutil import rmtree

pl.rc('font', family='serif')
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')

def fit_fun(x,a,b):
    return a+b*np.log(x)

def get_val(dictionary: dict, key: str, default_value=None):
    if key in dictionary.keys():
        try:
            return ufloat_fromstr(dictionary[key])
        except (ValueError, AttributeError) as e:
            return dictionary[key]
    else:
        return default_value

parser = argparse.ArgumentParser()
parser.add_argument("path", help="The path to be analyzed", type=str)

args = parser.parse_args()

try:
    rmtree(f"noise_results/{args.path}")
except:
    pass

try:
    makedirs(f"noise_results/{args.path}")
except:
    pass

res = {}
re_noise_val = re.compile(r"noise_(\d\.*\d*)_\d+")

for path,sub_path,files in os.walk(args.path):
    try:
        noise = float(re_noise_val.findall(path)[0])
    except IndexError:
        continue

    if noise > 6:
        continue

    if 'results.json' not in files or 'conf.json' not in files:
        continue

    with open(f"{path}/results.json") as f:
        result = load(f)

    with open(f"{path}/conf.json") as f:
        conf = load(f)

    h = get_val(result["Full Background result"], "$H_\\mathrm{osc}$")
    f = get_val(result["Full Background result"], '$f_\\mathrm{max}$ ')
    f_lit = conf["Literature value"]

    if np.abs(f.nominal_value-f_lit)/f_lit > 0.1:
        print(f"Skipping {path} due to difference between lit and result --> {np.abs(f.nominal_value-f_lit)*100/f_lit}")
        print(f"Literature value: {f_lit}")
        print(f"Result value: {f.nominal_value}\n")
        continue


    w = get_val(result["Full Background result"], "w")
    bayes = get_val(result, "Bayes factor")
    run_id = conf['KIC ID']

    if run_id not in res.keys():
        res[run_id] = {}

    if noise not in res[run_id].keys():
        res[run_id][noise] = {"w": [w], "h": [h], "bayes": [bayes]}
    else:
        res[run_id][noise]["w"].append(w)
        res[run_id][noise]["h"].append(h)
        res[run_id][noise]["bayes"].append(bayes)


mean_res = {}

for id_key in res.keys():
    mean_res[id_key] = {
        "w":[],
        "h":[],
        "bayes":[],
        "noise":[]
    }
    for noise_key,val in res[id_key].items():
        mean_res[id_key]["w"].append(np.mean(val["w"]))
        mean_res[id_key]["h"].append(np.mean(val["h"]))
        mean_res[id_key]["bayes"].append(np.mean(val["bayes"]))
        mean_res[id_key]["noise"].append(noise_key)

name_list = []

for key, val in mean_res.items():
    np_h = np.array(val["h"])
    np_w = np.array(val["w"])
    np_bayes = np.array(val["bayes"])
    np_noise = np.array(val["noise"])
    for noise in np_noise:
        name_list += [f"{key}_n_{noise}"]

    snr = np_h / np_w

    try:
        snr_full = np.hstack((snr_full, snr))
        bayes_full = np.hstack((bayes_full, np_bayes))
    except (UnboundLocalError, NameError) as e:
        snr_full = snr
        bayes_full = np_bayes

    np_bayes_err = unp.std_devs(np_bayes)
    np_bayes = unp.nominal_values(np_bayes)

    snr_err = unp.std_devs(snr)
    snr = unp.nominal_values(snr)

    fit_snr = np.linspace(min(snr) * 0.9, max(snr),1000)

    popt, pcov = curve_fit(fit_fun, snr, np_bayes,sigma=np_bayes_err)
    perr = np.sqrt(np.diag(pcov))

    popt_min = popt - 4 * perr
    popt_max = popt + 4 * perr

    #mask = np.logical_and(np_bayes > 0, np_bayes < 50)

    fig: Figure = pl.figure(figsize=(16, 10))
    ax: Axes = fig.add_subplot(1, 2, 1)
    ax.errorbar(np_noise, np_bayes, yerr=np_bayes_err, fmt='x', color='k')

    ax1: Axes = ax.twinx()
    ax1.errorbar(np_noise, snr, yerr=snr_err, fmt='x', color='red')
    ax1.set_ylabel("SNR")
    ax.set_title(key)
    ax.set_xlabel("Noise value")
    ax.set_ylabel("Bayes")

    ax: Axes = fig.add_subplot(1, 2, 2)
    ax.errorbar(snr, np_bayes, xerr=snr_err, yerr=np_bayes_err, fmt='x', color='k')
    ax.axhline(y=5, linestyle='dashed', color='black', label='Strong evidence')
    ax.plot(fit_snr, fit_fun(fit_snr, *popt), color='red', label='Fit', linewidth=2)
    ax.fill_between(fit_snr, fit_fun(fit_snr, *popt_min), fit_fun(fit_snr, *popt_max), color='red', alpha=0.1)
    ax.plot(fit_snr, fit_fun(fit_snr, *popt_min), color='red', linewidth=2, alpha=0.5)
    ax.plot(fit_snr, fit_fun(fit_snr, *popt_max), color='red', linewidth=2, alpha=0.5)
    ax.set_xscale('log')
    ax.legend()
    ax.set_xlabel("SNR")
    ax.set_ylabel("Bayes value")
    ax.set_title(key)
    ax.set_xlim(max(snr) * 1.3, min(snr) * 0.7)
    #pl.draw()
    #pl.pause(1)
    fig.savefig(f"noise_results/{args.path}{key}_noise_behaviour.pdf")
    pl.close(fig)

snr_full_err = unp.std_devs(snr_full)
snr_full = unp.nominal_values(snr_full)
bayes_full_err = unp.std_devs(bayes_full)
bayes_full = unp.nominal_values(bayes_full)

fit_snr = np.linspace(min(snr_full)*0.9,max(snr_full),1000)




np.savetxt(f"noise_results/{args.path}full_data.txt",np.array((snr_full,snr_full_err,bayes_full,bayes_full_err)),)


fig = pl.figure(figsize=(16, 10))
pl.errorbar(snr_full, bayes_full, xerr=snr_full_err, yerr=bayes_full_err, fmt='x', color='k')
pl.plot(fit_snr,fit_fun(fit_snr,*popt),color='red',label='Fit',linewidth=2)
pl.fill_between(fit_snr,fit_fun(fit_snr,*popt_min),fit_fun(fit_snr,*popt_max),color='red',alpha=0.1)
pl.plot(fit_snr,fit_fun(fit_snr,*popt_min),color='red',linewidth=2,alpha=0.5)
pl.plot(fit_snr,fit_fun(fit_snr,*popt_max),color='red',linewidth=2,alpha=0.5)
pl.axhline(y=5, linestyle='dashed', color='black', label='Strong evidence')
#pl.axhline(y=2.5, linestyle='dotted', color='red', label='Moderate evidence')
#pl.yscale('log')
pl.xscale('log')
pl.legend()
pl.xlabel("Signal to noise ratio")
pl.ylabel("Bayes factor")
#pl.xlim(max(snr_full) * 1.1, min(snr_full) *0.9)
pl.xlim(max(snr_full) * 2, min(snr_full) / 2)
# pl.ylim(10**-1,100)
pl.savefig(f"noise_results/{args.path}full_behaviour.pdf")


def onclick(event: MouseEvent):
    if event.dblclick:
        snr = event.xdata
        bayes = event.ydata

        print(f"ID snr: {name_list[np.argmin(np.abs(snr_full - snr))]}")
        print(f"ID bayes: {name_list[np.argmin(np.abs(bayes_full - bayes))]}")


cid = fig.canvas.mpl_connect('button_press_event', onclick)
pl.show()