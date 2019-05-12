# library imports
from multiprocessing import Pool, cpu_count, Process
from copy import deepcopy
from typing import Dict, List, Tuple
import json
from os import makedirs, getcwd
import os
import traceback
import shutil
from uncertainties import ufloat, ufloat_fromstr
import time
# scientific imports
import numpy as np
# project imports
from data_handler.file_reader import load_file, look_for_file
from data_handler.data_refiner import refine_data,get_magnitude
from data_handler.signal_features import nyqFreq
from evaluators.compute_flicker import calculate_flicker_amplitude, flicker_amplitude_to_frequency
from evaluators.compute_nu_max import compute_nu_max, compute_fliper_exact
from evaluators.compute_priors import priors
from background_file_handler.fileModels.bg_file_creator import create_files
from background_file_handler.backgroundProcess import BackgroundProcess
from data_handler.write_results import save_results,is_bayes_factor_good
from res.conf_file_str import general_analysis_result_path
from support.directoryManager import cd
from support.printer import print_int, Printer
from res.conf_file_str import general_nr_of_cores, analysis_list_of_ids, general_kic, cat_analysis, cat_files, \
    cat_general, cat_plot, internal_literature_value, analysis_folder_prefix, general_sequential_run, \
    analysis_noise_values, internal_noise_value, analysis_number_repeats, internal_run_number, internal_delta_nu, \
    internal_mag_value, internal_teff, internal_path, general_run_diamonds, internal_force_run,general_check_bayes_run,\
    analysis_nr_noise_points,analysis_target_magnitude,analysis_nr_magnitude_points,internal_multiple_mag,\
    analysis_nu_max_outer_guess,internal_id,analysis_file_path
from support.exceptions import ResultFileNotFound, InputFileNotFound, EvidenceFileNotFound
import uuid

def deepcopy_dict(dict_object : Dict):
    cp = deepcopy(dict_object)
    cp[internal_id] = str(uuid.uuid4())
    return cp

