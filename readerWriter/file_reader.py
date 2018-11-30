# standard imports
from typing import Dict
from os.path import isfile
# scientific imports
import numpy as np
from astropy.io import fits
# project imports
from res.file_load_str import fits_type
from res.conf_file_str import fits_flux_column, fits_time_column, fits_hdulist_column, ascii_skiprows, ascii_use_cols


def load_file(file_name: str, kwargs: Dict) -> np.ndarray:
    """
    Loads the dataset into the memory and returns it accordingly
    :param file_name: Name of the file including the path
    :param kwargs: Content of conf file.
    :return: 2D numpy array
    """
    check_file_exists(file_name)

    if file_name.endswith(fits_type):
        data = load_fits_file(file_name, kwargs)
    else:
        data = load_ascii_file(file_name, kwargs)

    return transpose_if_necessary(data)


def check_file_exists(file_name: str) -> None:
    """
    Checks if the file is on the filesystem and readable
    :param file_name: Name of the file including the path
    """
    if not isfile(file_name):
        raise FileNotFoundError(f"Cannot find {file_name}. Check if path is correct!")


def load_fits_file(file_name: str, kwargs: Dict) -> np.ndarray:
    """
    Loads fits files into the memory and returns accordingly. You need to specify time and flux columns as well
    as the hdulist column that should be used!. No check if the file exists happens outside of the open function.
    Therefore you need to make sure beforehand!
    :param file_name: Name of the file including the path
    :param kwargs: Content of conf file.
    :return: 2D numpy array
    """
    if fits_hdulist_column not in kwargs.keys() or not isinstance(kwargs[fits_hdulist_column], int):
        raise AttributeError(f"Reading of fits files requires to set the '{fits_hdulist_column}' and "
                             f"it to be an integer!")

    hdulist = fits.open(file_name)
    rawData = hdulist[kwargs[fits_hdulist_column]].data

    if len(rawData.shape) == 2:
        return rawData

    if fits_flux_column not in kwargs.keys() or fits_time_column not in kwargs.keys():
        raise AttributeError(f"Reading of this fits files requires to set the '{fits_flux_column}' "
                             f"and '{fits_time_column}' values")

    return np.array((rawData[kwargs[fits_time_column]], rawData[kwargs[fits_flux_column]]))


def load_ascii_file(file_name, kwargs):
    """
    Loads ascii files into the memory and returns accordingly. You can specify the rows to skip and used columns
    in the config file. No check if the file exists happens outside of the loadtxt function. Therefore you need
    to make sure beforehand!
    :param file_name: Name of the file including the path
    :param kwargs: Content of conf file.
    :return: 2D numpy array
    """
    if ascii_skiprows in kwargs:
        skip_rows = kwargs[ascii_skiprows]
    else:
        skip_rows = 0

    if ascii_use_cols in kwargs:
        use_cols = kwargs[ascii_use_cols]
    else:
        use_cols = (0, 1)

    try:
        return np.loadtxt(file_name, skiprows=skip_rows, usecols=use_cols)
    except ValueError:
        raise ValueError(
            f"Numpy couldn't read dataset. Be sure to set {ascii_skiprows} and {ascii_use_cols} if necessary")


def transpose_if_necessary(data: np.ndarray) -> np.ndarray:
    """
    Transposes a numpy array if it is necessary to do so.
    :param data: Dataset that may need to be transposed
    :return: corrected array
    """
    if len(data.shape) == 1:
        return data

    if data.shape[0] > data.shape[1]:
        return data.T
    else:
        return data