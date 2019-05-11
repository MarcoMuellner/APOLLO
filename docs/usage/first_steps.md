# Introduction
Welcome to APOLLO, named after the good old 
greek god of light and carrier of the sun. APOLLO stands for automated 
b**A**yesian **P**ipeline for s**OL**ar **L**ike **O**scillators, and is 
a fully integrated, automated and easy to use pipeline to detect solar like
oscillations in stars using model comparison.

On this page, the basic installation instructions are noted, as well as
a simple starting example.
# Prerequisites
The code is tested and used both under **Linux** and **MacOS** systems, which are
the operating systems supported by APOLLO. We never tried to run it on 
any Windows operating system, but in principle there is no reason
it should not work. If you manage to get it running, please contact
us, and we will provide an installation guide for Windows here as well.

To install APOLLO you need **Python3.6**, **pip**, **git**, **cmake** as 
well as the **gcc toolchain** (or alternatively **Clang**). Those things are generally easily obtainable
if you have a packet manager like _brew_ or _apt_ installed. If you
don't have a packet manager, simply search for these packages and install
them as recommended by their provider.

# Installation
Installing APOLLO is very easy. Start off by cloning the project from github:
```
git clone https://github.com/MarcoMuellner/APOLLO
cd APOLLO
```
To not create a conflict with any other Python project you might use,
it is highly recommended to create a virtual environment for APOLLO. 
Simply create and activate one
```
python3.6 -m venv venv/
source venv/bin/activate
```
The second line needs to be recalled every time you open a new terminal 
session from the path APOLLO is installed. 

APOLLO also uses git submodules. These need to be initialized and pulled
using
```
git submodule init
git submodule update
```
After this is done, simply install it using 
```
python setup.py install
```
which will install all necessary python packages, and build the DIAMONDS 
and Background code.
#Minimal example
APOLLO ships with a set of examples, to show you how it works, all of which
are explained in [examples page](showcases.md). If you just to quickly try
it, you can simply run the minimal example. This is done using
```
./apollo demo/1_mini_example.json
```
which runs the pipeline for [KIC 4057076](http://simbad.u-strasbg.fr/simbad/sim-basic?Ident=KIC+4057076&submit=SIMBAD+search#lab_basic),
a star from our Calibration sample. After the code shows done, you can
chancel the run using ```CTRL+c``` to end the run. The pipeline will then
have created a result directoy in ```demo_results/mini_example/```, consisting
of files for the light curve, power spectral density, config and result.

#What's next?
[The in&output page](in_out_files.md) describes some of the various input parameters 
that are possible using APOLLO. It will also show you what kind of output you can expect from APOLLO.
If you are a bit more interested in some hands on examples, check the [examples page](showcases.md)