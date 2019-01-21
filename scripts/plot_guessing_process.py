import argparse
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.image as mpimg
from matplotlib.gridspec import GridSpec
import numpy as np
import re

from scripts.helper_functions import load_results,get_val,recreate_dir
from scripts.helper_functions import f_max,full_background
from res.conf_file_str import general_kic,internal_literature_value
from pandas import DataFrame
from scipy.optimize import curve_fit
from uncertainties import ufloat
from fitter.fit_functions import sinc,sin
from evaluators.compute_nu_max import interpolate_acf
import os

def fit_fun(x,a,b):
    return a+b*x

pl.rc('font', family='serif')
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')


parser = argparse.ArgumentParser()

parser.add_argument("input_path", help="Result path for a given dataset", type=str)
parser.add_argument("output_path",help="Path were analysis results will be saved", type=str)

args = parser.parse_args()

recreate_dir(args.output_path)

res_list = load_results(args.input_path)

res = {
    "id": [],
    "f_max" : [],
    "f_max_err" : [],
    "f_lit" : [],
    "f_guess" : [],
    "evidence" : [],
    "bayes factor" : [],
    "bayes factor error" : [],
    "image_path":[]
}

for path,result,conf in res_list:
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    acf_data = {}
    acf_fit_sinc = {}
    acf_fit_sin = {}

    guess = result["Nu max guess"]
    max = get_val(result[full_background],f_max).nominal_value

    print(guess)
    print(max)

    for file in files:
        if file.startswith("ACF_"):
            f = float(re.findall(r"ACF_(\d+\.\d+)",file)[0])
            acf_data[f] = np.loadtxt(f"{path}/{file}")
            acf_data[f] = np.array((acf_data[f][0][::2],acf_data[f][1][::2]))
        elif file.startswith("Fit_parameter_sinc"):
            f = float(re.findall(r"Fit_parameter_sinc_(\d+\.\d+)\.txt",file)[0])
            acf_fit_sinc[f] = np.loadtxt(f"{path}/{file}")
        elif file.startswith("Fit_parameter_sin"):
            f = float(re.findall(r"Fit_parameter_sin_(\d+\.\d+)\.txt",file)[0])
            acf_fit_sin[f] = np.loadtxt(f"{path}/{file}")

    if np.abs(list(acf_data.keys())[1] - max) > 10 or list(acf_data.keys())[0] > list(acf_data.keys())[1]:
        continue

    psd = np.loadtxt(f"{path}/psd.txt").T

    gs = GridSpec(2, 2)#, width_ratios=[2,1])

    linestyle = ['dashed', 'dotted']
    colors = ['red', 'green']

    fig :Figure= pl.figure(figsize=(16,6))
    fig.subplots_adjust(wspace=0,hspace=0)

    ax_list = [fig.add_subplot(gs[0, 0]),fig.add_subplot(gs[0, 1])]

    ax_list[1].tick_params(labelleft=False)
    ax_list[0].set_xlabel("Time")
    ax_list[0].set_ylabel("ACF")

    for ax,col,(f,acf),(f_2,fit),(f_3,fit_sin) in zip(ax_list, colors, acf_data.items(), acf_fit_sinc.items(),acf_fit_sin.items()):
        plot_x = np.linspace(0, np.amax(acf[0]), 4000)
        ax : Axes
        x,y = interpolate_acf(acf[0],acf[1],2)
        ax.plot(x,y,'x',color='k',label=f'f={f}')
        ax.plot(plot_x,(sinc(plot_x,*fit) + sin(plot_x,*fit_sin)),color=col)
        #ax.yaxis.tick_right()
        #ax.yaxis.set_label_position("right")
        ax.legend()
        #ax.set_ylabel("ACF")

    ax : Axes = fig.add_subplot(gs[1,:])
    ax.loglog(psd[0],psd[1], linewidth=1, color='k',alpha=0.5)
    for (f,acf),(f_2,fit),ls,col in zip(acf_data.items(), acf_fit_sinc.items(), linestyle, colors):
        ax.axvline(x=f,label=f"f={f}",linestyle=ls,color=col)
    pl.legend()
    ax.set_ylabel(r'PSD [ppm$^2$/$\mu$Hz]')
    ax.set_xlabel(r'Frequency [$\mu$Hz]')
    fig.suptitle(f"KIC{conf[general_kic]}")

    #pl.draw()
    #pl.pause(1)
    #pl.waitforbuttonpress()

    pl.savefig(f"{args.output_path}/KIC{conf[general_kic]}.pdf")

    pl.close(fig)

