import argparse
from runner.runner import kwarg_list
from res.conf_file_str import general_kic, internal_mag_value
import warnings
from data_handler.file_reader import load_file
from data_handler.data_refiner import refine_data
from data_handler.signal_features import compute_periodogram
from evaluators.compute_priors import noise

parser = argparse.ArgumentParser()
parser.add_argument("runfile", help="The runfile", type=str)

args = parser.parse_args()

conf_list, nr_of_cores = kwarg_list(args.runfile)

res_list = []

with warnings.catch_warnings():
    warnings.simplefilter("ignore")

    for i in conf_list:
        print(f"ID: {i[general_kic]}")
        try:
            data = load_file(i)
        except:
            continue
        data = refine_data(data, i)
        data = compute_periodogram(data)
        n = noise(data)
        print(i[internal_mag_value],n)
