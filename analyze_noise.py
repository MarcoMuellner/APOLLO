import argparse
import os
from json import load
import re
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
from matplotlib.ticker import FuncFormatter
import matplotlib

from res.conf_file_str import cat_analysis,analysis_noise_values


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
parser.add_argument("runnerfile", help="Runnerfile", type=str)

args = parser.parse_args()

path = f"{args.path}"
with open(args.runnerfile,'r') as f:
    runner_file = load(f)

noise_values_conf = runner_file[cat_analysis][analysis_noise_values]

res = {}

re_noise_val = re.compile(r"noise_(\d\.*\d*)_\d+")
for path, sub_path, files in os.walk(path):
    in_path_values = re_noise_val.findall(str(sub_path))
    in_path_values = list(map(float,in_path_values))

    if not set(noise_values_conf).issubset(set(in_path_values)):
        continue
    id = re.findall(r"APO_(\d+)",path)[0]

    res[id] = {
        "w":[],
        "h":[],
        "bayes":[]
    }

    for noise_path,_,result_file in os.walk(path):
        if "results.json" in result_file and "conf.json" in result_file:
            with open(f"{noise_path}/results.json",'r') as f:
                result = load(f)

            with open(f"{noise_path}/conf.json",'r') as f:
                conf = load(f)

            h = get_val(result["Full Background result"],"$H_\\mathrm{osc}$")
            w = get_val(result["Full Background result"], "w")
            bayes = get_val(result,"Bayes factor")

            res[id]["w"].append(w)
            res[id]["h"].append(h)
            res[id]["bayes"].append(bayes)

for key,val in res.items():
    if len(val["h"]) < len(noise_values_conf)-2:
        continue
    np_h = np.array(val["h"])
    np_w = np.array(val["w"])
    np_bayes = np.array(val["bayes"])

    snr = np_h / np_w

    fig : Figure = pl.figure()
    pl.plot(snr,np_bayes,'x',color='k')
    pl.title(key)
    pl.xlabel("SNR")
    pl.ylabel("Bayes")
    pl.draw()
    pl.pause(1)
    pl.waitforbuttonpress()
    pl.close(fig)