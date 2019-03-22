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
from fitter.fit_functions import scipyFit,gaussian

from matplotlib import rcParams
import matplotlib as mpl


def MAG_COR_KEP(kepmag):
    """
    Function that computes photon noise from kepler magnitude following Jenkins et al., 2012.
    """
    c = 3.46 * 10 ** (0.4 * (12. - kepmag) + 8)
    siglower = np.sqrt(c + 7e6 * max([1, kepmag / 14.]) ** 4.) / c
    siglower = siglower * 1e6  # [ppm]
    dt = 1. / (2 * 0.000278)  # [sec]
    siglower = siglower ** 2. * 2 * dt * 1.e-6
    return siglower

input_path = ["../results/apokasc_results_full"]
res_path = "../plots/"

res_list = []
for i in input_path:
    res_list += load_results(i)

res = {
    "w" : [],
    "w_fliper" :[],
    "w_diff": [],
    "mag" : [],
    "mag_lit" :[],
    "mag_res" :[]
}

for path, result, conf in res_list:
    w = get_val(result["Full Background result"], "w").nominal_value
    mag = (np.log(w) + 3.18) / 0.37
    mag_lit = conf[internal_mag_value]
    mag_res = mag - mag_lit

    res["w"].append(w)
    res["w_fliper"].append(MAG_COR_KEP(mag_lit))
    res["w_diff"].append(w/MAG_COR_KEP(mag_lit))
    res["mag"].append(mag)
    res["mag_lit"].append(mag_lit)
    res["mag_res"].append(mag_res)

df = DataFrame.from_dict(res)

pl.plot(df.w_fliper,df.w,'o')

pl.figure()

bins = np.linspace(0,20,40)
val_hist,bins_hist,_ = pl.hist(df.w_diff,bins=bins,density=True)
x_plot_gauss = np.linspace(min(bins_hist),max(bins_hist),num=1000)
p0 = [0,bins_hist[np.where(val_hist == np.amax(val_hist))],2]
popt,perr = scipyFit(bins_hist[1:],val_hist,gaussian,p0)
pl.plot(x_plot_gauss,gaussian(x_plot_gauss,*popt),color='green',linewidth=2,linestyle='dotted',label='Gaussian fit')
print(popt)
pl.show()