import argparse
import os
from json import load
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseEvent
import matplotlib.image as mpimg
from collections import OrderedDict
import numpy as np
from uncertainties import ufloat_fromstr
from pdf2image import convert_from_path
from scipy.optimize import curve_fit
from fitter.fit_functions import quadraticPolynomial
from matplotlib.ticker import FuncFormatter
import matplotlib


def get_val(dictionary: dict, key: str, default_value=None):
    if key in dictionary.keys():
        try:
            return ufloat_fromstr(dictionary[key]).nominal_value
        except (ValueError, AttributeError) as e:
            return dictionary[key]
    else:
        return default_value

def to_percent(y, position):
    # Ignore the passed in position. This has the effect of scaling the default
    # tick locations.
    s = str(int(100 * y))

    # The percent symbol needs escaping in latex
    if matplotlib.rcParams['text.usetex'] is True:
        return s + r'$\%$'
    else:
        return s + '%'


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
res_dat[r"Amount sigma"] = []

res_dat["full_fit"] = []

for path, sub_path, files in os.walk(path):
    if "results.json" in files:
        with open(f"{path}/results.json", 'r') as f:
            data_dict = load(f)

        f_lit = get_val(data_dict, "Literature value")
        f_guess = get_val(data_dict, "Nu max guess")
        f_fit = get_val(data_dict["Full Background result"], "$f_\\mathrm{max}$ ")
        sigma = ufloat_fromstr(data_dict["Full Background result"]["$f_\\mathrm{max}$ "]).std_dev

        for i in range(1,11):
            if abs(f_fit - f_guess) < i*sigma:
                res_dat[r"Amount sigma"].append(i)
                break

        res_dat["ID"].append(int(path.split("_")[-1]))
        res_dat[r"$\nu_{max,guess}$"].append(f_guess)
        res_dat[r"$\nu_{max,literature}$"].append(f_lit)
        res_dat[r"$\nu_{max,fit}$"].append(f_fit)

        res_dat[r"Residual $\nu_{max,guess}$"].append(f_guess - f_lit)
        res_dat[r"Relative Residual $\nu_{max,guess}$"].append((f_guess - f_lit) * 100 / f_lit)

        res_dat[r"Residual $\nu_{max,fit}$"].append(f_fit - f_guess)
        res_dat[r"Relative Residual $\nu_{max,fit}$"].append((f_fit - f_guess) * 100 / f_lit)

        res_dat["full_fit"].append(f"{path}/images/PSD_full_fit_{int(path.split('_')[-1])}_.png")

fig: Figure = pl.figure(figsize=(20, 10))
fig.suptitle(r"$\nu_{max}$ analysis")

y = np.array(res_dat[r"$\nu_{max,guess}$"])
x = np.array(res_dat[r"$\nu_{max,literature}$"])[y < 66]
y = y[y < 66]
#popt, _ = curve_fit(quadraticPolynomial, x, y)

#lower_values = [x,2*y -quadraticPolynomial(y,*popt)]

y = np.array(res_dat[r"$\nu_{max,guess}$"])
x = np.array(res_dat[r"$\nu_{max,literature}$"])[y > 66]
y = y[y > 66]
#popt2, _ = curve_fit(quadraticPolynomial, x, y)
#upper_values = [x,2*y -quadraticPolynomial(y,*popt2)]

pl.figure()
arr = np.array(res_dat[r"Amount sigma"])
x = np.array([0,1,2,3,4,5,6,7,8,9,10])
hist,_ = np.histogram(arr,bins=x)
hist = hist / np.sum(hist)
pl.xlim(0.5,10)
pl.bar(x[:-1],hist,color='k',align='center')
formatter = FuncFormatter(to_percent)

# Set the formatter
pl.gca().yaxis.set_major_formatter(formatter)

pl.xlabel(r"#$\sigma$")
pl.ylabel(r"Number of $\nu_{max}$ within n*$\sigma$")
sum = 0
for i in range (1,5):
    sum += hist[i]
    sum_perc = sum*100
    print(f"Percentage within {i} sigma: {sum_perc}%")

