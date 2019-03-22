import argparse
import matplotlib.pyplot as pl
import numpy as np

from scripts.helper_functions import load_results,get_val
from scripts.helper_functions import f_max,full_background
from res.conf_file_str import internal_literature_value
from uncertainties import ufloat_fromstr
from fitter.fit_functions import gaussian
pl.rc('font', family='serif')
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')

parser = argparse.ArgumentParser()

input_path = "../results/legacy_sample_lund/"
res_list = load_results(input_path)

print(f"Usable: {len(res_list)}")

for path,result,conf in res_list:
    nu_max_prior = result['Determined params']['nu_max']
    f_lit = ufloat_fromstr(conf[internal_literature_value]).nominal_value
    f_max_f = get_val(result[full_background], f_max).nominal_value
    a = 0.6*nu_max_prior
    b = 1.4*nu_max_prior

    x = np.linspace(a*0.0,b*1.3,num=1000)
    y_1 = gaussian(x,0,nu_max_prior,(b-a)/2)
    max_y_1 = np.amax(y_1)
    y_1 = y_1/max_y_1

    fig = pl.figure()
    pl.plot(x,y_1,label='half width')
    pl.title(path)
    pl.axvline(a,linestyle='dashed',label='a',color='red')
    pl.axvline(b, linestyle='dashed',label='b',color='red')
    pl.axvline(f_lit, linestyle='dashed',label='Literature',color='green')
    pl.axvline(f_max_f, linestyle='dashed', label='Determined', color='blue')
    pl.legend()
    print(gaussian(f_lit,0,nu_max_prior,(b-a)/2)/max_y_1)
    pl.draw()
    pl.pause(1)
    pl.waitforbuttonpress()
    pl.close(fig)
