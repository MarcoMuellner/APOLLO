# library imports
import os
import re
# scientific imports
# project imports
from readerWriter.file_reader import load_file
from readerWriter.data_refiner import refine_data
from evaluators.compute_flicker import calculate_flicker_amplitude,flicker_amplitude_to_frequency
from evaluators.compute_nu_max import compute_nu_max
from res.conf_file_str import ascii_use_cols,ascii_skiprows,plot_show,general_kic

pre_path = re.findall(r'.+\/LCA\/', os.getcwd())[0]
test_file_dir = f"{pre_path}tests/testFiles/"

file = f"{test_file_dir}Lightcurve.txt"

kwargs = {
    ascii_skiprows: 1,
    ascii_use_cols: None,
    plot_show:True,
    general_kic: 123456
}

data = load_file(file,kwargs)
data = refine_data(data,kwargs)
sigma_ampl = calculate_flicker_amplitude(data)
f_ampl = flicker_amplitude_to_frequency(sigma_ampl)
nu_max = compute_nu_max(data,f_ampl,kwargs)

print(nu_max)
