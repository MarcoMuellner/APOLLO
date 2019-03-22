import argparse
import os
from json import load
import re
import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseEvent
import numpy as np
from uncertainties import ufloat_fromstr, unumpy as unp, ufloat, nominal_value, std_dev
from scipy.optimize import curve_fit
from os import makedirs
from shutil import rmtree
from typing import Union
from res.conf_file_str import internal_literature_value
import json
from scripts.helper_functions import load_results, get_val, recreate_dir, full_nr_of_runs
from scripts.helper_functions import f_max, full_background, delta_nu
from pandas import DataFrame
from res.conf_file_str import general_kic, internal_literature_value, internal_delta_nu, analysis_obs_time_value, \
    internal_mag_value, internal_teff,general_analysis_result_path,analysis_list_of_ids,cat_general,analysis_obs_time_value,cat_analysis
from data_handler.signal_features import background_model
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import kde
from data_handler.signal_features import noise,get_mag
from json import load,dump
from fitter.fit_functions import scipyFit,linearPolynomial

main_paths = [
#"../results/apokasc_results_full/",
#"../results/apokasc_results_full_356_days/",
#"../results/apokasc_results_full_109_days/",
#"../results/apokasc_results_full_82_days/",
#"../results/apokasc_results_full_54_days/",
#"../results/apokasc_results_full_27_days/",
#    "../results/noise_7_237_109/"
#"../results/noise_7_237_109/",
"../results/noise_85_163_109/",
"../results/noise_124_242_109/",
"../results/noise_163_242_109/",
              ]


