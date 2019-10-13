# APOLLO

[Logo](https://raw.githubusercontent.com/MarcoMuellner/APOLLO/master/logo/logo.png?token=ADJ6HMEUZ6ZU6UAY5GT5YSK5VS3Z6)
_**APOLLO**_ (bAyesian Pipeline for sOLar Like Oscillators) is a fully integrated, automated pipeline that can detect solar 
like oscillations in a given star using model Bayesian model comparison. For a full description of the pipeline,
check the paper [Muellner et al. (2019)](). For the documentation check either [here]() or run it locally
using```mkdocs serve```.

# Prerequisits
APOLLO is tested and used under Linux as well as under MacOS, which are the operating systems supported by APOLLO. It 
is also assumed that Python3.6, pip, git, cmake and the gcc chain are installed on your system. If they are not installed,
please do so using your favourite packet manager, for example **brew** on MacOS or **apt** on Debian systems.

# Installation
In the first step, clone the repository do your computer using
```
git clone https://github.com/MarcoMuellner/APOLLO
cd APOLLO
```
The project also makes use of submodules. These need to be initialized and updated
```
git submodule init
git submodule update
```

It is recommended to use a virtual environment for all python projects. Create and activate one using
```
python3.6 -m venv venv/
source venv/bin/activate
```
In the next step, simply install everything using
```
python setup.py install
```
This will install all necessary python packages, build [DIAMONDS]() and [Background]() and sets the ```apollo``` file
as executable.

And you are done.

# Demo
_**APOLLO**_ includes a couple of little demo files, to give you a feel on how the pipeline runs. To run the minimal example simply call
```
./apollo demo/1_mini_example.json
```
The results files are than available under ```demo_results/1_mini_example/``` and consists of the light curve, the 
power spectral density, a config file and a result file.

Further examples are shown in the documentation.

# Questions? Problems?
If you have any problems installing or using our code, don't hesitate to open an issue here on the github. We will
try to help you as soon as possible.

# Citation
If you use our pipeline for scientific purposes, please cite Muellner et al. (2019). 
