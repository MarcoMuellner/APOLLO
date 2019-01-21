# library imports
from multiprocessing import Pool, cpu_count, Process
import platform
from copy import deepcopy
from typing import Dict, List, Tuple
import json
from os import makedirs
import traceback
import shutil
# scientific imports
import numpy as np
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
from support.printer import print_int, Printer
from res.conf_file_str import general_nr_of_cores, analysis_list_of_ids, general_kic, cat_analysis, cat_files, \
    cat_general, cat_plot, internal_literature_value, analysis_folder_prefix, general_sequential_run, \
    analysis_noise_values, internal_noise_value,analysis_number_repeats,internal_run_number,internal_delta_nu
from support.exceptions import ResultFileNotFound,InputFileNotFound,EvidenceFileNotFound


def run(screen, file: str):
    conf_list, nr_of_cores = kwarg_list(file)

    Printer.total_runs = len(conf_list)

    if general_sequential_run in conf_list[0]:
        sequential_run = conf_list[0][general_sequential_run]
    else:
        sequential_run = False

    if not sequential_run:
        Printer.set_screen(screen)
    else:
        Printer.set_screen(None)

    p = Process(target=Printer.run)
    p.start()

    if platform.system() == 'Darwin' or sequential_run:  # MacOS cannot multiprocess for some reason. Stupid shit shit shit shit
        for i in conf_list:
            run_star(i)
    else:
        pool = Pool(processes=nr_of_cores)
        pool.map(run_star, conf_list)

    # print_int("KILL_SIR",conf_list[0])
    p.join()


def kwarg_list(conf_file: str) -> Tuple[List[Dict], int]:
    """
    Returns a list of configuration for the runner
    :param conf_file: basic configuration filename
    :return: an iterable list of configurations
    """
    with open(conf_file, 'r') as f:
        kwargs = json.load(f)

    # determine number of cores
    if general_nr_of_cores not in kwargs[cat_general].keys():
        nr_of_cores = 1
    else:
        nr_of_cores = kwargs[cat_general][general_nr_of_cores]

    if nr_of_cores > cpu_count():
        raise ValueError(
            f"Nr of processors cannot be more than available in the pc! Available: {cpu_count()}. Will be used: {nr_of_cores}")

    # Check analysis list!
    if analysis_list_of_ids not in kwargs.keys():
        raise ValueError(f"You need to set a list of ids to be analyzed with '{analysis_list_of_ids}'")

    copy_dict = {}

    # Copy all items from the general category
    for key, value in kwargs[cat_general].items():
        copy_dict[key] = value

    # Copy all items from the file category
    for key, value in kwargs[cat_files].items():
        copy_dict[key] = value

    # Copy all items from the plot category
    for key, value in kwargs[cat_plot].items():
        copy_dict[key] = value

    # Copy all items from analysis category
    for key, value in kwargs[cat_analysis].items():
        copy_dict[key] = value

    kwarg_list = []

    if ".txt" in str(kwargs[analysis_list_of_ids]):
        data = np.loadtxt(str(kwargs[analysis_list_of_ids]))
        if data.shape[0] > 1000:
            data = data.T
        if data.shape[0] == 2:
            data = zip(data[0].astype(int).tolist(), data[1].toList())
        else:
            data = data.tolist()

    else:
        data = kwargs[analysis_list_of_ids]

    if analysis_number_repeats in kwargs[cat_analysis]:
        repeat = int(kwargs[cat_analysis][analysis_number_repeats]) + 1
        repeat_set = True
    else:
        repeat = 2
        repeat_set = False

    for i in data:
        for j in range(1,repeat):
            cp = deepcopy(copy_dict)

            try:
                if len(i) == 2:
                    cp[general_kic] = int(i[0])
                    cp[internal_literature_value] = i[1]
                if len(i) == 3:
                    cp[internal_delta_nu] = i[2]
            except:
                cp[general_kic] = int(i)

            if repeat_set:
                if analysis_folder_prefix in cp:
                    pre = cp[analysis_folder_prefix]
                else:
                    pre = "KIC"

                cp[analysis_folder_prefix] = f"{pre}_{cp[general_kic]}/run_{j}"
                cp[internal_run_number] = j

            if analysis_noise_values in kwargs[cat_analysis]:
                for k in kwargs[cat_analysis][analysis_noise_values]:
                    newcp = deepcopy(cp)
                    newcp[internal_noise_value] = k
                    if analysis_folder_prefix in cp:
                        pre  = newcp[analysis_folder_prefix]
                    else:
                        pre = "KIC"

                    if repeat_set:
                        pre = f"{pre}/noise_{k}"
                    else:
                        pre = f"{pre}_{cp[general_kic]}/noise_{k}"
                    newcp[analysis_folder_prefix] = pre
                    kwarg_list.append(newcp)
            else:
                kwarg_list.append(cp)

    return kwarg_list, nr_of_cores


def run_star(kwargs: Dict):
    """
    Runs a full analysis for a given kwargs file.
    :param kwargs: Run conf
    """
    if analysis_folder_prefix in kwargs.keys():
        prefix = kwargs[analysis_folder_prefix]
    else:
        prefix = "KIC"

    path = f"{kwargs[general_analysis_result_path]}{prefix}_{kwargs[general_kic]}/"
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        pass
    try:
        makedirs(path)
    except FileExistsError:
        pass

    with cd(path):
        try:
            with open("conf.json", 'w') as f:
                json.dump(kwargs, f, indent=4)

            print_int("Starting run", kwargs)
            # load and refine data
            data = load_file(kwargs)
            data = refine_data(data, kwargs)

            # compute nu_max
            sigma_ampl = calculate_flicker_amplitude(data)
            f_ampl = flicker_amplitude_to_frequency(sigma_ampl)
            print_int("Computing nu_max", kwargs)
            nu_max,n_runs = compute_nu_max(data, f_ampl, kwargs)

            if internal_literature_value in kwargs.keys():
                print_int(f"Nu_max guess: {'%.2f' % nu_max}, literature: {'%.2f' % kwargs[internal_literature_value]}",
                          kwargs)
            else:
                print_int(f"Nu max guess: {'%.2f' % nu_max}", kwargs)

            # create files for diamonds and run
            prior, params = priors(nu_max, data, kwargs)
            print_int(f"Priors: {prior}", kwargs)

            create_files(data, nyqFreq(data), prior, kwargs)
            proc = BackgroundProcess(kwargs)
            proc.run()

            print_int("Saving results", kwargs)
            # save results

            save_results(prior, data, nu_max, params,proc,n_runs, kwargs)
            print_int("Done", kwargs)
        except (EvidenceFileNotFound,ResultFileNotFound,InputFileNotFound) as e:
            error = f"{e.__class__.__name__} : {str(e)}\n"
            trace = traceback.format_exc()
            with open("errors.txt", "w") as f:
                f.write(error)
                f.write(trace)
        except Exception as e:
            print_int("Failed", kwargs)  #
            error = f"{e.__class__.__name__} : {str(e)}\n"
            trace = traceback.format_exc()
            with open("errors.txt", "w") as f:
                f.write(error)
                f.write(trace)
