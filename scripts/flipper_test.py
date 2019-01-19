import numpy as np
import matplotlib.pyplot as pl

file = "/Users/marco/Documents/Dev/LCA/endurance_results/n_30_40/APO_7273426/run_1/noise_0.3_7273426/psd.txt"

data = np.loadtxt(file)


mean = np.mean(data[1])
noise = 10.256

F_p = mean/noise

print(F_p)

log_g_star = 2.6
T_eff = 4713

T_sun = 5778

T = T_eff/T_sun

log_g_sun = 4.44

g = (10**log_g_star)/(10**log_g_sun)

nu_max = g*np.sqrt(T)

print(nu_max)

print(nu_max * 3100)