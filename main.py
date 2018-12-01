import argparse
from runner.runner import run
from asciimatics.screen import Screen

parser = argparse.ArgumentParser()
parser.add_argument("runfile",help="The runfile",type=str)

args = parser.parse_args()

Screen.wrapper(run,arguments=[args.runfile])