def add_value_to_kwargs(kwargs, val, names, parameter, type_val):
    if names[0] in val.dtype.names:
        if len(names) == 2:
            if names[1] in val.dtype.names:
                kwargs[parameter] = type_val(val[names[0]], val[names[1]])
            else:
                kwargs[parameter] = type_val(val[names[0]], 0)
        else:
            try:
                kwargs[parameter] = type_val(val[names[0]])
            except AttributeError:
                kwargs[parameter] = type_val(val[names[0]], 0)
    return kwargs


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


    if sequential_run:  # MacOS cannot multiprocess for some reason. Stupid shit shit shit shit
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
    kwarg_list = []
    conf_file_list = conf_file.split(",")
    nr_of_cores = None
    for kwargs_file in conf_file_list:
        with open(kwargs_file, 'r') as f:
            kwargs = json.load(f)

        # determine number of cores
        if general_nr_of_cores not in kwargs[cat_general].keys() and nr_of_cores == None:
            nr_of_cores = 1
        elif nr_of_cores == None:
            nr_of_cores = kwargs[cat_general][general_nr_of_cores]

        if nr_of_cores > cpu_count():
            nr_of_cores = cpu_count()

        kwargs[cat_general][general_nr_of_cores] = nr_of_cores

        # Check analysis list!
        if analysis_list_of_ids not in kwargs.keys():
            raise ValueError(f"You need to set a list of ids to be analyzed with '{analysis_list_of_ids}'")

        copy_dict = {}

        # Copy all items from the general category
        for key, value in kwargs[cat_general].items():
            copy_dict[key] = value

        # Copy all items from the file category
        try:
            for key, value in kwargs[cat_files].items():
                copy_dict[key] = value
        except KeyError:
            pass

        # Copy all items from the plot category
        try:
            for key, value in kwargs[cat_plot].items():
                copy_dict[key] = value
        except:
            pass

        # Copy all items from analysis category
        for key, value in kwargs[cat_analysis].items():
            copy_dict[key] = value

        if ".txt" in str(kwargs[analysis_list_of_ids]):
            data = np.genfromtxt(str(kwargs[analysis_list_of_ids]), names=True).T
        else:
            data = kwargs[analysis_list_of_ids]

        if analysis_number_repeats in kwargs[cat_analysis]:
            repeat = int(kwargs[cat_analysis][analysis_number_repeats]) + 1
            repeat_set = True
        else:
            repeat = 2
            repeat_set = False

        try:
            mag_list = [i['mag'] for i in data]
        except TypeError:
            data = [data] # if single target in file, we need to create a list of data to make it iterable
            mag_list = [i['mag'] for i in data]

        if analysis_target_magnitude in kwargs[cat_analysis]:
            copy_dict[internal_multiple_mag] = True
        else:
            copy_dict[internal_multiple_mag] = False

        for i in data:
            for j in range(1, repeat):
                cp = deepcopy_dict(copy_dict)

                try:
                    cp = add_value_to_kwargs(cp, i, ['id'], general_kic, int)
                    cp = add_value_to_kwargs(cp, i, ['nu_max', 'nu_max_err'], internal_literature_value, ufloat)
                    cp = add_value_to_kwargs(cp, i, ['delta_nu', 'delta_nu_err'], internal_delta_nu, ufloat)
                    cp = add_value_to_kwargs(cp, i, ['mag'], internal_mag_value, float)
                    cp = add_value_to_kwargs(cp, i, ['T_eff'], internal_teff, float)
                except:
                    try:
                        cp[general_kic] = int(i)
                    except:
                        continue

                cp[internal_path] = getcwd()
                if not cp[analysis_file_path].startswith("/"):
                    cp[analysis_file_path] = f"{cp[internal_path]}/{cp[analysis_file_path]}"
                    #Adding working path if no absolute path was given for files

                if repeat_set:
                    if analysis_folder_prefix in cp:
                        pre = cp[analysis_folder_prefix]
                    else:
                        pre = "KIC"

                    cp[analysis_folder_prefix] = f"{pre}_{cp[general_kic]}/run_{j}"
                    cp[internal_run_number] = j

                if analysis_noise_values in kwargs[cat_analysis]:

                    if analysis_nr_noise_points in kwargs[cat_analysis].keys():
                        nr = kwargs[cat_analysis][analysis_nr_noise_points]
                    else:
                        nr = kwargs[cat_analysis][analysis_noise_values]*10

                    noise_values = np.linspace(0,kwargs[cat_analysis][analysis_noise_values],nr)

                    for k in noise_values:
                        k = float('%.1f' % k)
                        newcp = deepcopy_dict(cp)
                        newcp[internal_noise_value] = k
                        if analysis_folder_prefix in cp:
                            pre = newcp[analysis_folder_prefix]
                        else:
                            pre = "KIC"

                        if repeat_set:
                            pre = f"{pre}/noise_{k}"
                        else:
                            pre = f"{pre}_{cp[general_kic]}/noise_{k}"
                        newcp[analysis_folder_prefix] = pre
                        kwarg_list.append(newcp)

                elif analysis_target_magnitude in kwargs[cat_analysis]:
                    min_mag = max(mag_list)

                    if analysis_nr_magnitude_points in kwargs[cat_analysis].keys():
                        nr = kwargs[cat_analysis][analysis_nr_magnitude_points]
                    else:
                        nr = 5

                    mag_values = np.linspace(min_mag,kwargs[cat_analysis][analysis_target_magnitude],nr)
                    for k in mag_values:
                        k = float('%.1f' % k)
                        newcp = deepcopy_dict(cp)
                        copy_dict["Original magnitude"] = i['mag']
                        newcp[internal_mag_value] = k
                        if analysis_folder_prefix in cp:
                            pre = newcp[analysis_folder_prefix]
                        else:
                            pre = "KIC"

                        if repeat_set:
                            pre = f"{pre}/mag_{k}"
                        else:
                            pre = f"{pre}_{cp[general_kic]}/mag_{k}"
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
    t1 = time.time()
    if analysis_folder_prefix in kwargs.keys():
        prefix = kwargs[analysis_folder_prefix]
    else:
        prefix = "KIC"

    path = f"{kwargs[general_analysis_result_path]}{prefix}_{kwargs[general_kic]}/"
    if os.path.exists(path) and ((internal_force_run in kwargs.keys() and not kwargs[
        internal_force_run]) or internal_force_run not in kwargs.keys()):
        with cd(path):
            if os.path.exists("results.json") and not os.path.exists("errors.txt"):
                with open('results.json','r') as f:
                    old_res = json.load(f)
                kwargs["time"] = float(old_res['Runtime'])
                print_int("Done", kwargs)
                return

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
            #print_int("Starting run", kwargs)
            # load and refine data
            data = load_file(kwargs)
            with open("conf.json", 'w') as f:
                if internal_literature_value in kwargs.keys():
                    kwargs[internal_literature_value] = f"{kwargs[internal_literature_value]}"
                if internal_delta_nu in kwargs.keys():
                    kwargs[internal_delta_nu] = f"{kwargs[internal_delta_nu]}"

                json.dump(kwargs, f, indent=4)

                if internal_literature_value in kwargs.keys():
                    kwargs[internal_literature_value] = ufloat_fromstr(kwargs[internal_literature_value])
                if internal_delta_nu in kwargs.keys():
                    kwargs[internal_delta_nu] = ufloat_fromstr(kwargs[internal_delta_nu])

            data,kwargs = refine_data(data, kwargs)

            np.save("lc", data)

            # compute nu_max
            print_int("Computing nu_max", kwargs)
            """
            sigma_ampl = calculate_flicker_amplitude(data)
            f_ampl = flicker_amplitude_to_frequency(sigma_ampl)
            nu_max, f_list, f_fliper = compute_nu_max(data, f_ampl, kwargs)
            """
