#standard imports
from typing import Tuple,List,Dict
#scientific imports
import numpy as np
#project imports
from fitter.fit_functions import scipyFit,gaussian
from plotter.plot_handler import plot_sigma_clipping,plot_interpolation

def refine_data(data : np.ndarray, kwargs : Dict) -> np.ndarray:
    """
    Refines the dataset and returns it
    :param data: Dataset that needs refining
    :param kwargs: Run configuration
    :return: Good dataset
    """
    data = set_time_from_zero(data)
    data = remove_stray(data,kwargs)
    data = interpolate(data,kwargs)
    return data


def set_time_from_zero(data:np.ndarray) -> np.ndarray:
    """
    Subtracts the zero point of the time array
    :param data: Dataset
    :return: zeroed in dataset
    """
    return np.array(((data[0] - data[0][0]), data[1]))

def get_gaps(data:np.ndarray) -> Tuple[List[int],float]:
    """
    Finds gaps in a given dataset
    :param data: Dataset
    :return: Gap ids and most common difference between two values
    """
    x = data[0]
    #approximation of difference
    diff = np.round(x[1:len(x)] - x[0:len(x)-1],decimals=2)
    #real difference
    real_diff = x[1:len(x)] - x[0:len(x) - 1]

    (values,counts) = np.unique(real_diff,return_counts=True)
    most_common = values[np.argmax(counts)]

    gap_ids = np.where(diff !=  np.round(most_common,decimals=2))
    if len(gap_ids[0]) == 0:
        gap_ids = None
    else:
        gap_ids = gap_ids[0]

    return gap_ids, most_common

def remove_stray(data:np.ndarray,kwargs : Dict) -> np.ndarray:
    """
    Removes stray values from the dataset (values bigger than 5 sigma of the distribution of datapoints)
    :param data: dataset
    :param kwargs: Run configuration
    :return: dataset with removed strays
    """
    binsize = int((np.amax(data[1]) - np.amin(data[1]))/10)

    bins = np.linspace(np.amin(data[1]), np.amax(data[1]), binsize)
    hist = np.histogram(data[1], bins=bins, density=True)[0]

    mids = (bins[1:] + bins[:-1]) / 2
    cen = np.average(mids, weights=hist)
    wid = np.sqrt(np.average((mids - cen) ** 2, weights=hist))

    p0 = [0, cen, wid]
    bins = bins[:-1]

    popt, __ = scipyFit(bins, hist, gaussian, p0)

    (cen, wid) = (popt[1], popt[2])

    list_data = []
    for i in [0,1]:
        list_data.append(data[i][np.logical_and(data[1] > cen - 4 * wid, data[1] < cen + 4 * wid)])

    data = np.array(list_data)

    data[1] -=cen

    plot_sigma_clipping(data,bins,hist,popt,kwargs)

    return data

def interpolate(data : np.ndarray,kwargs : Dict)->np.ndarray:
    """
    Interpolates the dataset within the gaps
    :param data: dataset
    :return: interpolated dataset
    """

    gap_ids,most_common = get_gaps(data)

    if gap_ids is None or not gap_ids.size:
        return data


    ids_interpolated = []

    incrementer = 0

    gap_arr_ids = []

    for i in gap_ids:
        #ident moves the ID after each
        ident = i+incrementer

        count = int(np.round((data[0][ident + 1] - data[0][ident]) / most_common))

        delta_y = (data[1][ident + 1] - data[1][ident]) / count
        lister = [(0, data[0], most_common), (1, data[1], delta_y)]
        data = []

        #inserts new block of data into the dataset for x and y
        for (id,raw,adder) in lister:
            insert = np.linspace(raw[ident]+adder,raw[ident+1]-adder,num=count-1)
            data.append(np.insert(raw, ident + 1, insert))
            added_arr = np.searchsorted(data[-1],insert).tolist()
            for i in added_arr:
                if i not in gap_arr_ids and i != 0:
                    gap_arr_ids.append(i-1)

        data = np.array((data[0], data[1]))
        incrementer += count - 1

    plot_interpolation(data,gap_arr_ids,kwargs)

    return data
