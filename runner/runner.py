# library imports
from multiprocessing import Pool,cpu_count
from copy import deepcopy
from typing import Dict
import json
# scientific imports
# project imports
from data_handler.file_reader import load_file
from data_handler.data_refiner import refine_data
from data_handler.signal_features import compute_periodogram, nyqFreq
from evaluators.compute_flicker import calculate_flicker_amplitude, flicker_amplitude_to_frequency
from evaluators.compute_nu_max import compute_nu_max
from evaluators.compute_priors import priors
from background.fileModels.bg_file_creator import create_files
from background.backgroundProcess import BackgroundProcess
from data_handler.write_results import save_results
from res.conf_file_str import general_analysis_result_path
from support.directoryManager import cd
from support.printer import print_int
from res.conf_file_str import general_nr_of_cores,analysis_list_of_ids,general_kic


def run_star(kwargs : Dict):
    with cd(kwargs[general_analysis_result_path]):

        print_int("Starting run",kwargs)
        #load and refine data
        data = load_file(kwargs)
        data = refine_data(data, kwargs)

        #compute nu_max
        sigma_ampl = calculate_flicker_amplitude(data)
        f_ampl = flicker_amplitude_to_frequency(sigma_ampl)
        nu_max = compute_nu_max(data, f_ampl, kwargs)
        print_int(f"Nu max guess: {'%.2f'%nu_max}", kwargs)

        #create files for diamonds and run
        create_files(data, nyqFreq(data), priors(nu_max, data), kwargs)
        proc = BackgroundProcess(kwargs)
        proc.run()

        print_int("Saving results",kwargs)
        #save results
        save_results(priors(nu_max, data), data, kwargs)

def run(file : str):
    with open(file, 'r') as f:
        kwargs = json.load(f)

    if general_nr_of_cores not in kwargs.keys():
        nr_of_cores = 2
    else:
        nr_of_cores = kwargs[general_nr_of_cores]

    if nr_of_cores*2 < cpu_count():
        raise ValueError("Nr of processors cannot be more than available in the pc!")


    if analysis_list_of_ids not in kwargs.keys():
        raise ValueError(f"You need to set a list of ids to be analyzed with '{analysis_list_of_ids}'")

    kwarg_list = []
    for i in kwargs[analysis_list_of_ids]:
        cp = deepcopy(kwargs)
        cp[general_kic] = i
        del cp[analysis_list_of_ids]
        kwarg_list.append(cp)

    pool = Pool(processes=nr_of_cores)

    for run_dict in kwarg_list:
        pool.apply(run_star,args=(run_dict,))