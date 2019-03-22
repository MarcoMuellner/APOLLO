import numpy as np
from uncertainties import ufloat_fromstr
import json
from scripts.helper_functions import load_results, get_val
from scripts.helper_functions import f_max, full_background
from res.conf_file_str import general_kic, internal_literature_value, internal_mag_value, internal_teff, \
    general_analysis_result_path, analysis_list_of_ids, cat_general, analysis_obs_time_value, cat_analysis, \
    analysis_target_magnitude, analysis_nr_magnitude_points, analysis_number_repeats
from data_handler.signal_features import noise, get_mag
from json import load
from matplotlib import rcParams

params = {
    'axes.labelsize': 16,
    'legend.fontsize': 18,
    'xtick.labelsize': 18,
    'ytick.labelsize': 18,
    'text.usetex': False,
    'figure.figsize': [4.5, 4.5]
}
rcParams.update(params)

path = "../results/apokasc_results_full"
time = 27.4

res_list = load_results(path)
cnt = 0

data_list = []
for path, result, conf in res_list:
    bayes = get_val(result, "Bayes factor")
    nu_max = get_val(result[full_background], f_max)
    nu_max_lit = ufloat_fromstr(conf[internal_literature_value])

    if np.abs(nu_max - nu_max_lit) > ufloat_fromstr(conf[internal_literature_value]).std_dev:
        continue

    psd = np.load(f'{path}/psd.npy').T
    noise_val = noise(psd)
    mag = get_mag(noise_val)
    mag_lit = conf[internal_mag_value]

    if mag_lit < 11.6 or mag_lit > 12:
        continue

    diff = mag - mag_lit

    if np.abs(diff) > 0.4:
        continue

    delta_nu = get_val(conf, 'Literature value delta nu')
    data_list.append((conf[general_kic], nu_max_lit.nominal_value, nu_max_lit.std_dev,
                      delta_nu.nominal_value, delta_nu.std_dev, conf[internal_mag_value],
                      conf[internal_teff]))
    cnt += 1

np.savetxt(f"../sample_lists/{time}_mag_run.txt", np.array(data_list),
           fmt=['%d', '%.2f', '%.2f', '%.2f', '%.2f', '%.3f', '%d'],
           header='id nu_max nu_max_err delta_nu delta_nu_err mag T_eff')

with open("../run_cfg/magnitude_template.json", 'r') as f:
    kwargs_template = load(f)

kwargs_template[cat_analysis][analysis_obs_time_value] = time
kwargs_template[cat_general][general_analysis_result_path] = f"/home/marco/prog/LCA/results/mag_{time}/"
kwargs_template[analysis_list_of_ids] = f"sample_lists/{time}_mag_run.txt"
kwargs_template[cat_analysis][analysis_target_magnitude] = 15
kwargs_template[cat_analysis][analysis_nr_magnitude_points] = 10
kwargs_template[cat_analysis][analysis_number_repeats] = 2

with open(f"../run_cfg/mag_{time}.json",
          'w') as f:
    json.dump(kwargs_template, f, indent=4)

print(cnt)
print(cnt * 10 * 3)
