#standard imports
from typing import Tuple,Union
#scientific imports
import numpy as np
from sympy.ntheory import factorint
#project imports

def get_time_step(data:np.ndarray) ->float:
    """
    Returns the most common time steps in the datapoints.
    :param data: Dataset of the lightcurve
    :return: Most common time diff
    """
    real_diff = data[0][1:len(data[0])] - data[0][0:len(data[0]) - 1]
    (values, counts) = np.unique(real_diff, return_counts=True)
    most_common = values[np.argmax(counts)]
    return most_common

def calculate_flicker_amplitude(data:np.ndarray) -> float:
    """
    Computes the flicker amplitude after Bastien et al. (2013)
    :param data: data consisting of the full lightcurve
    :return: flicker amplitude
    """
    flicker_time = get_flicker_time(data)
    t_step = get_time_step(data)
    elements = data[0].shape

    box_size = np.round(flicker_time/t_step)
    bin_count = int(elements / box_size)
    points_left = elements - box_size * bin_count

    index_shift,cols = get_index_shift(points_left)
    mean_array, subtract_array_amplitude = get_flicker_arrays(data, elements, cols, index_shift, box_size, flicker_time)
    mean_amp = np.mean(mean_array)
    subtract_array_amplitude = np.unique(subtract_array_amplitude)

    flic_amplitude = 0

    for i in range(0, len(subtract_array_amplitude)):
        flic_amplitude += (subtract_array_amplitude[i] - mean_amp) ** 2

    denominator = float(len(subtract_array_amplitude))
    amp_flic = np.sqrt(flic_amplitude / denominator)
    return amp_flic

def flicker_amplitude_to_frequency(flicker_amplitude : float) -> float:
    """
    Converts the flicker amplitude to the first filter frequency according to Kallinger et al. (2016)
    :param flicker_amplitude: Flicker amplitude calculated according to Bastien et. al (2013)
    :return: First filter frequency
    """
    return 10 ** (5.187) / (flicker_amplitude ** (1.560))


def get_flicker_time(data : np.ndarray) -> float:
    """
    Returns the flicker time. 2.5 hours for SC, 5 days for LC data
    :param data: data consisting of the full lightcurve
    :return: flicker time
    """
    t_step = get_time_step(data)
    t_step *= 24*60

    if t_step < 10:
        return 2.5/(60*24) #2.5 hours time for SC data
    else:
        return 5/24 #5 days for LC data

def get_index_shift(points_left : int) -> Tuple[int,int]:
    """
    Depending on how many points are left in the array from the binsize, this method will return the according
    index_shift for the data as well as the amount of cols whereover these have to be iterated
    :param points_left: Restpoints after binning
    :return: index_shift,cols
    """
    index_shift = 0
    cols = 1

    if points_left > 1:

        factors=factorint(points_left, multiple=True)

        if len(factors) > 1:
            index_shift = factors[0]**factors[1]
        else:
            index_shift = factors[0]

        cols = int(points_left / index_shift + 1)
    elif points_left == 1:
        cols = 2
        index_shift = 1

    return index_shift,cols


def get_flicker_arrays(data : np.ndarray, elements : Union[int,Tuple[int,]], cols : int, index_shift : int, box_size : int
                       , filter_time :float) -> Tuple[float,np.ndarray]:
    """
    This method, depending on the indexshift, boxsize and filtertime creates the appropiate arrays, for which the
    flicker amplitude is calculated. It calculates the mean of every box for the boxsize
    """
    if isinstance(elements,tuple) and len(elements) > 1:
        raise ValueError("Elements is not allowed to be a tuple longer than 1!")
    else:
        elements = elements[0]

    bin_count = int(elements / box_size)
    points_left = elements - box_size * bin_count

    array_mean = np.zeros(cols)

    for k in range(0,cols):
        array_rebin = np.zeros(int(elements-points_left))
        n_points_bin_array = np.zeros(int(elements-points_left))

        i = k * index_shift

        for j in range(0,bin_count):
            mean_bin = 0.0
            timetime_referenceeference = i
            count = 1

            while i < (int(elements)-1) and (data[0][i] - data[0][timetime_referenceeference])/(3600*24) < filter_time:
                mean_bin +=data[1][i]
                if data[1][i] != 0:
                    count +=1
                i+=1

            mean_bin += data[1][i]
            if data[1][i] != 0:
                count +=1

            if count > 1:
                mean_bin /= count-1

            array_rebin[timetime_referenceeference - k * index_shift:(i - 1) - k * index_shift] = mean_bin
            n_points_bin_array[timetime_referenceeference - k * index_shift:(i - 1) - k * index_shift] = count

        subtract_array_amplitude = data[1][k * index_shift:k * index_shift + len(array_rebin)] - array_rebin
        subtract_array_amplitude = subtract_array_amplitude[n_points_bin_array >= box_size / 2]
        array_mean[k] = np.mean(subtract_array_amplitude)

    return array_mean,subtract_array_amplitude