import argparse
from runner.runner import kwarg_list
from data_handler.file_reader import load_file
from data_handler.data_refiner import refine_data
from data_handler.signal_features import nyqFreq_c_d, compute_periodogram, nyqFreq, noise
import matplotlib.pyplot as pl
import numpy as np
from res.conf_file_str import general_kic, internal_literature_value,internal_noise_value
from evaluators.compute_nu_max import filter_lightcurve, compute_nu_max
from evaluators.compute_flicker import calculate_flicker_amplitude, flicker_amplitude_to_frequency
from scipy import signal
from FLIPER.FLIPER import FLIPER, ML
import warnings
from copy import deepcopy
from fitter.fit_functions import quadraticPolynomial, scipyFit
from uncertainties import ufloat
import uncertainties.unumpy as unp


def butter_highpass(cutoff, nyq, order=1):
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return b, a


def butter_highpass_filter(data, cutoff, order=2):
    nyq = nyqFreq(data) * 10 ** -6 * 24 * 3600
    b, a = butter_highpass(cutoff, nyq, order=order)
    y = signal.filtfilt(b, a, data[1])
    return np.array((data[0], y))


parser = argparse.ArgumentParser()
parser.add_argument("runfile", help="The runfile", type=str)

args = parser.parse_args()

fliper_vals = np.loadtxt("fliper.txt", usecols=[0, 1], skiprows=1).T

popt, perr = scipyFit(fliper_vals[0], fliper_vals[1], quadraticPolynomial)
popt = [ufloat(val, err / 2) for val, err in zip(popt, perr)]
fit = quadraticPolynomial(fliper_vals[0], *popt)
# fit = 10**fit

# fliper_vals[0] = 10**fliper_vals[0]

conf_list, nr_of_cores = kwarg_list(args.runfile)

res_list = []

with warnings.catch_warnings():
    warnings.simplefilter("ignore")

    for i in conf_list:
        print(f"ID: {i[general_kic]}")
        try:
            data = load_file(i)
        except:
            continue
        data = refine_data(data, i)

        sigma_ampl = calculate_flicker_amplitude(data)
        f_ampl = flicker_amplitude_to_frequency(sigma_ampl)
        nu_max_it, f_list, f_fliper = compute_nu_max(data, f_ampl, i)

        print(f"ID: {i[general_kic]}")
        print(f"lit: {i[internal_literature_value]}")
        print(f"ACF: {nu_max_it}")
        print(f"List: {f_list}")
        print(f"nu_max Flipper: {f_fliper}")
        if internal_noise_value in i.keys():
            print(f"Noise value: {i[internal_noise_value]}")
        print("\n ")

        #res_list.append((i[general_kic],
        #                 i[internal_literature_value].nominal_value,
        #                 f_fliper,
        #                 nu_max_it))

arr = np.array(res_list)
target_file = args.runfile.split("/")[-1].replace(".json", "") + "_nu_max_methods.txt"
np.savetxt(target_file, arr, fmt="%10d %.2f")
