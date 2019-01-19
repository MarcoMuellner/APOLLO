import argparse
import os
from json import load
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseEvent
from collections import OrderedDict
import numpy as np
from uncertainties import ufloat_fromstr
from pdf2image import convert_from_path
from scipy.optimize import curve_fit
from fitter.fit_functions import quadraticPolynomial


def get_val(dictionary: dict, key: str, default_value=None):
    if key in dictionary.keys():
        try:
            return ufloat_fromstr(dictionary[key]).nominal_value
        except (ValueError, AttributeError) as e:
            return dictionary[key]
    else:
        return default_value


parser = argparse.ArgumentParser()
parser.add_argument("path", help="The path to be analyzed", type=str)

args = parser.parse_args()

path = f"{args.path}"

res_dat = OrderedDict()
res_dat["ID"] = []
res_dat[r"$\nu_{max,guess}$"] = []
res_dat[r"$\nu_{max,literature}$"] = []
res_dat[r"$\nu_{max,fit}$"] = []
res_dat[r"Residual $\nu_{max,guess}$"] = []
res_dat[r"Relative Residual $\nu_{max,guess}$"] = []
res_dat[r"Residual $\nu_{max,fit}$"] = []
res_dat[r"Relative Residual $\nu_{max,fit}$"] = []

res_dat["full_fit"] = []

for path, sub_path, files in os.walk(path):
    if "results.json" in files:
        with open(f"{path}/results.json", 'r') as f:
            data_dict = load(f)

        f_lit = get_val(data_dict, "Literature value")
        f_guess = get_val(data_dict, "Nu max guess")
        f_fit = get_val(data_dict["Full Background result"], "$f_\\mathrm{max}$ ")

        res_dat["ID"].append(int(path.split("_")[-1]))
        res_dat[r"$\nu_{max,guess}$"].append(f_guess)
        res_dat[r"$\nu_{max,literature}$"].append(f_lit)
        res_dat[r"$\nu_{max,fit}$"].append(f_fit)

        res_dat[r"Residual $\nu_{max,guess}$"].append(f_guess - f_lit)
        res_dat[r"Relative Residual $\nu_{max,guess}$"].append((f_guess - f_lit) * 100 / f_lit)

        res_dat[r"Residual $\nu_{max,fit}$"].append(f_fit - f_guess)
        res_dat[r"Relative Residual $\nu_{max,fit}$"].append((f_fit - f_guess) * 100 / f_lit)

        res_dat["full_fit"].append(f"{path}/images/PSD_full_fit.pdf")

fig: Figure = pl.figure(figsize=(17, 6))
#fig.suptitle(r"$\nu_{max}$ analysis")

y = np.array(res_dat[r"$\nu_{max,guess}$"])
x = np.array(res_dat[r"$\nu_{max,literature}$"])[y < 66]
y = y[y < 66]
popt, _ = curve_fit(quadraticPolynomial, x, y)

lower_values = [x,2*y -quadraticPolynomial(y,*popt)]

y = np.array(res_dat[r"$\nu_{max,guess}$"])
x = np.array(res_dat[r"$\nu_{max,literature}$"])[y > 66]
y = y[y > 66]
popt2, _ = curve_fit(quadraticPolynomial, x, y)
upper_values = [x,2*y -quadraticPolynomial(y,*popt2)]



cnt = 1
for j in [r"$\nu_{max,guess}$", r"Residual $\nu_{max,guess}$", r"Relative Residual $\nu_{max,guess}$"]:
    if cnt != 1:
        ax: Axes = fig.add_subplot(1, 3, cnt,sharex=ax)
    else:
        ax: Axes = fig.add_subplot(1, 3, cnt)
    lit_val = np.array(res_dat[r"$\nu_{max,literature}$"])
    ax.plot(lit_val, res_dat[j], 'x', markersize=2, color='k')

    if cnt == 1 or cnt == 4:
        ax.plot(lit_val, res_dat[r"$\nu_{max,literature}$"], markersize=2, color='k',
                linestyle='dashed', alpha=0.7)

    if cnt == 1:
        ax.plot(lit_val, quadraticPolynomial(lit_val, *popt), 'x', markersize=5, color='red', alpha=0.7)
        ax.plot(lit_val, quadraticPolynomial(lit_val, *popt2), 'x', markersize=5, color='blue', alpha=0.7)

    if cnt == 2:
        ax.plot(lit_val, quadraticPolynomial(lit_val, *popt) - lit_val, 'x', markersize=5, color='red', alpha=0.7)
        ax.plot(lit_val, quadraticPolynomial(lit_val, *popt2) - lit_val, 'x', markersize=5, color='blue', alpha=0.7)

    if cnt == 3:
        ax.plot(lit_val, (quadraticPolynomial(lit_val, *popt) - lit_val) * 100 / lit_val, 'x', markersize=5,
                color='red', alpha=0.7)
        ax.plot(lit_val, (quadraticPolynomial(lit_val, *popt2) - lit_val) * 100 / lit_val, 'x', markersize=5,
                color='blue', alpha=0.7)

    if cnt != 4:
        ax.set_ylim(min(res_dat[j])*1.2,max(res_dat[j])*1.2)


    ax.axhline(y=0, color='k')
    ax.set_ylabel(j)
    ax.set_xlabel(r"$\nu_{max,literature}$")
    cnt += 1

pl.show()