for main_path  in main_paths:
    res_list = load_results(main_path)

    res_data = {
        'snr': [],
        'snr_bg': [],
        'snr_bg_ln': [],
        'snr_real': [],
        'snr_real_divided_bg': [],
        'w': [],
        'h': [],
        'model_bg': [],
        'model_total': [],
        "model_total_noise": [],
        'model_osc': [],
        'nu_max': [],
        'nu_max_lit': [],
        'bayes': [],
        'a_1': [],
        'a_2': [],
        'a_3': [],
        'id':[]
    }

    redo_name = "noise_candidates.txt"
    out_path = "../sample_lists/"

    data_list = []
    nu_max_list = []

    for path, result, conf in res_list:
        psd = np.load(f'{path}/psd.npy').T

        try:
            fit_res = result["Full Background result"]
        except:
            continue
        fit_res_noise = result["Noise Background result"]

        for key, value in fit_res.items():
            fit_res[key] = ufloat_fromstr(value).nominal_value

        for key, value in fit_res_noise.items():
            fit_res_noise[key] = ufloat_fromstr(value).nominal_value

        a_long = fit_res['$\sigma_\mathrm{long}$']
        a_gran_1 = fit_res['$\sigma_\mathrm{gran,1}$']
        a_gran_2 = fit_res['$\sigma_\mathrm{gran,2}$']

        nyq = 277
        model = background_model(psd, nyq, fit_res['w'], fit_res["$\\sigma_\\mathrm{long}$"], fit_res["$b_\\mathrm{long}$"],
                                 fit_res["$\\sigma_\\mathrm{gran,1}$"], fit_res["$b_\\mathrm{gran,1}$"],
                                 fit_res["$\\sigma_\\mathrm{gran,2}$"],
                                 fit_res["$b_\\mathrm{gran,2}$"], fit_res["$f_\\mathrm{max}$ "],
                                 fit_res["$H_\\mathrm{osc}$"],
                                 fit_res["$\\sigma_\\mathrm{env}$"])

        model_noise = background_model(psd, nyq, fit_res_noise['w'], fit_res_noise["$\\sigma_\\mathrm{long}$"],
                                       fit_res_noise["$b_\\mathrm{long}$"],
                                       fit_res_noise["$\\sigma_\\mathrm{gran,1}$"], fit_res_noise["$b_\\mathrm{gran,1}$"],
                                       fit_res_noise["$\\sigma_\\mathrm{gran,2}$"],
                                       fit_res_noise["$b_\\mathrm{gran,2}$"])

        nu_max = get_val(result[full_background], f_max)
        nu_max_lit = ufloat_fromstr(conf[internal_literature_value]).nominal_value

        w = get_val(result["Full Background result"], "w")
        h = get_val(result["Full Background result"], "$H_\\mathrm{osc}$")
        bayes = get_val(result, "Bayes factor")

        if np.abs(nu_max - nu_max_lit) > ufloat_fromstr(conf[internal_literature_value]).std_dev:
            continue

        # if not 80 < nu_max_lit < 120:
        #    continue

        arg_nu_max = np.argmin(np.abs(psd[0] - nu_max))

        res_data['snr_bg'].append((h / w))
        res_data['snr_bg_ln'].append((np.log(h) / np.log(np.sum(model[0:4], axis=0)[arg_nu_max])))
        res_data['snr'].append((h / (w)))
        res_data['w'].append(w)
        res_data['h'].append(h)
        res_data['bayes'].append(bayes.nominal_value)
        res_data['model_bg'].append(np.sum(model[0:4]))
        res_data['model_total'].append(np.sum(model))
        res_data['model_total_noise'].append(np.sum(model_noise))
        res_data['model_osc'].append(np.sum(model[4]))
        res_data['nu_max'].append(nu_max)
        res_data['nu_max_lit'].append(nu_max_lit)
        res_data['a_1'].append(a_long)
        res_data['a_2'].append(a_gran_1)
        res_data['a_3'].append(a_gran_2)
        res_data['id'].append(conf[general_kic])

        f_data = psd[1] / np.sum(model[:4], axis=0)

        sigma = get_val(result[full_background], "$\sigma_\mathrm{env}$")
        lower_mask = np.logical_and(psd[0] < nu_max - sigma, psd[0] > nu_max - 2 * sigma)
        upper_mask = np.logical_and(psd[0] > nu_max + sigma, psd[0] < nu_max + 2 * sigma)
        osc_region = np.logical_and(psd[0] > nu_max - sigma, psd[0] < nu_max + sigma)

        #    max_amp = psd[1][np.where(psd[0] == nu_max)]
        max_amp_bg_div = np.amax(f_data[osc_region])
        max_amp = np.amax(psd[1][osc_region])
        noise_bg_div = np.mean(np.hstack((f_data[lower_mask], f_data[upper_mask])))
        noise_fit = np.mean(np.hstack((psd[1][lower_mask], psd[1][upper_mask])))
        res_data["snr_real"].append(max_amp / noise_fit)
        res_data["snr_real_divided_bg"].append(max_amp_bg_div / noise_bg_div)

        noise_val = noise(psd)
        mag = get_mag(noise_val)
        mag_lit = conf[internal_mag_value]
        diff = mag - mag_lit
        nu_max_lit = ufloat_fromstr(conf[internal_literature_value])
        delta_nu = get_val(result, 'Delta nu')
        if delta_nu is None:
            delta_nu = ufloat(0,0)
        if  np.abs(diff) < 0.5 and np.abs(nu_max_lit.nominal_value - nu_max) < nu_max_lit.std_dev:
            data_list.append((conf[general_kic], nu_max_lit, max_amp_bg_div / noise_bg_div,
                              (conf[general_kic], nu_max_lit.nominal_value, nu_max_lit.std_dev,
                               delta_nu.nominal_value, delta_nu.std_dev, conf[internal_mag_value],
                               conf[internal_teff])))
            nu_max_list.append((conf[general_kic], nu_max_lit))

    arr_nu_max_list = np.array(nu_max_list).T
    if len(arr_nu_max_list) == 0:
        continue
    bins = np.linspace(min(arr_nu_max_list[1]), max(arr_nu_max_list[1]), num=4)
    #bins = [min(arr_nu_max_list[1]), max(arr_nu_max_list[1]),max(arr_nu_max_list[1])]
    run_lists = {}

    for i, bin in enumerate(bins[:-1]):
        continue
        mask = np.logical_and(arr_nu_max_list[1] > bin, arr_nu_max_list[1] < bins[i + 1])
        ids = arr_nu_max_list[0][mask]
        data_dict_write = {
            'id': [],
            'snr': [],
            'data': []
        }
        for (kic_id, nu_max, snr, data) in data_list:
            if kic_id not in ids:
                continue
            data_dict_write['id'].append(kic_id)
            data_dict_write['snr'].append(snr)
            data_dict_write['data'].append(data)

        df_run_lists = DataFrame.from_dict(data_dict_write)
        max_n = 20 if len(df_run_lists.snr.values) > 10 else len(df_run_lists.snr.values)
        min_snr_vals_args = np.argsort(df_run_lists.snr.values)[0:max_n]
        min_nu,max_nu = '%d' % bin.nominal_value,'%d' % bins[i + 1].nominal_value
        data = df_run_lists.data.values[min_snr_vals_args]

        if len(data) <= 1:
            continue

        try:
            np.savetxt(f"{out_path}noise_{min_nu}_{max_nu}.txt", np.array(data.tolist()),
                  fmt=['%d', '%.2f', '%.2f', '%.2f', '%.2f', '%.3f', '%d'],header='id nu_max nu_max_err delta_nu delta_nu_err mag T_eff')
            pass
        except:
            pass

        with open("../run_cfg/noise_template.json",'r') as f:
            kwargs_template = load(f)

        kwargs_template[cat_analysis][analysis_obs_time_value] = 109.6
        kwargs_template[cat_general][general_analysis_result_path] = f"/home/marco/prog/LCA/results/noise_{min_nu}_{max_nu}_{int(kwargs_template[cat_analysis][analysis_obs_time_value])}/"
        kwargs_template[analysis_list_of_ids] = f"sample_lists/noise_{min_nu}_{max_nu}.txt"

        with open(f"../run_cfg/noise_{min_nu}_{max_nu}_{int(kwargs_template[cat_analysis][analysis_obs_time_value])}_days.json",'w') as f:
            json.dump(kwargs_template, f, indent=4)




    df = DataFrame.from_dict(res_data)


    def discrete_cmap(N, base_cmap='Set1'):
        """Create an N-bin discrete colormap from the specified input map"""

        # Note that if base_cmap is a string or None, you can simply do
        return pl.cm.get_cmap(base_cmap, N)
        # The following works for string, None, or a colormap instance:

        base = pl.cm.get_cmap(base_cmap)
        color_list = base(np.linspace(0, 1, N))
        cmap_name = base.name + str(N)
        return base.from_list(cmap_name, color_list, N)

    def plot_points(ax_top: Axes, ax_low: Axes, fig: Figure, x, y, z, title, ylabel, x_label,fit=True):
        mask = x < 60  # max(x)/2
        x = x[mask]
        y = y[mask]
        z = z[mask]

        if fit:
            try:
                popt,perr = scipyFit(x,y,linearPolynomial)
                ax_top.plot(x,linearPolynomial(x,*popt),linewidth=1,color='red')
                a = ufloat(popt[0],perr[0])
                b = ufloat(popt[1], perr[1])
                print(f"{title}: Threshold: {(np.log10(5) - a)/b}")
            except:
                pass

        map = ax_top.scatter(x, y, c=np.log(z))


        fig.colorbar(map, ax=ax_top)#,ticks=range(len(z)))
        # ax_top.set_xlim(1.1 * max(x), 0.8 * min(x))
        ax_top.invert_xaxis()
        ax_top.set_title(title)
        ax_top.set_ylabel(ylabel)
        ax_top.axhline(y=np.log10(5),color='k',linestyle='dashed')
        #ax_top.set_xscale('log')

        bins = np.linspace(min(x), max(x), num=int(len(x)/10))

        mean_list = []
        mean_z = []
        x_arr = np.array(x)
        y_arr = np.array(y)

        for i, bin in enumerate(bins[:-1]):
            mask = np.logical_and(x_arr > bin, x_arr < bins[i + 1])
            mean = np.mean(y_arr[mask])
            std = np.mean(y_arr[mask])
            n = np.sqrt(len(x_arr[mask]))
            mean_z.append(np.median(z[mask]))

            mean_list.append(ufloat(mean, np.abs(std) / n))

        nominal = unp.nominal_values(mean_list)
        uncertainties = unp.std_devs(mean_list)

        map_2 = ax_low.scatter(bins[:-1], nominal, c=np.log(mean_z))
        fig.colorbar(map_2, ax=ax_low)#,ticks=range(len(z)))
        ax_low.errorbar(bins[:-1], nominal, yerr=uncertainties, fmt='', marker='', alpha=0.5)
        # pl.xscale('log')

        if fit:
            try:
                popt,perr = scipyFit(bins[:-1],nominal,linearPolynomial,sigma=uncertainties)
                ax_low.plot(bins[:-1],linearPolynomial(bins[:-1],*popt),linewidth=1,color='red')
                a = ufloat(popt[0],perr[0])
                b = ufloat(popt[1], perr[1])
                print(f"{title}: Threshold: {(np.log10(5) - a)/b}")
            except:
                pass


        min_x = -1 if min(x) < 1 else 0.1 * min(x)
        # ax_low.set_xlim(max(x) + 2 , min(x) - 2)
        ax_low.invert_xaxis()
        ax_low.set_ylabel(ylabel + " binned")
        ax_low.axhline(y=np.log10(5), color='k', linestyle='dashed')
        #ax_low.set_xscale('log')
        ax_low.set_xlabel(x_label)


    fig, ax_list = pl.subplots(2, 3, sharey=True, figsize=(16, 10))
    fig:Figure
    print(main_path)
    plot_points(ax_list[0][0], ax_list[1][0], fig, df.snr_real_divided_bg, df.bayes, df.nu_max, "SNR classic divided",
                "Bayes Factor", "snr old")
    plot_points(ax_list[0][1], ax_list[1][1], fig, df.snr_real, df.bayes, df.nu_max, "SNR classic", "Bayes Factor", "snr")
    # plot_points(ax_list[0][2],ax_list[1][2],fig,df.model_total/df.model_total_noise,df.bayes,df.nu_max,"Models","Bayes Factor","models")
    plot_points(ax_list[0][2], ax_list[1][2], fig, df.snr, df.bayes, df.nu_max, "$H_{{osc}}$/$w$", "Bayes Factor",
                "snr old")
    """
    plot_points(ax_list[0][0],ax_list[1][0],fig,df.snr,df.bayes,df.nu_max,"$H_{{osc}}$/$w$","Bayes Factor","snr old")
    #plot_points(ax_list[0][0],ax_list[1][0],fig,df.snr_bg,df.bayes,df.nu_max,"$H_{{osc}}$/$bg$","Bayes Factor","snr with bg")
    plot_points(ax_list[0][1],ax_list[1][1],fig,df.snr_bg_ln,df.bayes,df.nu_max,"SNR classic","Bayes Factor","sn with ln bgr")
    #plot_points(ax_list[0][2],ax_list[1][2],fig,df.model_total/df.model_total_noise,df.bayes,df.nu_max,"Models","Bayes Factor","models")
    """
    #fig.subplots_adjust(hspace=0)
    fig.suptitle(main_path)
    file_name = main_path.split("/")[-2]
    fig.savefig(f"../plots/SNR_progression_{file_name}.pdf")
    #pl.tight_layout()

pl.show()
