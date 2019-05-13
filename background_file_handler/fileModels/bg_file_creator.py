# library imports
from typing import List, Dict
import os
# scientific imports
import numpy as np
# project imports
from res.conf_file_str import general_background_result_path, general_kic, general_background_data_path
from data_handler.signal_features import compute_periodogram
from support.directoryManager import cd
from res.conf_file_str import internal_noise_value,general_run_diamonds,internal_mag_value,internal_multiple_mag,\
    internal_path,analysis_folder_prefix
from support.printer import print_int
import shutil


def full_result_path(kwargs: Dict) -> str:
    """
    Generates the full results path from kic id and general results path
    :param kwargs: Run config
    """
    if general_background_result_path not in kwargs.keys():
        bg_result_path = kwargs[internal_path] + "/Background/results/"
    else:
        bg_result_path = kwargs[general_background_result_path]

    if general_kic not in kwargs.keys():
        raise AttributeError(f"You need to set '{general_kic}' in job file!")

    bg_result_path = bg_result_path + "" if bg_result_path.endswith("/") else "/"

    if not os.path.exists(bg_result_path):
        os.makedirs(bg_result_path)

    if internal_noise_value in kwargs.keys():
        return f"{bg_result_path}{kwargs[analysis_folder_prefix]}{kwargs[general_kic]}_n_{kwargs[internal_noise_value]}"
    elif internal_multiple_mag in kwargs.keys() and kwargs[internal_multiple_mag]:
        return f"{bg_result_path}{kwargs[analysis_folder_prefix]}{kwargs[general_kic]}_m_{kwargs[internal_mag_value]}"
    else:
        return f"{bg_result_path}{kwargs[analysis_folder_prefix]}{kwargs[general_kic]}"


def create_files(data: np.ndarray, nyq_f: float, priors: List[List[float]], kwargs: Dict):
    """
    Creates all files for a DIAMONDS run
    :param data: Lightcurve dataset
    :param nyq_f: Nyquist frequency
    :param priors: List of priors
    :param kwargs: Run configuratio
    """
    print_int(f"Path: {full_result_path(kwargs)}",kwargs)
    create_folder(full_result_path(kwargs),kwargs)
    create_data(compute_periodogram(data,kwargs), kwargs)
    create_priors(np.array(priors), full_result_path(kwargs))
    create_nsmc_configuring_parameters(full_result_path(kwargs))
    create_xmeans_configuring_parameters(full_result_path(kwargs))
    create_nyquist_frequency(nyq_f, full_result_path(kwargs))


def create_folder(res_path: str,kwargs : Dict):
    """
    Creates the result folder
    :param res_path: Results path
    """
    if (general_run_diamonds in kwargs.keys() and kwargs[general_run_diamonds]) or general_run_diamonds not in kwargs.keys():
        try:
            shutil.rmtree(res_path)
        except FileNotFoundError:
            pass

    if not os.path.exists(res_path):
        os.makedirs(res_path)



def create_priors(priors: np.ndarray, res_path: str):
    """
    Creates the files for the priors
    :param priors: Array of priors
    :param res_path: Result path
    """
    arr_full = priors
    arr_min = priors[:7]
    filename_full = "background_hyperParameters.txt"
    filename_min = "background_hyperParameters_noise.txt"
    save_numpy_array(res_path, filename_full, arr_full, '2','%.')
    save_numpy_array(res_path, filename_min, arr_min, '2','%.')

def nsmc_configuring_parameters() -> np.ndarray:
    """
    Lists the nsmc configuring parameters.
    """
    return np.array([500, 500, 50000, 1000, 50, 2.10, 0.1, 1.0]).transpose()

def create_nsmc_configuring_parameters(res_path: str):
    """
    Creates the nsmc configuration parameters
    :param res_path:  Result path
    """
    arr = nsmc_configuring_parameters()
    filename = "NSMC_configuringParameters.txt"
    save_numpy_array(res_path, filename, arr)
    return


def create_nyquist_frequency(nyq_f: float, res_path: str):
    """
    Creates the file with the nyquist frequency
    :param nyq_f: Nyquist frequency
    :param res_path: Result path
    """
    arr = np.array([nyq_f])
    filename = "NyquistFrequency.txt"
    save_numpy_array(res_path, filename, arr)


def create_xmeans_configuring_parameters(res_path: str):
    """
    Creates the file for the xmeans parameters
    :param res_path: Result path
    """
    arr = np.array([1, 10]).transpose()
    arr.transpose()
    filename = "Xmeans_configuringParameters.txt"
    save_numpy_array(res_path, filename, arr)
    return


def save_numpy_array(path, filename, array, comma='14',pre = '%10.'):
    """
    Saves a given numpy array
    :param path: path where the file is saved to
    :param filename: name of the file
    :param array: Array to be saved to
    :param comma: how many digits
    """
    with cd(path):
        np.savetxt(filename, array, fmt= pre + comma + 'f')


def create_data(f_data: np.ndarray, kwargs: Dict):
    """
    Creates the datafile (PSD)
    :param f_data: Frequency domain data of the data
    :param kwargs: Run configuration
    """
    if general_background_data_path not in kwargs.keys():
        path = kwargs[internal_path] + "/Background/data/"
    else:
        path = kwargs[general_background_data_path]

    if not os.path.exists(path):
        os.makedirs(path)

    if internal_noise_value in kwargs.keys():
        filename = f"{kwargs[analysis_folder_prefix]}{kwargs[general_kic]}_n_{kwargs[internal_noise_value]}.txt"
    elif internal_multiple_mag in kwargs.keys() and kwargs[internal_multiple_mag]:
        filename = f"{kwargs[analysis_folder_prefix]}{kwargs[general_kic]}_m_{kwargs[internal_mag_value]}.txt"
    else:
        filename = f"{kwargs[analysis_folder_prefix]}{kwargs[general_kic]}.txt"

    save_numpy_array(path, filename, f_data.T)
