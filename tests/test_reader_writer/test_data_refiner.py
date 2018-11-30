import os
import re
# scientific imports
import numpy as np
# project imports
from readerWriter.data_refiner import refine_data,set_time_from_zero,get_gaps,remove_stray,interpolate

try:
    pre_path = re.findall(r'.+\/LCA\/', os.getcwd())[0]
    test_file_dir = f"{pre_path}tests/testFiles/"
except IndexError:
    test_file_dir = f"tests/testFiles/"

x = np.linspace(0,100,5000)
y = np.sin(x)
arr = np.array((x,y))

def test_set_time_from_zero():
    arr[0] += 500
    assert np.abs(set_time_from_zero(arr)[0][0]) < 10**-7
    arr[0] -= 1000
    assert np.abs(set_time_from_zero(arr)[0][0]) < 10 ** -7
    arr[0] += 1000
    assert np.abs(set_time_from_zero(arr)[0][0]) < 10 ** -7

def test_get_gaps():
    gap = [i for i in range(3000,4001)]

    x_gap = np.delete(x,gap)
    y_gap = np.delete(y,gap)

    gap_ids, most_common = get_gaps(np.array((x_gap,y_gap)))
    assert 2999 in gap_ids
    assert np.abs(most_common - 100/5000) < 10**-5

    gap = [i for i in range(3000, 3002)]

    x_gap = np.delete(x, gap)
    y_gap = np.delete(y, gap)

    gap_ids, most_common = get_gaps(np.array((x_gap, y_gap)))
    assert 2999 in gap_ids
    assert np.abs(most_common - 100 / 5000) < 10 ** -5

    gap = []

    x_gap = np.delete(x, gap)
    y_gap = np.delete(y, gap)

    gap_ids, most_common = get_gaps(np.array((x_gap, y_gap)))
    assert None == gap_ids
    assert np.abs(most_common - 100 / 5000) < 10 ** -5

def test_remove_stray():
    y_noise = np.random.normal(5, 8, 5000)

    arr_noise = np.array((x,y_noise))
    data = remove_stray(arr_noise)

    assert np.abs(np.mean(data[1])) < 0.5

def test_interpolate():
    gap = [i for i in range(3000,4001)]

    mean_compare_x = np.mean(x[3000:4000])
    mean_compare_y = (y[4000] - y[3000])/2

    x_gap = np.delete(x,gap)
    y_gap = np.delete(y,gap)

    data = interpolate(np.array((x_gap,y_gap)))

    assert np.abs(np.mean(data[0][3000:4000]) - mean_compare_x) < 10**-7
    assert np.abs(np.mean(data[1][3000:4000]) - mean_compare_y) < 1


def test_refine_data():
    gap = [i for i in range(3000,4001)]

    y_noise =y+ np.random.normal(5, 8, 5000)

    mean_compare_x = np.mean(x[3000:4000])
    mean_compare_y = (y[4000] - y[3000]) / 2

    x_gap = np.delete(x,gap)
    y_gap = np.delete(y_noise,gap)

    data = refine_data(np.array((x_gap,y_gap)))
    assert np.abs(np.mean(data[1])) < 3
    assert np.abs(np.mean(data[0][3000:4000]) - mean_compare_x) < 10 ** -7
    assert np.abs(np.mean(data[1][3000:4000]) - mean_compare_y) < 10