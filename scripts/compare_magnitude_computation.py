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
from uncertainties import ufloat, ufloat_fromstr,unumpy as unp
from matplotlib import gridspec
from matplotlib.ticker import FuncFormatter

from matplotlib import rcParams
import matplotlib as mpl
from data_handler.signal_features import noise

input_path = ["../results/apokasc_results_full"]
redo_name = "noise_candidates.txt"
out_path = "../"

try:
    os.makedirs(out_path)
except:
    pass

total = {}
res_list = []
res = {
    "nu_max": [],
    "bayes_factor": [],
    "snr" : [],
    "magnitude" : []
}

for i in input_path:
    res_list += load_results(i)

data_list =[]

upper_snr = 25

res = []

data_list =[]

for path, result, conf in res_list:

    noise_candidates = np.loadtxt(f"../{redo_name}").T

    kic_id = conf[general_kic]

    if kic_id not in noise_candidates[0]:
        continue

    psd = f"{path}/psd.npy"
    psd = np.load(psd).T
    noise_val = noise(psd)

    mag = (np.log(noise_val) + 3.849) / 0.3849 - 4.91
    mag_lit = conf[internal_mag_value]

    if mag_lit > 12:
        continue

    diff = mag - mag_lit

    if np.abs(diff) > 1:
        print(kic_id)
        continue

    idx = np.where(noise_candidates[0] == kic_id)

    data_list.append(noise_candidates.T[idx].tolist()[0])

    res.append(diff)

np.savetxt(f"{out_path}/{redo_name}", np.array(data_list),
               fmt=['%d', '%.2f', '%.2f', '%.2f', '%.2f', '%.3f','%d'])

#print(data_list)
std = np.std(np.array(res))
median = np.median(np.array(res))

print(median,std)

mask = np.logical_and(np.array(res) > median - 4*std, np.array(res) < median  + 4*std)

pl.hist(np.array(res)[mask])
pl.show()
