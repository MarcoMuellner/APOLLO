import argparse
from runner.runner import run

parser = argparse.ArgumentParser()
parser.add_argument("runfile",help="The runfile",type=str)

args = parser.parse_args()

run(args.runfile)