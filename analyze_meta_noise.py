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
from support.directoryManager import cd

pl.rc('font', family='serif')
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')

def fit_fun(x,a,b):
    return a+b*np.log(x)

res = {}


reg = re.compile(r"n_(\d+)_(\d+)")

for path,sub_path,files in os.walk("noise_results"):
    if "full_data.txt" in files:
        with cd(path):
            data = np.loadtxt("full_data.txt")

        lower_noise = int(reg.findall(path)[0][0])
        upper_noise = int(reg.findall(path)[0][1])

        res[(lower_noise,upper_noise)] = {
            "SNR" : data[0],
            "SNR_err": data[1],
            "Bayes": data[2],
            "Bayes_err": data[3],
        }

fig = pl.figure(figsize=(16, 10))

c_l = ["red","green","blue","black","cyan","yellow"]

c = 0

for key,value in res.items():
    fit_snr = np.linspace(min(value["SNR"]) * 0.9, max(value["SNR"]),1000)

    popt, pcov = curve_fit(fit_fun, value["SNR"], value["Bayes"],sigma=value["Bayes_err"])
    perr = np.sqrt(np.diag(pcov))

    a = ufloat(popt[0], perr[0])
    b = ufloat(popt[1], perr[1])


    snr_strong = 10 ** ((5 - a) / b)
    snr_moderate = 10 ** ((3 - a) / b)
    snr_zero = 10 ** (-a / b)

    print(f"{key[0]} $\mu$Hz - {key[1]} $\mu$Hz")
    print(a, b)
    print(f"Boundary strong evidence: {snr_strong}")
    print(f"Boundary moderate evidence: {snr_moderate}")
    print(f"Boundary zero: {snr_zero}\n")

    popt_min = popt - 4 * perr
    popt_max = popt + 4 * perr

    pl.errorbar(value["SNR"], value["Bayes"],color=c_l[c], xerr=value["SNR_err"], yerr=value["Bayes_err"], fmt='x',label=f"{key[0]} $\mu$Hz - {key[1]} $\mu$Hz")
    pl.plot(fit_snr, fit_fun(fit_snr, *popt), color=c_l[c],linewidth=2,alpha=0.7)
    pl.fill_between(fit_snr, fit_fun(fit_snr, *popt_min), fit_fun(fit_snr, *popt_max), color=c_l[c], alpha=0.1)
    pl.plot(fit_snr, fit_fun(fit_snr, *popt_min), color=c_l[c], linewidth=2, alpha=0.5)
    pl.plot(fit_snr, fit_fun(fit_snr, *popt_max), color=c_l[c], linewidth=2, alpha=0.5)
    pl.xscale('log')
    pl.legend()
    pl.xlabel("Signal to noise ratio")
    pl.ylabel("Bayes factor")
    #pl.xlim(max(value["SNR"]) * 1.1, min(value["SNR"]) *0.9)
    pl.xlim(max(value["SNR"]) * 2, min(value["SNR"]) / 2)
    c +=1


pl.axhline(y=5, linestyle='dashed', color='black', label='Strong evidence')
pl.savefig(f"noise_results/full_behaviour.pdf")
pl.show()
