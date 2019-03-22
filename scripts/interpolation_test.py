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
from fitter.fit_functions import scipyFit
from data_handler.data_refiner import interpolate

input_path = ["../results/mag_356.2"]
res_list = []

for i in input_path:
    res_list += load_results(i)

for path, result, conf in res_list:
    lc= f"{path}/lc.npy"

    data = np.load(lc)

    if "6756908" in path:
        pass
    data_interpolate  =interpolate(data,conf)
    print(path)
