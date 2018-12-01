import argparse
from runner.runner import run
from asciimatics.screen import Screen
from curses import error as curses_error
from support.printer import Printer

parser = argparse.ArgumentParser()
parser.add_argument("runfile",help="The runfile",type=str)

args = parser.parse_args()

try:
    Screen.wrapper(run,arguments=[args.runfile])
except curses_error:
    run(None,args.runfile)