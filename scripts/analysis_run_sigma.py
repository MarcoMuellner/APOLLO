import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np

from scripts.helper_functions import load_results, get_val
from scripts.helper_functions import f_max, full_background
from res.conf_file_str import general_kic, internal_literature_value, internal_delta_nu
from pandas import DataFrame
from uncertainties import ufloat, ufloat_fromstr

from matplotlib import rcParams

params = {
   'axes.labelsize': 20,
#   'text.fontsize': 8,
   'legend.fontsize': 18,
   'xtick.labelsize': 18,
   'ytick.labelsize': 18,
   'text.usetex': False,
   'figure.figsize': [4.5, 4.5]
   }
rcParams.update(params)

def plot_data(x, y, err, x_label, y_label, save_path):
    fig, (a_plot, a_residual) = pl.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]}, figsize=(16, 10), sharex=True)
    fig: Figure
    a_plot: Axes
    a_residual: Axes
    pos_err = x + err
    neg_err = x - err

    a_plot.plot(x, y, 'o', markersize=2, color='k')
    a_plot.plot(x, x, linewidth=1, color='grey', alpha=0.2)
    a_plot.fill_between(x, pos_err, neg_err, color='red', alpha=0.2)

    print(f"Mean err: {'%.2f' % np.mean((y - x)/err)}")

    a_residual.plot(x, (y - x)/err, 'o', markersize=2, color='k')
    a_residual.plot(x, np.zeros(len(x)), linewidth=1, color='black', alpha=0.5)
    a_residual.fill_between(x, 1,-1, color='red', alpha=0.2)

    a_plot.set_xlabel(x_label)
    a_plot.set_ylabel(y_label)
    a_residual.set_xlabel(x_label)
    a_residual.set_ylabel("Residual in sigma")

    a_plot.set_xlim(min(x)*0.95,max(x))

    fig.tight_layout()
    fig.subplots_adjust(hspace=0)
    fig.savefig(save_path)


pl.rc('font', family='serif')

input_path = ["../results/apokasc_results_full"]
res_path = "../plots/"

try:
    os.makedirs(res_path)
except:
    pass

total = {}
res_list = []
res = {
    "id": [],
    "nu_max": [],
    "nu_max_err": [],
    "delta_nu": [],
    "delta_nu_err": [],
    "nu_max_lit": [],
    "nu_max_lit_err": [],
    "delta_nu_lit": [],
    "delta_nu_lit_err": [],
    "f_guess": [],
    "evidence": [],
    "bayes_factor": [],
    "bayes_factor_error": [],
    "image_path": []
}

for i in input_path:
    res_list += load_results(i)

for path, result, conf in res_list:
    kic_id = conf[general_kic]
    nu_max_lit = ufloat_fromstr(conf[internal_literature_value])
    delta_nu_lit = ufloat_fromstr(conf[internal_delta_nu])
    try:
        #nu_max = get_val(result, "nu_max_gauss")
        nu_max = get_val(result[full_background], f_max)
        if nu_max is None:
            nu_max = get_val(result[full_background], f_max)
    except:
        nu_max = get_val(result[full_background], f_max)
    try:
        delta_nu = get_val(result, 'Delta nu')
        if delta_nu is None or isinstance(delta_nu,str):
            delta_nu = ufloat(np.nan, np.nan)
    except:
        delta_nu = ufloat(np.nan, np.nan)

    f_guess = result["Nu max guess"]
    bayes_factor = get_val(result, "Bayes factor")

    if bayes_factor < 5:
        print(f"Skpping {conf[general_kic]} --> bayes value: {get_val(result, 'Bayes factor')}")
        continue

    mask = np.abs(np.array(res['nu_max_lit'])-nu_max_lit.nominal_value) < 0.1
    if len(np.array(res['nu_max_lit'])) > 1:
        pass

    res["id"].append(kic_id)
    res["nu_max"].append(nu_max.nominal_value)
    res["nu_max_err"].append(nu_max.std_dev)
    try:
        res["delta_nu"].append(delta_nu.nominal_value)
    except:
        pass

    res["delta_nu_err"].append(delta_nu.std_dev)
    res["delta_nu_lit"].append(delta_nu_lit.nominal_value)
    res["delta_nu_lit_err"].append(delta_nu_lit.std_dev)
    res["nu_max_lit"].append(nu_max_lit.nominal_value)
    res["nu_max_lit_err"].append(nu_max_lit.std_dev)
    res["f_guess"].append(f_guess)
    res["evidence"].append(result["Conclusion"])
    res["bayes_factor"].append(bayes_factor.nominal_value)
    res["bayes_factor_error"].append(bayes_factor.std_dev)
    res["image_path"].append(f"{path}/images")

df = DataFrame(data=res)
df = df.sort_values(by=['nu_max_lit'])

plot_data(df.nu_max_lit, df.nu_max, df.nu_max_lit_err, r"$\nu_{{\mathrm{{max,literature}}}}$",
          r"$\nu_{{\mathrm{{max,LCA}}}}$", f"{res_path}nu_max_values.pdf")

df = df.sort_values(by=['delta_nu_lit'])

plot_data(df.delta_nu_lit, df.delta_nu, df.delta_nu_lit_err, r"$\Delta\nu_{{\mathrm{{literature}}}}$",
          r"$\Delta\nu_{{\mathrm{{max,LCA}}}}$", f"{res_path}delta_nu_values.pdf")

#pl.show()
