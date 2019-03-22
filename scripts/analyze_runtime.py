import argparse
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.image as mpimg
import numpy as np

from scripts.helper_functions import load_results,get_val,recreate_dir,full_nr_of_runs
from scripts.helper_functions import f_max,full_background, delta_nu
from res.conf_file_str import general_kic,internal_literature_value,internal_delta_nu,internal_mag_value,internal_teff
from pandas import DataFrame
from scipy.optimize import curve_fit
from uncertainties import ufloat,ufloat_fromstr
from fitter.fit_functions import scipyFit,gaussian
import datetime
pl.rc('font', family='serif')
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')

parser = argparse.ArgumentParser()

parser.add_argument("input_path", help="Result path for a given dataset", type=str)
args = parser.parse_args()
res_list = load_results(args.input_path)
total = full_nr_of_runs(args.input_path)

print(f"Usable: {len(res_list)}")

res = {
    "id": [],
    "Runtime":[]
}

for path,result,conf in res_list:
    f_lit = ufloat_fromstr(conf[internal_literature_value])
    if f_lit > 288:
        continue

    res["id"].append(conf[general_kic])
    res["Runtime"].append(float(result["Runtime"]))

print(f"Runtime single star: {datetime.timedelta(seconds=np.mean(res['Runtime']))}")
print(f"Total: {datetime.timedelta(seconds=np.sum(res['Runtime'])/32)}")
arr = np.array(res['Runtime'])
arr = arr[arr<np.median(arr)+np.std(arr)/2]

binsize = int(max(arr)/50)
bins = np.linspace(0, np.amax(arr), binsize)
hist = np.histogram(arr, bins=bins, density=True)[0]
mids = (bins[1:] + bins[:-1]) / 2
cen = np.average(mids, weights=hist)
wid = np.sqrt(np.average((mids - cen) ** 2, weights=hist))
p0 = [0, cen, wid]
bins = bins[:-1]
popt, __ = scipyFit(bins, hist, gaussian, p0)
(cen, wid) = (popt[1], popt[2])
print(ufloat(cen,wid)/60)

lin = np.linspace(np.min(bins), np.max(bins), len(bins) * 5)

pl.plot(bins, hist, 'x', color='k', markersize=4)
pl.plot(lin, gaussian(lin, *popt))# plot histogram
pl.show()