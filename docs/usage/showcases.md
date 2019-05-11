#Concerning the examples
APOLLO ships with a set of small examples including a data set of 4 red giants
from our calibration sample. These light curves were directly downloaded from the 
[KASOC website](http://kasoc.phys.au.dk/).

Magnitudes and temperatures for these stars were extracted from the Kepler
input catalogue.

While this set of examples should cover the basics on how to use the
pipeline, it doesn't show everything. Therefore, please also refer
to [parameters page](../parameters.md) and please read [input and output page](in_out_files.md)
before this.

#Example 1: Mini example
This example was already covered in the [first steps](first_steps.md). It runs the
pipeline on a single star and has the following config file:
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
and this sample file (```demo/sample_files/targets_single.txt```):
````
id T_eff mag
4057076 4708 11.844
```` 
It should produce the following output
```
- demo_results/
    -mini_example/
        -DEMO_4057076
            -result files
```
and produces the values of the resulting fit.

The interface for APOLLO usually looks like this:

![](../images/APOLLO_interface.png)

and is split into three parts. At the top you can find the status 
of the stars currently running. 

![](../images/Status_star.png)

At the furthest left you have two numbers: The first one is a simple _out of_,
the number on the right shows the number of currently running stars. Next to it,
you have the ID of the star, as defined in the sample file.Furthest to the 
right shows the log messages of the star, in this case the number of iterations in
DIAMONDS.

At the bottom of the interface you find the statistics for the whole run.

![](../images/Statistics.png)

In green, it gives you the number of stars from the sample that are already
done, including the last couple of IDs in the brackets. Below that it shows
the currently running stars. On the bottom, in white, it how many stars are worked 
of from the total, as well as estimation of time that the run will still need.
This is computed by averaging over the run times from the result times the number of 
stars left, divided by the number of cores used. This is really a rough estimation
and will not be exact.
