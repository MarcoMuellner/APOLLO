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
import pandas
from fitter.fit_functions import scipyFit,quadraticPolynomial

def fit_fun(x,a,b):
    return a+b*x

input_path = ["../results/apokasc_results_full"]
res_path = "../plots/"

try:
    os.makedirs(res_path)
except:
    pass

total = {}
res_list = []
res = {
    "id": [],
    "magnitude":[],
    "w":[],
}

data_list = []
redo_name = "noise_candidates.txt"
out_path = "../run_results"

for i in input_path:
    res_list += load_results(i)

for path, result, conf in res_list:
    nu_max_lit = ufloat_fromstr(conf[internal_literature_value])
    w = get_val(result["Full Background result"], "w").nominal_value
    h = get_val(result["Full Background result"], "$H_\\mathrm{osc}$")
    bayes = get_val(result, "Bayes factor")
    f_guess = result["Nu max guess"]
    delta_nu = get_val(result, 'Delta nu')

    nu_max = get_val(result[full_background], f_max)
    psd = np.load(f'{path}/psd.npy').T

    sigma = get_val(result[full_background], "$\sigma_\mathrm{env}$")
    lower_mask = np.logical_and(psd[0] < nu_max - sigma, psd[0] > nu_max - 2 * sigma)
    upper_mask = np.logical_and(psd[0] > nu_max + sigma, psd[0] < nu_max + 2 * sigma)
    osc_region = np.logical_and(psd[0] > nu_max - sigma, psd[0] < nu_max + sigma)

    #    max_amp = psd[1][np.where(psd[0] == nu_max)]
    max_amp = np.amax(psd[1][osc_region])
    noise_fit_val = np.mean(np.hstack((psd[1][lower_mask], psd[1][upper_mask])))


    mag = (np.log(noise_val) + 3.849) / 0.3849 - 4.91
    mag_lit = conf[internal_mag_value]

    if mag_lit > 12:
        continue

    diff = mag - mag_lit

    if np.abs(diff) > 1:
        print(kic_id)
        continue


    if max_amp/noise_fit_val < 10:# and f_guess > nu_max_lit:
        data_list.append((conf[general_kic], nu_max_lit.nominal_value, nu_max_lit.std_dev,
                          delta_nu.nominal_value, delta_nu.std_dev, conf[internal_mag_value],
                          conf[internal_teff]))
        print(conf[general_kic],h/w,bayes,(f_guess - nu_max_lit)/nu_max_lit.std_dev,nu_max_lit)
    res["id"].append(conf[general_kic])
    res["magnitude"].append(conf[internal_mag_value])
    res["w"].append(w)

np.savetxt(f"{out_path}/{redo_name}", np.array(data_list),
               fmt=['%d', '%d', '%.2f', '%.2f', '%.2f', '%.2f', '%.3f'])

df = pandas.DataFrame.from_dict(res)

df = df.sort_values(by=['w'])
popt,perr = scipyFit(df.w,df.magnitude,fit_fun)
print(popt)
pl.plot(df.w,df.magnitude,'o')
pl.plot(df.w,fit_fun(df.w,*popt))
#pl.yscale('log')
#pl.show()

res = {
    "w":[],
    "magnitude":[],
    "magnitude_res":[]
}

for w,mag in zip(df.w,df.magnitude):
    kp_new = fit_fun(w,*popt)
    res["magnitude_res"].append(kp_new-mag)
    res["magnitude"].append(mag)
    res["w"].append(w)

df = pandas.DataFrame.from_dict(res)

pl.figure()
pl.plot(df.magnitude,df.magnitude_res,'o')
pl.show()