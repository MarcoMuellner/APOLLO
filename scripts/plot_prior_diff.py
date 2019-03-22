import argparse
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.image as mpimg
import numpy as np

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

pl.rc('font', family='serif')
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')

input_path = ["../results/apokasc_results_full"]
res_path = "../plots/"

try:
    os.makedirs(res_path)
except:
    pass

total = {}
res_list = []
res = {
}

for i in input_path:
    res_list += load_results(i)

for path, result, conf in res_list:
    fit_res = result["Full Background result"]

    for key, value in fit_res.items():
        fit_res[key] = ufloat_fromstr(value).nominal_value

    prior_val = result["Determined params"]

    for key, value in fit_res.items():
        fit_res[key] = value

    key_map = [
        ('w',"w"),
        ('sigma_1',"$\\sigma_\\mathrm{long}$"),
        ('b_1',"$b_\\mathrm{long}$"),
        ('sigma_2',"$\\sigma_\\mathrm{gran,1}$"),
        ('b_2',"$b_\\mathrm{gran,1}$"),
        ('sigma_3',"$\\sigma_\\mathrm{gran,2}$"),
        ('b_3',"$b_\\mathrm{gran,2}$"),
        ('nu_max',"$H_\\mathrm{osc}$"),
        ('H_osc',"$f_\\mathrm{max}$ "),
        ('sigma',"$\\sigma_\\mathrm{env}$"),
    ]

    for prior_key,val_key in key_map:
        if prior_key not in res.keys():
            res[prior_key] = []

        res[prior_key].append((fit_res[val_key] - prior_val[prior_key])*100/fit_res[val_key] )

for key,value in res.items():
    pl.figure()
    print(f"{key}: {'%.2f' % np.median(value)}({'%.2f'  % np.std(value)})")
    arr_val = np.array(value)
    mask = np.logical_and(arr_val > (np.median(arr_val) - 4*np.std(arr_val)),arr_val < (np.median(arr_val) + 4*np.std(arr_val)) )
    #bins = np.linspace(min(value),max(value),num=(max(value) - min(value))*2)
    pl.hist(arr_val[mask])
    pl.title(key)
pl.show()
pl.close()