import argparse
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.image as mpimg
import numpy as np

from scripts.helper_functions import load_results,get_val,recreate_dir
from scripts.helper_functions import f_max,full_background
from res.conf_file_str import general_kic,internal_literature_value
from pandas import DataFrame

pl.rc('font', family='serif')
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')

parser = argparse.ArgumentParser()

parser.add_argument("input_path", help="Result path for a given dataset", type=str)
parser.add_argument("output_path",help="Path were analysis results will be saved", type=str)

args = parser.parse_args()

recreate_dir(args.output_path)

res_list = load_results(args.input_path)

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

for path,result,conf in res_list:
    f_lit = conf["Literature value"]

    res["id"].append(conf[general_kic])
    res["f_max"].append(get_val(result[full_background],f_max).nominal_value)
    res["f_max_err"].append(get_val(result[full_background], f_max).std_dev)
    res["f_lit"].append(result[internal_literature_value])
    res["f_guess"].append(result["Nu max guess"])
    res["evidence"].append(result["Conclusion"])
    res["bayes factor"].append(get_val(result,"Bayes factor").nominal_value)
    res["bayes factor error"].append(get_val(result, "Bayes factor").std_dev)
    res["image_path"].append(f"{path}/images")

df = DataFrame(data=res)
df = df.sort_values(by=['f_lit'])

print(df.f_max)

fig : Figure = pl.figure(figsize=(6,8))
fig.subplots_adjust(hspace=0)
ax_guess : Axes = fig.add_subplot(211)
ax_guess.plot(df.f_lit,df.f_guess,'o',markersize=2,color='k')
ax_guess.plot(df.f_lit,df.f_lit,linewidth=2,color='gray',alpha=0.8)
ax_guess.set_xlabel(r"$\nu_{{literature}}$")
ax_guess.set_ylabel(r"$\nu_{{guess}}$")

ax_det : Axes = fig.add_subplot(212,sharex=ax_guess,sharey=ax_guess)
ax_det.plot(df.f_lit,df.f_max,'o',markersize=2,color='k')
ax_det.plot(df.f_lit,df.f_lit,linewidth=2,color='gray',alpha=0.8)
ax_det.set_xlabel(r"$\nu_{{literature}}$")
ax_det.set_ylabel(r"$\nu_{{max}}$")

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

pl.savefig(f"{args.output_path}nu_max_trend.pdf")
pl.show()