#standard imports
from typing import Tuple,Dict
#scientific imports
import numpy as np
#project imports
from astropy.stats import sigma_clip

from fitter.fit_functions import scipyFit,gaussian
from plotter.plot_handler import plot_sigma_clipping,plot_interpolation,plot_noise_residual
from res.conf_file_str import internal_noise_value,analysis_obs_time_value,internal_mag_value,analysis_upper_mag_limit,internal_multiple_mag,internal_mag_noise
from data_handler.signal_features import compute_periodogram,noise,get_mag


def get_magnitude(data : np.ndarray,kwargs : Dict,mag_check : bool = True ) -> Dict:
    """
    Changes magnitude according to Panda et al. 2018 if noise is added
    :param kwargs: run config
    :return: run config with magnitude changed
    """
    f_data = compute_periodogram(data,kwargs)
    noise_val = noise(f_data)
    mag = get_mag(noise_val)

    upper_limit_mag = 14.5 if analysis_upper_mag_limit not in kwargs else kwargs[analysis_upper_mag_limit]
    np.savetxt("computed_magnitude.txt",np.array([mag]))

    if mag > upper_limit_mag and mag_check:
        raise ValueError(f"Magnitude for noise {kwargs[internal_noise_value]} too high! Computed mag: {'%.2f' % mag}, upper limit: {'%.2f' % upper_limit_mag}")

    kwargs[internal_mag_value] = mag

    return kwargs

def refine_data(data : np.ndarray, kwargs : Dict) -> Tuple[np.ndarray,Dict]:
    """
    Refines the dataset and returns it
    :param data: Dataset that needs refining
    :param kwargs: Run configuration
    :return: Good dataset
    """
    data = normalize_data(data)
    data = reduce_data_to_observation_time(data,kwargs)
    data,kwargs = add_noise(data,kwargs)
    data = remove_stray(data,kwargs)
    data = interpolate(data,kwargs)
    return data,kwargs

def get_total_gap(data : np.ndarray) -> float:
    """
    Computes the total gap in time units for a given dataset
    :param data: datset of the lightcurve
    :return: total gap in units of time
    """
    values,counts,most_common = get_diff_values_counts_most_common(data)

    values[values - most_common < 10**-5] = 0
    return float(np.sum(values*counts))

def compute_duty_cycle(data : np.ndarray) -> float:
    """
    Computes the duty cycle for a given lightcurve.
    :param data: dataset of the lightcurve
    :return: duty cycle in percent
    """
    x = data[0]
    total_length = x[-1] - x[0]

    total_gap = get_total_gap(data)

    return (total_length-total_gap)*100/total_length

def compute_observation_time(data : np.ndarray) -> float:
    """
    Computes the total observation time for a given dataset
    :param data: dataset of the lightcurve
    :return: total observation time
    """
    x = data[0]
    total_length = x[-1] - x[0]
    total_gap = get_total_gap(data)
    return total_length - total_gap

def reduce_data_to_observation_time(data : np.ndarray, kwargs : Dict) -> np.ndarray:
    """
    Reduces the observation to a given time by cutting in the edges
    :param data: dataset of the lightcurve
    :param time: target observation time
    :return: array with given length
    """
    if analysis_obs_time_value in kwargs.keys():
        time = kwargs[analysis_obs_time_value]
        null_obs_time = compute_observation_time(data)
        if time > null_obs_time or null_obs_time < 0:
            raise ValueError(f"Target observation time cannot be reached. Needs to be bigger zero and smaller than "
                             f"zero observation time. 0 time is {null_obs_time}, target obs time is {time}")

        x = data[0]
        y = data[1]
        obs_time = compute_observation_time(np.array((x, y)))
        fringe = 0
        _,_,most_common = get_diff_values_counts_most_common(data)
        while (obs_time > time):
            mask = np.logical_and(data[0] > data[0][int(len(data[0])/2)] - time/2 - fringe/2
                                  ,data[0]< data[0][int(len(data[0])/2)] + time/2 + fringe/2)
            y = data[1][mask]
            x = data[0][mask]
            obs_time = compute_observation_time(np.array((x, y)))
            fringe = obs_time - time

        return normalize_data(np.array((x,y)))
    else:
        return data


def reduce_data_to_duty_cycle(data : np.ndarray, target_duty_cycle : float) -> np.ndarray:
    """
    Adds gaps to the dataset to reach a given duty cycle
    :param data: dataset of the lightcurve
    :param target_duty_cycle: duty cycle that is needed to reach. Needs to be less then the starting duty cycle
    :return: data with given dutycycle
    """

    null_duty_cycle = compute_duty_cycle(data)
    if target_duty_cycle > null_duty_cycle or target_duty_cycle > 100 or target_duty_cycle < 0:
        raise ValueError(f"Target duty cycle can't be reached. It needs to be between 0 and a 100 and smaller than"
                         "the starting duty cycle. Starting duty cycle is {'.%2f'%null_duty_cycle}% "
                         "and target duty cycle is {'.%2f'%target_duty_cycle}%")

    x = data[0]
    y = data[1]
    duty_cycle =compute_duty_cycle(np.array((x,y)))
    fringe = 0
    while(duty_cycle > target_duty_cycle):
        target_indices = len(data[0])*((null_duty_cycle - target_duty_cycle)/100 + fringe)
        mask = np.logical_or(data[0] < data[0][int(len(data[0])/2 - target_indices/2)]
                             ,data[0] >  data[0][int(len(data[0])/2 + target_indices/2)])
        y = data[1][mask]
        x = data[0][mask]
        duty_cycle = compute_duty_cycle(np.array((x, y)))
        fringe = duty_cycle - target_duty_cycle

    return np.array((x,y))

