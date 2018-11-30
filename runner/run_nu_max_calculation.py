# library imports
import os
import re
# scientific imports
# project imports
from readerWriter.file_reader import load_file
from readerWriter.data_refiner import refine_data
from readerWriter.signal_features import compute_periodogram, nyqFreq
from evaluators.compute_flicker import calculate_flicker_amplitude, flicker_amplitude_to_frequency
from evaluators.compute_nu_max import compute_nu_max
from evaluators.compute_priors import priors
from background.fileModels.bg_file_creator import create_files
from background.backgroundProcess import BackgroundProcess
from readerWriter.write_results import save_results
from res.conf_file_str import ascii_use_cols, ascii_skiprows, plot_show, general_kic, fits_hdulist_column, \
    general_background_result_path, general_binary_path, general_background_data_path

pre_path = re.findall(r'.+\/LCA\/', os.getcwd())[0]
test_file_dir = f"{pre_path}tests/testFiles/"

file = f"{test_file_dir}YS_224319473.txt"

kwargs = {
    ascii_skiprows: 1,
    ascii_use_cols: (0, 10),
    plot_show: False,
    general_kic: "224319473",
    fits_hdulist_column: 0,
    general_background_result_path: "/Users/marco/Documents/Dev/Background/results/",
    general_background_data_path: "/Users/marco/Documents/Dev/Background/data/",
    general_binary_path: "/Users/marco/Documents/Dev/Background/build/",

}

data = load_file(file, kwargs)
data = refine_data(data, kwargs)
sigma_ampl = calculate_flicker_amplitude(data)
f_ampl = flicker_amplitude_to_frequency(sigma_ampl)
nu_max = compute_nu_max(data, f_ampl, kwargs)
f_data = compute_periodogram(data)
create_files(data, nyqFreq(data), priors(nu_max, data), kwargs)

proc = BackgroundProcess(kwargs)
proc.run()

save_results(priors(nu_max, data),data, kwargs)
