import argparse
from runner.runner import run
from asciimatics.screen import Screen
from curses import error as curses_error
import json
from res.conf_file_str import general_sequential_run,cat_general
import warnings


parser = argparse.ArgumentParser()
parser.add_argument("runfile",help="The runfile",type=str)

args = parser.parse_args()
with warnings.catch_warnings():
    warnings.simplefilter("ignore")

    conf_file_list = args.runfile.split(",")

    with open(conf_file_list[0], 'r') as f:
        kwargs = json.load(f)

    try:
        if general_sequential_run in kwargs[cat_general].keys() and kwargs[cat_general][general_sequential_run]:
            run(None,args.runfile)
        else:
            Screen.wrapper(run,arguments=[args.runfile])
    except curses_error:
        run(None,args.runfile)