def normalize_data(data:np.ndarray) -> np.ndarray:
    """
    Subtracts the zero point of the time array and removes nans and infs
    :param data: Dataset
    :return: zeroed in dataset
    """
    x = data[0]
    y = data[1]

    for i in [np.inf,-np.inf,np.nan]:
        if i in y:
            n = len(y[y==i])

        x = x[y != i]
        y = y[y != i]


    return np.array(((x - x[0]), y))

def get_diff_values_counts_most_common(data : np.ndarray) -> Tuple[np.ndarray,np.ndarray,float]:
    """
    Returns the difference values and counts for a given dataset in the temporal axis as well as the most common value
    :param data: Dataset of the lightcurve
    :return: Tuple of 2 arrays, consisting of values and counts as well as a float with the most common value
    """
    x = data[0]
    diff = x[1:] - x[:-1]
    (values, counts) = np.unique(diff, return_counts=True)
    most_common = values[np.argmax(counts)]
    return values,counts,most_common

def get_gaps(data:np.ndarray) -> Tuple[int,float]:
    """
    Finds gaps in a given dataset
    :param data: Dataset
    :return: Gap ids and most common difference between two values
    """
    x = data[0]
    #approximation of difference
    diff = np.round(x[1:] - x[0:-1],decimals=2)
    values, counts, most_common = get_diff_values_counts_most_common(data)

    gap_ids = np.where(diff > 3)
    if len(gap_ids[0]) == 0:
        gap_ids = None
    else:
        gap_ids = gap_ids[0][0]

    return gap_ids,most_common

def remove_stray(data:np.ndarray,kwargs : Dict) -> np.ndarray:
    """
    Removes stray values from the dataset (values bigger than 5 sigma of the distribution of datapoints)
    :param data: dataset
    :param kwargs: Run configuration
    :return: dataset with removed strays
    """

    clipped = sigma_clip(data[1],sigma=5,maxiters=10)
    plot_sigma_clipping(data,clipped.mask,kwargs)
    data = np.array([data[0][~clipped.mask],data[1][~clipped.mask]])
    return data

def get_line(x1,x2,y1,y2,most_common):
    """
    Creates a line between two points
    :param x1: x1 point
    :param x2: x2 point
    :param y1: y1 pint
    :param y2: y2 point
    :param most_common: most common value in dataset
    :return:
    """
    b = (y1 - y2)/(x1 -x2)
    a = y1 - b*x1

    delta_t = x2 -x1
    n = int(delta_t//most_common)
    x = np.linspace(x1+most_common,x2,n,endpoint=False)
    y = a+b*x
    return np.array((x,y))

def interpolate(data : np.ndarray,kwargs : Dict)->np.ndarray:
    """
    Interpolates the dataset within the gaps
    :param data: dataset
    :return: interpolated dataset
    """
    gap_arr_ids = []
    while True:
        gap,most_common = get_gaps(data)

        if gap is None or not gap.size:
            break

        line_data = get_line(data[0][gap],data[0][gap+1],data[1][gap],data[1][gap+1],most_common)
        x = np.hstack((data[0][:gap],line_data[0],data[0][gap+1:]))
        y = np.hstack((data[1][:gap], line_data[1], data[1][gap + 1:]))
        ids = np.arange(0,len(line_data[0])) + gap

        data = np.array((x,y))
        gap_arr_ids = gap_arr_ids + ids.tolist()

    plot_interpolation(data,gap_arr_ids,kwargs)

    return data


def add_noise(data : np.ndarray, kwargs : Dict) -> Tuple[np.ndarray,Dict]:
    """
    Adds noise to the signal configured within the conf dict
    :param data: Dataset
    :param kwargs: Run conf
    :return: Noisier signal
    """
    if internal_noise_value in kwargs.keys() or (internal_multiple_mag in kwargs.keys() and kwargs[internal_multiple_mag]):
        range_data = np.amax(data[1]) - np.amin(data[1])
        binsize = int(range_data * np.exp(-range_data / 9500000))  # empirically brought down to a reasonable value

        bins = np.linspace(np.amin(data[1]), np.amax(data[1]), binsize)
        hist = np.histogram(data[1], bins=bins, density=True)[0]

        mids = (bins[1:] + bins[:-1]) / 2
        cen = np.average(mids, weights=hist)
        wid = np.sqrt(np.average((mids - cen) ** 2, weights=hist))

        p0 = [0, cen, wid]
        bins = bins[:-1]

        popt, __ = scipyFit(bins, hist, gaussian, p0)

        (cen, wid) = (popt[1], popt[2])

        x = data[0]
        y = data[1]

        if internal_noise_value in kwargs.keys():
            noise = float(kwargs[internal_noise_value]) * (np.random.normal(cen,100,len(y)))
            plot_noise_residual(data,np.array((x,(y + noise))),kwargs)
            kwargs = get_magnitude(np.array((x,(y + noise))), kwargs)
        else:
            old_mag = kwargs[internal_mag_value]
            kwargs = get_magnitude(np.array((x, y)), kwargs, False)
            noise_val = 0
            noise = 0
            while old_mag - kwargs[internal_mag_value] > 0:
                noise_val +=0.1
                noise = noise_val * (np.random.normal(cen, 100, len(y)))
                kwargs = get_magnitude(np.array((x, (y+noise))), kwargs,False)

            kwargs[internal_mag_value] = old_mag
            kwargs[internal_mag_noise] = noise_val
            plot_noise_residual(data, np.array((x, (y + noise))), kwargs)

        return np.array((x,(y + noise))),kwargs
    else:
        return data,kwargs