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

redo_name = args.input_path.split("/")[-1]+"_redo.txt"

print(f"Usable: {len(res_list)}")

res = {
    "id": [],
    "f_max" : [],
    "f_max_err" : [],
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
    (80,90) : [],
    (90,100) : [],
    (100,110) : [],
    (110,120) : [],
    (120,130) : [],
    (130,140) : [],
    (140,150) : [],
    (150,160) : [],
    (160,170) : [],
    (170,180) : [],
    (180,190) : [],



}

full_list_noise = []
total = full_nr_of_runs(args.input_path)
redo_list = []

for path,result,conf in res_list:
    f_lit = ufloat_fromstr(conf[internal_literature_value])
    #if f_lit > 288:
    #    continue
    f_delta_nu = ufloat_fromstr(conf[internal_delta_nu])
    f_max_f = get_val(result[full_background],f_max).nominal_value
    f_guess = result["Nu max guess"]

    if get_val(result,"Bayes factor").nominal_value < 5:
        print(f"Skpping {conf[general_kic]} --> bayes value: {get_val(result,'Bayes factor')}")
        redo_list.append((conf[general_kic], f_lit.nominal_value, f_lit.std_dev,
                                              f_delta_nu.nominal_value, f_delta_nu.std_dev, conf[internal_mag_value],
                                              conf[internal_teff]))
        continue
    if 40 < (f_guess - f_lit)*100/f_lit:
        print((f_guess - f_lit)*100/f_lit)
        for (minimum,maximum) in good_list.keys():
            full_list_noise.append((conf[general_kic],f_lit.nominal_value,f_lit.std_dev,f_delta_nu.nominal_value,f_delta_nu.std_dev,conf[internal_mag_value],conf[internal_teff]))
            if minimum < f_max_f < maximum:
                good_list[(minimum,maximum)].append((conf[general_kic],f_lit.nominal_value,f_lit.std_dev,f_delta_nu.nominal_value,f_delta_nu.std_dev,conf[internal_mag_value],conf[internal_teff]))
                break
        print(f"Minima ID: {conf[general_kic]},max : {f_max_f}")

    res["id"].append(conf[general_kic])
    res["f_max"].append(get_val(result[full_background],f_max).nominal_value)
    res["f_max_err"].append(get_val(result[full_background], f_max).std_dev)
    res["f_lit"].append(get_val(result,internal_literature_value).nominal_value)
    res["f_guess"].append(result["Nu max guess"])
    res["evidence"].append(result["Conclusion"])
    res["bayes factor"].append(get_val(result,"Bayes factor").nominal_value)
    res["bayes factor error"].append(get_val(result, "Bayes factor").std_dev)
    res["image_path"].append(f"{path}/images")

np.savetxt(f"{args.output_path}/{redo_name}.txt",np.array(redo_list),fmt=['%d','%d','%.2f','%.2f','%.2f','%.2f','%.3f'])

df = DataFrame(data=res)
df = df.sort_values(by=['f_lit'])

#df.f_guess = (df.f_guess + fit_fun(df.f_guess,30.5,0.7))/2

popt,pcov = curve_fit(fit_fun,df.f_lit,df.f_guess)
perr = np.sqrt(np.diag(pcov))

#popt = [30.5,0.7]

fig : Figure = pl.figure(figsize=(6,8))
fig.subplots_adjust(hspace=0)
ax_guess : Axes = fig.add_subplot(411)
ax_guess.plot(df.f_lit,df.f_guess,'o',markersize=2,color='k')
ax_guess.plot(df.f_lit,df.f_lit,linewidth=2,color='gray',alpha=0.8)
#ax_guess.plot(df.f_lit,fit_fun(df.f_lit,*popt),linewidth=2,color='red',alpha=0.6)
ax_guess.set_xlabel(r"$\nu_{{max,literature}}$")
ax_guess.set_ylabel(r"$\nu_{{max,guess}}$")

ax_redo : Axes = fig.add_subplot(412)
ax_redo.plot(df.f_lit,df.f_max,'o',markersize=2,color='k')
ax_redo.plot(df.f_lit,df.f_lit,linewidth=2,color='gray',alpha=0.8)
ax_redo.set_xlabel(r"$\nu_{{max,literature}}$")
ax_redo.set_ylabel(r"$\nu_{{max,guess}}$")

ax_redo : Axes = fig.add_subplot(413)
ax_redo.plot(df.f_lit,(df.f_guess - df.f_lit)*100/df.f_lit,'o',markersize=2,color='k')
ax_redo.plot(df.f_lit,np.zeros(len(df.f_lit)),linewidth=2,color='gray',alpha=0.8)
ax_redo.set_ylim(0,80)
ax_redo.set_xlabel(r"$\nu_{{max,literature}}$")
ax_redo.set_ylabel(r"Residual guess")

ax_redo : Axes = fig.add_subplot(414)
ax_redo.plot(df.f_lit,(df.f_max - df.f_lit)*100/df.f_lit,'o',markersize=2,color='k')
ax_redo.plot(df.f_lit,np.zeros(len(df.f_lit)),linewidth=2,color='gray',alpha=0.8)
ax_redo.set_xlabel(r"$\nu_{{max,literature}}$")
ax_redo.set_ylabel(r"Residual")

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
            pl.text(0.5, -0.1, rf"$\nu_{{max,literature}}$={df.f_lit[arg]},$\nu_{{max,guess}}$={df.f_guess[arg]},$\nu_{{max,fit}}$={df.f_max[arg]}",
                    size=14, ha='center', transform=pl.gca().transAxes)

        pl.show()


cid = fig.canvas.mpl_connect('button_press_event', onclick)

print(f"{ufloat(popt[0],perr[0])},{ufloat(popt[1],perr[1])}")
#print(f"{used}/{total} --> {used*100/total}%")
pl.savefig(f"{args.output_path}nu_max_trend.pdf")
pl.show()