#            if internal_literature_value in kwargs:
#                nu_max = kwargs[internal_literature_value].nominal_value
#            else:
            if analysis_nu_max_outer_guess in kwargs.keys():
                nu_max = kwargs[analysis_nu_max_outer_guess]
            else:
                nu_max = compute_fliper_exact(data, kwargs)
            #nu_max = kwargs[internal_literature_value].nominal_value

            f_fliper = nu_max
            f_list = []

            if internal_literature_value in kwargs.keys():
                print_int(f"Nu_max guess: {'%.2f' % nu_max}, fliper: {f_fliper} literature: {kwargs[internal_literature_value]}", kwargs)
            else:
                print_int(f"Nu max guess: {'%.2f' % nu_max}, fliper: {f_fliper}", kwargs)

            # create files for diamonds and run
            prior, params = priors(nu_max, data, kwargs)
            print_int(f"Priors: {prior}", kwargs)

            cnt =1
            while cnt <=3:
                create_files(data, nyqFreq(data), prior, kwargs)
                proc = BackgroundProcess(kwargs)
                if general_run_diamonds in kwargs.keys():
                    if kwargs[general_run_diamonds]:
                        proc.run()
                else:
                    proc.run()

                if general_check_bayes_run in kwargs.keys():
                    if is_bayes_factor_good(kwargs):
                        break
                else:
                    break

                cnt +=1

            kwargs['Number of DIAMONDS runs'] = cnt
            print_int("Saving results", kwargs)
            # save results

            save_results(prior, data, nu_max, params, proc, f_list, f_fliper, t1, kwargs)
            delta_t = time.time() -t1
            kwargs["time"] = delta_t
            print_int("Done", kwargs)

        except (EvidenceFileNotFound, ResultFileNotFound, InputFileNotFound) as e:
            error = f"{e.__class__.__name__} : {str(e)}\n"
            print_int("Done", kwargs)
            trace = traceback.format_exc()
            with open("errors.txt", "w") as f:
                f.write(error)
                f.write(trace)
        except Exception as e:
            print_int("Done", kwargs)
            error = f"{e.__class__.__name__} : {str(e)}\n"
            trace = traceback.format_exc()
            with open("errors.txt", "w") as f:
                f.write(error)
                f.write(trace)
