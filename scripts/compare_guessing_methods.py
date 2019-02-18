import argparse
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.image as mpimg
import numpy as np

from scripts.helper_functions import load_results,get_val,recreate_dir
from scripts.helper_functions import f_max,full_background, delta_nu
from res.conf_file_str import general_kic,internal_literature_value
from pandas import DataFrame
from scipy.optimize import curve_fit
from uncertainties import ufloat,ufloat_fromstr

pl.rc('font', family='serif')
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')

def plot_methods(ax : Axes, title : str, ylabel : str, lit_val , val):
    ax.plot(lit_val,val,'o',markersize=2,color='k')
    ax.plot(lit_val,np.zeros(len(lit_val)),color='grey',alpha=0.6,linewidth=2)
    ax.set_xlabel(r"$\nu_{{max,literature}}$")
    ax.set_ylabel(ylabel)
    ax.set_ylim(-80,80)
    ax.set_title(title)



parser = argparse.ArgumentParser()

parser.add_argument("input_path", help="Result path for a given dataset", type=str)

args = parser.parse_args()

res_list = load_results(args.input_path)

res = {
    "id": [],
    "f_lit" : [],
    "f_guess_acf" : [],
    "f_guess_fliper_rough" : [],
    "f_guess_fliper_exact" : [],
    "image_path":[]
}

for path,result,conf in res_list:
    f_lit = ufloat_fromstr(conf[internal_literature_value])
    f_guess_acf = None
    for key, val in result['List of Frequencies'].items():
        if key.startswith("F_filter_1"):
            f_guess_acf = val

    if f_guess_acf is None:
        continue
    f_fliper_guess = float(result["Fliper frequency"]["Fliper rough"])
    f_fliper_exact = float(result["Fliper frequency"]["Fliper exact"])
    res["id"].append(conf[general_kic])
    res["image_path"].append(f"{path}/images")
    res["f_lit"].append(get_val(result,internal_literature_value).nominal_value)
    res["f_guess_acf"].append(f_guess_acf)
    res["f_guess_fliper_rough"].append(f_fliper_guess)
    res["f_guess_fliper_exact"].append(f_fliper_exact)

res["f_lit"] = np.array(res["f_lit"])
res["f_guess_acf"] = np.array(res["f_guess_acf"])
res["f_guess_fliper_rough"] = np.array(res["f_guess_fliper_rough"])
res["f_guess_fliper_exact"] = np.array(res["f_guess_fliper_exact"])

res_acf = np.array((res["f_guess_acf"] - res["f_lit"])*100/res["f_lit"])
res_fliper_rough = np.array((res["f_guess_fliper_rough"]-res["f_lit"])*100/res["f_lit"])
res_fliper_exact = np.array((res["f_guess_fliper_exact"]-res["f_lit"])*100/res["f_lit"])

print(f"Residual ACF: {ufloat(np.mean(res_acf),np.std(res_acf))}%")
print(f"Residual fliper rough: {ufloat(np.mean(res_fliper_rough),np.std(res_fliper_rough))}%")
print(f"Residual fliper exact: {ufloat(np.mean(res_fliper_exact),np.std(res_fliper_exact))}%")


fig : Figure = pl.figure()
ax_acf : Axes  = fig.add_subplot(311)
plot_methods(ax_acf,"ACF method","residual",res["f_lit"],res_acf)
ax_fliper_rough  : Axes= fig.add_subplot(312)
plot_methods(ax_fliper_rough,"Fliper rough method","residual",res["f_lit"],res_fliper_rough)
ax_fliper_exact  : Axes= fig.add_subplot(313)
plot_methods(ax_fliper_exact,"Fliper Exact method","residual",res["f_lit"],res_fliper_exact)
pl.show()
