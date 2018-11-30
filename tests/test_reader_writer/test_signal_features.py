import os
import re
# scientific imports
import numpy as np
# project imports
from data_handler.signal_features import compute_periodogram,get_time_step,nyqFreq,noise

x = np.linspace(0,100,5000)
y = np.sin(x)

def test_compute_periodogram():
    f_space = compute_periodogram(np.array((x,y)))
    assert np.abs(f_space[0][np.where(f_space[1] == np.max(f_space[1]))] - np.pi/2)[0] < 0.3

def test_get_time_step():
    most_common = get_time_step(np.array((x,y)))
    assert np.abs(most_common - 100/5000) < 10**-5

def test_nyq_freq():
    nyq = nyqFreq(np.array((x,y)))
    assert np.abs(nyq - 10 ** 6 /(2*(100/5000)*24*3600)) < 0.1

def test_noise():
    y_noise = np.random.normal(5, 3, 5000)
    n = noise(np.array((x,y_noise)))
    assert np.abs(n - 5) < 2.5
