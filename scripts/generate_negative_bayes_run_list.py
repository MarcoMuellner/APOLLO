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

from scripts.helper_functions import load_results,get_val,recreate_dir,full_nr_of_runs
from scripts.helper_functions import f_max,full_background, delta_nu
from res.conf_file_str import general_kic,internal_literature_value,internal_delta_nu,analysis_obs_time_value,internal_mag_value,internal_teff
from pandas import DataFrame
from scipy.optimize import curve_fit
from uncertainties import ufloat,ufloat_fromstr,unumpy as unp
from matplotlib.ticker import FuncFormatter

paths = [
    "../results/apokasc_results_full",
    "../results/apokasc_results_full_356_days",
    "../results/apokasc_results_full_109_days",
    "../results/apokasc_results_full_54_days",
    "../results/apokasc_results_full_27_days",
]

out_path = "../run_results/"

total = {

}

res_list = []
for i in paths:
    results = load_results(i)
    redo_name = i.split("/")[-1] + "_redo.txt"
    redo_list = []
    for path, result, conf in results:
        f_lit = ufloat_fromstr(conf[internal_literature_value])
        f_delta_nu = ufloat_fromstr(conf[internal_delta_nu])
        if get_val(result, "Bayes factor") is None or get_val(result, "Bayes factor").nominal_value < 5:
            print(f"Skpping {conf[general_kic]} --> bayes value: {get_val(result, 'Bayes factor')}")
            redo_list.append((conf[general_kic], f_lit.nominal_value, f_lit.std_dev,
                              f_delta_nu.nominal_value, f_delta_nu.std_dev, conf[internal_mag_value],
                              conf[internal_teff]))
    np.savetxt(f"{out_path}/{redo_name}", np.array(redo_list),
               fmt=['%d', '%d', '%.2f', '%.2f', '%.2f', '%.2f', '%.3f'])
