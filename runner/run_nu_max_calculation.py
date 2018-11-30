# library imports
import os
import re
# scientific imports
import numpy as np
# project imports
from readerWriter.file_reader import load_file
from readerWriter.data_refiner import refine_data
from readerWriter.signal_features import compute_periodogram,nyqFreq
from evaluators.compute_flicker import calculate_flicker_amplitude,flicker_amplitude_to_frequency
from evaluators.compute_nu_max import compute_nu_max
from evaluators.compute_priors import priors
from background.fileModels.bg_file_creator import create_files
from background.backgroundProcess import BackgroundProcess
from res.conf_file_str import ascii_use_cols,ascii_skiprows,plot_show,general_kic,fits_hdulist_column

pre_path = re.findall(r'.+\/LCA\/', os.getcwd())[0]
test_file_dir = f"{pre_path}tests/testFiles/"

file = f"{test_file_dir}kplr008962923_2846_COR_filt_inp.fits"

kwargs = {
    ascii_skiprows: 1,
    ascii_use_cols: None,
    plot_show:False,
    general_kic: 123456,
    fits_hdulist_column:0
}

data = load_file(file,kwargs)
data = refine_data(data,kwargs)
sigma_ampl = calculate_flicker_amplitude(data)
f_ampl = flicker_amplitude_to_frequency(sigma_ampl)
nu_max = compute_nu_max(data,f_ampl,kwargs)
f_data = compute_periodogram(data)
create_files(data,nyqFreq(data),priors(nu_max,data),kwargs)

proc = BackgroundProcess(str(kwargs[general_kic]))
proc.run()