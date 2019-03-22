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
import json

input_path = ["../results/legacy_sample_lund"]

sample_file = "../sample_lists/apokasc_dwarfs.txt"


data = np.genfromtxt(sample_file,names=True)

res_list = []

for i in input_path:
    res_list += load_results(i,ignore_ignore=True)

for path, result, conf in res_list:
    kic_id = conf[general_kic]

    id_data = np.where(data['id'] == kic_id)

    conf[internal_teff] = data['T_eff'][id_data][0]
    conf[internal_delta_nu] = f"{ufloat(data['delta_nu'][id_data],data['delta_nu_err'][id_data])}"
    conf[internal_literature_value] = f"{ufloat(data['nu_max'][id_data], data['nu_max_err'][id_data])}"
    conf[internal_mag_value] = data['mag'][id_data][0]
    with open(f"{path}/conf.json",'w') as f:
        json.dump(conf,f,indent=4)