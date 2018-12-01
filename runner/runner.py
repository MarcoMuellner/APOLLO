# library imports
from multiprocessing import Pool, cpu_count
from multiprocessing.pool import ThreadPool
import time
import platform
from copy import deepcopy
from typing import Dict
import json
from os import makedirs
# scientific imports
# project imports
from data_handler.file_reader import load_file
from data_handler.data_refiner import refine_data
from data_handler.signal_features import nyqFreq
from evaluators.compute_flicker import calculate_flicker_amplitude, flicker_amplitude_to_frequency
from evaluators.compute_nu_max import compute_nu_max
from evaluators.compute_priors import priors
from background.fileModels.bg_file_creator import create_files
from background.backgroundProcess import BackgroundProcess
from data_handler.write_results import save_results
from res.conf_file_str import general_analysis_result_path
from support.directoryManager import cd
from support.printer import print_int
from res.conf_file_str import general_nr_of_cores, analysis_list_of_ids, general_kic, cat_analysis, cat_files, \
    cat_general, cat_plot, analysis_file_path,analysis_folder_prefix


def run_star(kwargs: Dict):
    if analysis_folder_prefix in kwargs.keys():
        prefix = kwargs[analysis_folder_prefix]
    else:
        prefix = "KIC"


    path = f"{kwargs[general_analysis_result_path]}{prefix}_{kwargs[general_kic]}/"
    try:
        makedirs(path)
    except FileExistsError:
        pass

    with cd(path):

        print_int("Starting run", kwargs)
        # load and refine data
        data = load_file(kwargs)
        data = refine_data(data, kwargs)

        # compute nu_max
        sigma_ampl = calculate_flicker_amplitude(data)
        f_ampl = flicker_amplitude_to_frequency(sigma_ampl)
        nu_max = compute_nu_max(data, f_ampl, kwargs)
        print_int(f"Nu max guess: {'%.2f' % nu_max}", kwargs)

        # create files for diamonds and run
        create_files(data, nyqFreq(data), priors(nu_max, data), kwargs)
        proc = BackgroundProcess(kwargs)
        proc.run()

        print_int("Saving results", kwargs)
        # save results
        save_results(priors(nu_max, data), data, kwargs)
        print_int("Done", kwargs)


def run(file: str):
    with open(file, 'r') as f:
        kwargs = json.load(f)

    if general_nr_of_cores not in kwargs[cat_general].keys():
        nr_of_cores = 1
    else:
        nr_of_cores = kwargs[cat_general][general_nr_of_cores]

    if nr_of_cores * 2 > cpu_count():
        raise ValueError(
            f"Nr of processors cannot be more than available in the pc! Available: {cpu_count()}. Will be used: {nr_of_cores}")

    if analysis_list_of_ids not in kwargs[cat_analysis].keys():
        raise ValueError(f"You need to set a list of ids to be analyzed with '{analysis_list_of_ids}'")

    copy_dict = {}

    for key, value in kwargs[cat_general].items():
        copy_dict[key] = value

    for key, value in kwargs[cat_files].items():
        copy_dict[key] = value

    for key, value in kwargs[cat_plot].items():
        copy_dict[key] = value

    copy_dict[analysis_file_path] = kwargs[cat_analysis][analysis_file_path]

    if analysis_folder_prefix in kwargs[cat_analysis].keys():
        copy_dict[analysis_folder_prefix] = kwargs[cat_analysis][analysis_folder_prefix]

    kwarg_list = []

    for i in kwargs[cat_analysis][analysis_list_of_ids]:
        cp = deepcopy(copy_dict)
        cp[general_kic] = i
        kwarg_list.append(cp)

    if platform.system() == 'Darwin': #MacOS cannot multiprocess for some reason. Stupid shit shit shit shit
        for i in kwarg_list:
            run_star(i)
    else:
        pool = Pool(processes=nr_of_cores)
        pool.map(run_star,kwarg_list)
