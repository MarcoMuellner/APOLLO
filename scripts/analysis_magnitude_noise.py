import argparse
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.image as mpimg
import numpy as np

from scripts.helper_functions import load_results,get_val,recreate_dir
from scripts.helper_functions import f_max,full_background, delta_nu
from res.conf_file_str import general_kic,internal_literature_value,internal_delta_nu,internal_mag_value,internal_teff
from pandas import DataFrame
from scipy.optimize import curve_fit
from uncertainties import ufloat,ufloat_fromstr
pl.rc('font', family='serif')
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')


parser = argparse.ArgumentParser()

parser.add_argument("input_path", help="Result path for a given dataset", type=str)

args = parser.parse_args()

res_list = load_results(args.input_path)

print(f"Usable: {len(res_list)}")

res = {
    "id": [],
    "noise" : [],
    "mag" : [],
    "noise_jenkins": []
}

for path,result,conf in res_list:
    f_lit = ufloat_fromstr(conf[internal_literature_value])
    if f_lit > 288:
        continue

    res["id"].append(conf[general_kic])
    res["mag"].append(conf[internal_mag_value])
    res["noise"].append(get_val(result["Full Background result"], "w").nominal_value)

    c = 3.46 * 10 ** (0.4 * (12. - conf[internal_mag_value]) + 8)
    siglower = np.sqrt(c + 7e6 * max([1, conf[internal_mag_value] / 14.]) ** 4.) / c
    siglower = siglower * 1e6  # [ppm]
    dt = 1. / (2 * 0.000278)  # [sec]
    siglower = siglower ** 2. * 2 * dt * 1.e-6
    print(siglower,get_val(result["Full Background result"], "w").nominal_value)
    res["noise_jenkins"].append(siglower)


pl.plot(res["mag"],res["noise"],'o')
pl.figure()
pl.plot(res["noise"],res["noise_jenkins"],'x')
pl.show()