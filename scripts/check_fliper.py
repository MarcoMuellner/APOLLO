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
    internal_teff,internal_path
from pandas import DataFrame
from scipy.optimize import curve_fit
from uncertainties import ufloat, ufloat_fromstr
from matplotlib import gridspec
from matplotlib.ticker import FuncFormatter
from matplotlib import rcParams
import matplotlib as mpl
from uncertainties import unumpy as unp
from fitter.fit_functions import scipyFit

from evaluators.compute_nu_max import compute_fliper_exact

def fit_fun(x,a,b,c,d):
    return a-b*np.tanh(c*x-d)

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
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')

input_path = "../results/apokasc_results_full"

res_list = load_results(input_path,all=True)

mag_results = {}

nu_max_diff = []

for path, result, conf in res_list:

    if "Run number" in conf.keys() and conf["Run number"] != 1:
        continue

    try:
        lc = np.load(f'{path}/lc.npy')
    except:
        continue

    conf[internal_path]  = os.getcwd() + "/.."

    try:
        nu_max = compute_fliper_exact(lc,conf)
    except:
        nu_max = compute_fliper_exact(lc,conf)

    nu_max_diff.append((nu_max - ufloat_fromstr(conf[internal_literature_value]))*100/ufloat_fromstr(conf[internal_literature_value]))
    print((nu_max - ufloat_fromstr(conf[internal_literature_value]))*100/ufloat_fromstr(conf[internal_literature_value]),conf[internal_mag_value])

pl.hist(unp.nominal_values(nu_max_diff))
pl.show()