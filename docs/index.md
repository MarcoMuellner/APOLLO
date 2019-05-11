# The APOLLO code
The APOLLO code is a fully automated pipeline to detect solar
like oscillations in light curves. It uses Bayesian model
comparison, by applying two different models using 
[DIAMONDS](https://github.com/EnricoCorsaro/DIAMONDS). 

This documentation should be purely taken as a technical
guide on how to use the pipeline. For further insight into
the inner workings of the code, see the associated 
publication (Muellner et al, 2019).

#Getting started
We recommend to read the associated publication before applying
the code to your use case (Muellner et al, 2019). It should not
be treated as a black box and an understanding of the inner 
workings should be gained before applying the code.

A quick start guide is available [here](usage/first_steps.md),
providing an installation guide as well as a quick example. This
should be your starting point. Your next step should be
the [in- and output page](usage/in_out_files.md), which gives
you an overview on what is needed to run APOLLO and gives a 
description of the configuration and result files. We also 
have a set of [examples](usage/showcases.md) included in the code.
These provide you with some show cases and go into detail into
the interface and behaviour of the code. For a full list of 
available configuration parameters, see the 
[parameters page](parameters.md).