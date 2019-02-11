import argparse
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.image as mpimg
import numpy as np

from scripts.helper_functions import load_results,get_val,recreate_dir
from scripts.helper_functions import f_max,full_background, delta_nu
from res.conf_file_str import general_kic,internal_literature_value,internal_delta_nu
from pandas import DataFrame
from scipy.optimize import curve_fit
from uncertainties import ufloat,ufloat_fromstr
from collections import OrderedDict

def fit_fun(x,a,b):
    return a+b*x

pl.rc('font', family='serif')
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')


parser = argparse.ArgumentParser()

parser.add_argument("input_path", help="Result path for a given dataset", type=str)
parser.add_argument("output_path",help="Path were analysis results will be saved", type=str)

args = parser.parse_args()

recreate_dir(args.output_path)

res_list = load_results(args.input_path)

print(f"Usable: {len(res_list)}")

res = {
    "id": [],
    "f_delta" : [],
    "f_delta_err" : [],
    "f_lit" : [],
    "f_guess" : [],
    "evidence" : [],
    "bayes factor" : [],
    "bayes factor error" : [],
    "image_path":[]
}

good_list = {
    (30,40) : [],
    (40,50) : [],
    (50,60) : [],
    (60,70) : [],
    (70,80) : [],
}

deviation_list = OrderedDict()

for path,result,conf in res_list:
    try:
        res["f_delta"].append(get_val(result,delta_nu).nominal_value)
    except:
        continue

    if np.abs(get_val(result,delta_nu) - get_val(result,internal_delta_nu)) > get_val(result,internal_delta_nu).std_dev:
        deviation_list[conf[general_kic]] = np.abs(get_val(result,delta_nu) - get_val(result,internal_delta_nu))
        #print(f"{conf[general_kic]}: {np.abs(get_val(result,delta_nu) - get_val(result,internal_delta_nu))}")

    res["id"].append(conf[general_kic])
    res["f_delta_err"].append(get_val(result, delta_nu).std_dev)
    res["f_lit"].append(get_val(result,internal_delta_nu).nominal_value)
    res["f_guess"].append(result["Nu max guess"])
    res["evidence"].append(result["Conclusion"])
    res["bayes factor"].append(get_val(result,"Bayes factor").nominal_value)
    res["bayes factor error"].append(get_val(result, "Bayes factor").std_dev)
    res["image_path"].append(f"{path}/images")

for key,val in sorted(deviation_list.items(),key=lambda x:x[1]):
    print(f"{key}:{val.nominal_value}")

df = DataFrame(data=res)
df = df.sort_values(by=['f_lit'])

#df.f_guess = (df.f_guess + fit_fun(df.f_guess,30.5,0.7))/2

popt,pcov = curve_fit(fit_fun,df.f_lit,df.f_guess)
perr = np.sqrt(np.diag(pcov))

#popt = [30.5,0.7]

fig : Figure = pl.figure(figsize=(6,6))
fig.subplots_adjust(hspace=0)
ax_guess : Axes = fig.add_subplot(111)
ax_guess.plot(df.f_lit,df.f_delta,'o',markersize=2,color='k')
ax_guess.plot(df.f_lit,df.f_lit,linewidth=2,color='gray',alpha=0.8)
ax_guess.set_xlabel(r"$\Delta\nu_{{literature}}$")
ax_guess.set_ylabel(r"$\Delta\nu_{{max,guess}}$")

def onclick(event):
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))

    if event.dblclick:
        if event.inaxes == ax_guess:
            args = np.where(np.abs(df.f_lit - event.xdata) < 0.2)
            img_name = "/PSD_guess_full_fit_{0}_.png"
        else:
            args = np.where(np.abs(df.f_lit - event.xdata) < 0.2)
            img_name = "/PSD_full_fit_{0}_.png"


        for arg in args[0]:
            im_path = df.image_path[arg]
            tmp_img_name = img_name.format(df.id[arg])
            image = mpimg.imread(im_path + tmp_img_name)
            pl.figure()
            pl.imshow(image)
            pl.axis('off')
            pl.text(0.5, -0.1, rf"$\nu_{{max,literature}}$={df.f_lit[arg]},$\nu_{{max,guess}}$={df.f_guess[arg]},$\nu_{{max,fit}}$={df.f_delta[arg]}",
                    size=14, ha='center', transform=pl.gca().transAxes)

        pl.show()


cid = fig.canvas.mpl_connect('button_press_event', onclick)

print(f"{ufloat(popt[0],perr[0])},{ufloat(popt[1],perr[1])}")
pl.savefig(f"{args.output_path}delta_nu_trend.pdf")
pl.show()
