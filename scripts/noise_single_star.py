import argparse
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.image as mpimg
import numpy as np

from scripts.helper_functions import load_results, get_val, recreate_dir
from scripts.helper_functions import f_max, full_background, delta_nu
from res.conf_file_str import general_kic, internal_literature_value, internal_delta_nu, internal_mag_value, \
    internal_teff, internal_run_number, internal_noise_value
from pandas import DataFrame
from scipy.optimize import curve_fit
from uncertainties import ufloat, ufloat_fromstr, unumpy as unp

pl.rc('font', family='serif')
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')

parser = argparse.ArgumentParser()

parser.add_argument("input_path", help="Result path for a given dataset", type=str)

args = parser.parse_args()
res_list = load_results(args.input_path)
res = {}

for path, result, conf in res_list:

    kic_id = conf[general_kic]
    if kic_id not in res.keys():
        res[kic_id] = {}

    if internal_noise_value in conf.keys():
        noise_val = conf[internal_noise_value]
    else:
        noise_val = 0

    if internal_run_number in conf.keys():
        run_nr = conf[internal_run_number]
    else:
        run_nr = 1

    w = get_val(result["Full Background result"], "w")
    bayes = get_val(result, "Bayes factor")
    h = get_val(result["Full Background result"], "$H_\\mathrm{osc}$")

    if run_nr not in res[kic_id].keys():
        res[kic_id][run_nr] = {"w": [],
                               "h": [],
                               "bayes": [],
                               "noise": []}

    res[kic_id][run_nr]["w"].append(w.nominal_value)
    res[kic_id][run_nr]["h"].append(h.nominal_value)
    res[kic_id][run_nr]["bayes"].append(bayes.nominal_value)
    res[kic_id][run_nr]["noise"].append(noise_val)

for kic_id in res.keys():
    length = [len(res[kic_id][i]["w"]) for i in res[kic_id].keys()]
    min_lenth = min(length)
    print(kic_id)
    w_list = np.vstack(tuple([np.array(res[kic_id][i]["w"])[0:min_lenth] for i in res[kic_id].keys()]))
    h_list = np.vstack(tuple([np.array(res[kic_id][i]["h"])[0:min_lenth] for i in res[kic_id].keys()]))
    bayes_list = np.vstack(tuple([np.array(res[kic_id][i]["bayes"])[0:min_lenth] for i in res[kic_id].keys()]))
    noise_list = np.array(res[kic_id][list(res[kic_id].keys())[0]]["noise"])[0:min_lenth]

    res[kic_id][0] = {"w": unp.uarray(np.average(w_list,axis=0),np.std(w_list,axis=0)),
                      "h": unp.uarray(np.average(h_list,axis=0),np.std(h_list,axis=0)),
                      "bayes": unp.uarray(np.average(bayes_list,axis=0),np.std(bayes_list,axis=0)),
                      "noise": noise_list}
snr_full = []
bayes_full = []
noise_full = []

for kic_id in res.keys():
    if 0 not in res[kic_id].keys():
        continue

    snr = res[kic_id][0]["h"]/res[kic_id][0]["w"]
    mask = unp.nominal_values(res[kic_id][0]["bayes"]) > 0
    pl.figure()
    pl.title(kic_id)
    pl.scatter(unp.nominal_values(snr)[mask],unp.nominal_values(res[kic_id][0]["bayes"])[mask],c=res[kic_id][0]["noise"][mask])
    pl.xlim(max(unp.nominal_values(snr)) * 2, min(unp.nominal_values(snr)) / 2)
    pl.xscale('log')
    pl.colorbar()

pl.show()
