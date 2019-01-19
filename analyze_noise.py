import argparse
import os
from json import load
import re
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseEvent
from collections import OrderedDict
import numpy as np
from uncertainties import ufloat_fromstr,unumpy as unp
from pdf2image import convert_from_path
from scipy.optimize import curve_fit
from scipy import odr
from fitter.fit_functions import quadraticPolynomial
from matplotlib.ticker import FuncFormatter
import matplotlib

from res.conf_file_str import cat_analysis,analysis_noise_values

def fit_fun(par,x):
    a,b = par
    return a+np.exp(x,b)


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
parser.add_argument("runnerfile", help="Runnerfile", type=str)

args = parser.parse_args()

path = f"{args.path}"
with open(args.runnerfile,'r') as f:
    runner_file = load(f)
    print(runner_file)

noise_values_conf = runner_file[cat_analysis][analysis_noise_values]

res = {}

re_noise_val = re.compile(r"noise_(\d\.*\d*)_\d+")
for path, sub_path, files in os.walk(path):
    in_path_values = re_noise_val.findall(str(sub_path))
    in_path_values = list(map(float,in_path_values))

    if not set(noise_values_conf).issubset(set(in_path_values)):
        continue
    id = re.findall(r"APO_(\d+)",path)[0]

    res[id] = {
        "w":[],
        "h":[],
        "bayes":[],
        "noise":[]
    }

    for noise_path,_,result_file in os.walk(path):
        if "results.json" in result_file and "conf.json" in result_file:
            with open(f"{noise_path}/results.json",'r') as f:
                result = load(f)

            with open(f"{noise_path}/conf.json",'r') as f:
                conf = load(f)

            h = get_val(result["Full Background result"],"$H_\\mathrm{osc}$")
            w = get_val(result["Full Background result"], "w")
            bayes = get_val(result,"Bayes factor")

            noise = re_noise_val.findall(str(noise_path))[0]
            noise = float(noise)

            res[id]["w"].append(w)
            res[id]["h"].append(h)
            res[id]["bayes"].append(bayes)
            res[id]["noise"].append(noise)


for key,val in res.items():
    if len(val["h"]) < len(noise_values_conf)-5:
        continue
    np_h = np.array(val["h"])
    np_w = np.array(val["w"])
    np_bayes = np.array(val["bayes"])
    np_noise = np.array(val["noise"])

    snr = np_h / np_w

    try:
        snr_full = np.hstack((snr_full,snr))
        bayes_full = np.hstack((bayes_full,np_bayes))
    except (UnboundLocalError,NameError) as e:
        snr_full = snr
        bayes_full = np_bayes

    np_bayes_err = unp.std_devs(np_bayes)
    np_bayes = unp.nominal_values(np_bayes)

    snr_err = unp.std_devs(snr)
    snr = unp.nominal_values(snr)

    mask = np.logical_and(np_bayes > 0,np_bayes < 50)

    fig : Figure = pl.figure(figsize=(16,10))
    ax : Axes = fig.add_subplot(1,2,1)
    ax.errorbar(np_noise[mask],np_bayes[mask],yerr=np_bayes_err[mask],fmt='x',color='k')

    ax1 : Axes = ax.twinx()
    ax1.errorbar(np_noise[mask],snr[mask],yerr=snr_err[mask],fmt='x',color='red')
    ax1.set_ylabel("SNR")
    ax.set_title(key)
    ax.set_xlabel("Noise value")
    ax.set_ylabel("Bayes")

    ax: Axes = fig.add_subplot(1, 2, 2)
    ax.errorbar(snr[mask], np_bayes[mask],xerr=snr_err[mask], yerr=np_bayes_err[mask], fmt='x', color='k')
    ax.axhline(y=5,linestyle='dashed',color='red',label='Strong evidence')
    ax.axhline(y=2.5, linestyle='dotted', color='red', label='Moderate evidence')
    ax.legend()
    ax.set_xlabel("SNR")
    ax.set_ylabel("Bayes value")
    ax.set_title(key)
    ax.set_xlim(max(snr)*1.3,min(snr)*0.7)
    #pl.draw()
    #pl.pause(1)
    #pl.waitforbuttonpress()
    fig.savefig(f"noise_results/{key}_noise_behaviour.pdf")
    pl.close(fig)

snr_full_err = unp.std_devs(snr_full)
snr_full = unp.nominal_values(snr_full)
bayes_full_err = unp.std_devs(bayes_full)
bayes_full = unp.nominal_values(bayes_full)

mask = np.abs(snr_full/snr_full_err) > 3
mask = bayes_full > 0

pl.figure(figsize=(16,10))
pl.errorbar(snr_full[mask],bayes_full[mask],xerr=snr_full_err[mask],yerr=bayes_full_err[mask],fmt='x',color='k')
pl.axhline(y=5, linestyle='dashed', color='red', label='Strong evidence')
pl.axhline(y=2.5, linestyle='dotted', color='red', label='Moderate evidence')
pl.legend()
pl.title("Full analysis")
pl.xlabel("SNR")
pl.ylabel("Bayes")
pl.xlim(150,0)
pl.ylim(-10,50)
pl.savefig(f"noise_results/full_behaviour.pdf")
#pl.show()