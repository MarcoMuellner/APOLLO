# Input and output of APOLLO

Generally, to use APOLLO you need a couple of things:

- The light curves of the stars you want to analyze
- Magnitude and temperature for these stars
- A config file in the ```json``` format (For more info on this file format see [here](https://en.wikipedia.org/wiki/JSON))
- A sample file

Magnitude and temperature for the publication from the Kepler input 
catalogue, and don't need to be particularly accurate for APOLLO to work.
Be advised though, that the scaling relations for mass and radius both 
use the temperature.
 
# The config file
This file configures your options for a given run. It is structured in 
the ```json``` format, which is easily readable, but also very easy
to use in python, only consisting of key-value pairs. For an easy example,
lets look at the ```mini_example.json``` file in the demo folder:
```
{
  "General": {
    "Path for results": "demo_results/mini_example/",
  },
  "Analysis": {
    "Paths to lightcurves": "demo/data/",
    "Prefix of folder": "DEMO"
  },
  "List of IDs": "demo/sample_files/targets_single.txt"
}

```
This is the minimal set of settings one needs to set for APOLLO to run.
The ```General``` section consists only of:

- ```Path for results```: The path where the results are saved.

The ```Analysis``` section consists of:

- ```Paths to lightcurves```: Paths to the light curve files. 
- ```Prefix of folder```: APOLLO prefixes this value to all result folders
of individual stars. 

Last but not least, you need the ```List of IDs``` parameter. This is the 
path to the sample file.

This file has many more parameters that you can activate. Check the 
[example](examples.md) page or the [parameters](../parameters.md) file.

## Other parameters, that are usually set
Usually, a list of other parameters are also always set in the config file. Below
is a list of those, with their according section:

- ```General/Number of cores used```: Defines how many cores should be 
taken up by APOLLO. If this value exceeds the number of physical cores on a system,
the maximum amount available is used.
- ```General/Check Bayes factor after run```: If this is is set to ```true```, it
will check the Bayes factor directly after running both models. If the 
resulting Bayes factor is not significant, it will rerun both models up to 
three times, with every iteration being checked. This might be useful for
stars that show a low amplitude/high noise. Default is ```false```.
- ```General/Force run```: If this is is set to ```true```, it will automatically
delete the previous run result and rerun the star. If not, and a ```results.json```
file exists, it will leave the result as is. Default is ```false```.
- ```Plot/Save plots```: It is possible to let APOLLO generate a set of plots
throughout its process. If this flag is set to ```true```, APOLLO will save
these plots in the results folder of the star. Default is ```false```.

The default behaviour is always active if the parameter is not set in the config file.
So a probably more common run file would look like this:
```
{
  "General": {
    "Path for results": "demo_results/mini_example/",
    "Number of cores used": 32,
    "Check Bayes factor after run": true,
    "Force run": false
  },
  "Analysis": {
    "Paths to lightcurves": "demo/data/",
    "Prefix of folder": "DEMO"
  },
  "Plot": {
    "Save plots": true
  },
  "List of IDs": "demo/sample_files/targets_single.txt"
}
```

# The sample file
This file represents the data set you want to run through the pipeline.
At minimum, you need three parameters for each star:

- _ID_: A unique identifier of the star, some numerical value. This string
can be anywhere in the filename. So for APOLLO it makes no difference if you 
call your light curve file _kplr_xxxxxx_data.dat_ or _xxxxxx.txt_.
- _T_eff_: The effective temperature of the star
- _mag_: The magnitude of the star.

All three values must be split by a single white space and must have
header description at the top. For example, the ```targets_single.txt``` file:
```
id T_eff mag
4057076 4708 11.844
```

You can also add literature values for delta nu and nu max as well as their
errors. For example the ```targets_single_lit.txt``` file:
````
id T_eff delta_nu delta_nu_err nu_max nu_max_err  mag
4057076 4708 4.58 0.09 42.01 0.95 11.844
````
These values will then be added to the result file for more convinient
analysis of the result.
# Result files
The output of APOLLO consists of the following structure:
```
-result_path/
    -PREFIX_ID/
        -images/
        conf.json
        lc.npy
        psd.npy
        results.json
    -PREFIX_ID/
        -images/
        conf.json
        lc.npy
        psd.npy
        results.json
    .
    .
    .
```
So the result for a given star consists of ```images``` (given you set 
save plots parameter), the ```conf.json``` file (a simple copy of the 
config file, including the stellar input parameters), ```lc.npy``` and
```psd.npy``` the light curve (already reduced by the pipeline) and psd of the star in a 
[binary format](https://github.com/numpy/numpy/blob/067cb067cb17a20422e51da908920a4fbb3ab851/doc/neps/nep-0001-npy-format.rst)
(as the raw size of these files can add up quickly) and the ```results.json```
file.

You have a couple of categories in your result. These are:

- ```Priors Oscillation model```: The upper and lower values of the prior
distributions for each of the 10 free parameters of the oscillation model. The up/low value for f_max
are the 1-sigma values of the mean value.
- ```Priors Noise model```: The upper and lower values of the prior
distributions for each of the 7 free parameters of the noise model.
- ```Determined params```: The centroid values for the prior distributions
- ```Oscillation model result```: The resulting parameters from the fit
for the oscillation model using DIAMONDS, including their uncertainties.
- ```Noise model result```: The resulting parameters from the fit for the noise
model, including their uncertainties.

Below those sections, you find some singular results. These are:

- ```Evidence Oscillation model```: The Bayesian evidence for the 
oscillation model (natural logarithm)
- ```Evidence Noise model```: The Bayesian evidence for the noise model (natural logarithm)
- ```Bayes factor```: The resulting Bayes factor from the two evidences (natural logarithm).
If this value exceeds ln(5), the resulting fit strongly prefers the 
oscillation model over the noise model.
- ```Nu max guess```: The _guess_ of nu max with FliPer.
- ```Delta nu```: The large frequency separation, computed using the 
auto correlation of the oscillation region.
- ```log(g)```: Surface gravity of the star. 
- ```Radius```: Radius of the star. Computed using Bellinger (2018)
- ```Mass```: Mass of the star. Computed using Bellinger (2018)
- ```nu_max_gauss```: Legacy, will be removed
- ```Run worked flag```: A flag if the result was successfully compiled
- ```{key}: Number of runs```: How many iterations were needed for DIAMONDS
until a successful fit was done.
- ```NSMC configuring parameters```: The configuring parameters for the nested
sampling algorithm, used for DIAMONDS.
- ```List of frequencies```: Legacy, will be removed in future versions
- ```FliPer frequency```: Same value as ```Nu max guess```
- ```Runtime```: Runtime for the star in seconds

# Errors
Sometimes it can happen, that a fit couldn't be complete, something broke
or some setting was wrong. If this is the case, in the folder structure of 
the results, you will find ```errors.txt``` files, that contain the error
that happened. This is simply the exception thrown by Python. Please read 
the content of this file carefully and if a setting was wrong, adjust your 
config file. If it was an internal error by the pipeline, open an issue on 
the github page.