cnt = 1
for j in [r"$\nu_{max,guess}$", r"Residual $\nu_{max,guess}$", r"Relative Residual $\nu_{max,guess}$",
          r"$\nu_{max,fit}$", r"Residual $\nu_{max,fit}$", r"Relative Residual $\nu_{max,fit}$"]:
    if cnt != 1:
        ax: Axes = fig.add_subplot(3, 3, cnt,sharex=ax)
    else:
        ax: Axes = fig.add_subplot(3, 3, cnt)
    lit_val = np.array(res_dat[r"$\nu_{max,literature}$"])
    ax.plot(lit_val, res_dat[j], 'x', markersize=2, color='k')

    if cnt == 1 or cnt == 4:
        ax.plot(lit_val, res_dat[r"$\nu_{max,literature}$"], markersize=2, color='k',
                linestyle='dashed', alpha=0.7)

    if cnt == 1:
        pass
        #ax.plot(lit_val, quadraticPolynomial(lit_val, *popt), 'x', markersize=5, color='red', alpha=0.7)
        #ax.plot(lit_val, quadraticPolynomial(lit_val, *popt2), 'x', markersize=5, color='blue', alpha=0.7)

    if cnt == 2:
        pass
        #ax.plot(lit_val, quadraticPolynomial(lit_val, *popt) - lit_val, 'x', markersize=5, color='red', alpha=0.7)
        #ax.plot(lit_val, quadraticPolynomial(lit_val, *popt2) - lit_val, 'x', markersize=5, color='blue', alpha=0.7)

    if cnt == 3:
        pass
        #ax.plot(lit_val, (quadraticPolynomial(lit_val, *popt) - lit_val) * 100 / lit_val, 'x', markersize=5,
        #        color='red', alpha=0.7)
        #ax.plot(lit_val, (quadraticPolynomial(lit_val, *popt2) - lit_val) * 100 / lit_val, 'x', markersize=5,
        #        color='blue', alpha=0.7)

    if cnt != 4:
        ax.set_ylim(min(res_dat[j])*1.2,max(res_dat[j])*1.2)


    ax.axhline(y=0, color='k')
    ax.set_ylabel(j)
    ax.set_xlabel(r"$\nu_{max,literature}$")
    cnt += 1

ax: Axes = fig.add_subplot(3, 3, 7,sharex = ax)
#ax.plot(lower_values[0], lower_values[1], 'x', markersize=2, color='red')
#ax.plot(upper_values[0], upper_values[1], 'x', markersize=2, color='blue')
ax.plot(lit_val, res_dat[r"$\nu_{max,literature}$"], markersize=2, color='k',
                linestyle='dashed', alpha=0.7)
ax.axhline(y=0, color='k')
ax.set_title("Guess normalized to fit")
ax.set_ylabel("Fitted values")

ax: Axes = fig.add_subplot(3, 3, 8,sharex = ax)
#ax.plot(lower_values[0], lower_values[1]-lower_values[0], 'x', markersize=2, color='red')
#ax.plot(upper_values[0], upper_values[1]-upper_values[0], 'x', markersize=2, color='blue')
ax.axhline(y=0, color='k')
ax.set_title("Guess normalized to fit")
ax.set_ylabel("Residual values")

ax: Axes = fig.add_subplot(3, 3, 9,sharex = ax)
#ax.plot(lower_values[0], 100*(lower_values[1]-lower_values[0])/lower_values[0], 'x', markersize=2, color='red')
#ax.plot(upper_values[0], 100*(upper_values[1]-upper_values[0])/upper_values[0], 'x', markersize=2, color='blue')
ax.axhline(y=0, color='k')
ax.set_title("Guess normalized to fit (Relative)")
ax.set_ylabel("Residual values")


def onclick(event: MouseEvent):
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))
    if event.dblclick:
        index = (np.abs(np.array(res_dat[r"$\nu_{max,literature}$"]) - event.xdata)).argmin()

        fig_im : Figure= pl.figure(figsize=(10, 6))
        print(res_dat["full_fit"][index])

        image = mpimg.imread(res_dat["full_fit"][index])
        pl.imshow(image)
        pl.axis('off')
        identifier = r'$\nu_{max,literature}$'
        pl.text(0.5, -0.1, rf"$\nu_{{max,literature}}$={res_dat[identifier][index]}",
                size=14, ha='center', transform=pl.gca().transAxes)

        pl.show(fig_im)


cid = fig.canvas.mpl_connect('button_press_event', onclick)

#print(f"Lower fit: {popt}")
#print(f"Upper fit: {popt2}")
#print(f"Lower std: {(lower_values[1]-lower_values[0]).std()}")
#print(f"Lower std relative: {((lower_values[1]-lower_values[0])*100/lower_values[0]).std()}")
#print(f"Upper std: {(upper_values[1]-upper_values[0]).std()}")
#print(f"Upper std relative: {((upper_values[1]-upper_values[0])*100/upper_values[0]).std()}")

pl.show(fig)
