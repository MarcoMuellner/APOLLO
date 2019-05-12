# The input parameters
The subsections below define the category name for each setting and need to put 
below them. The miscellaneous section shows all settings that don't belong to a category.

For each setting you can find its **name** and **type**, as well as a short documentation
what each parameter does. A parameter will also contain a **default** section if it not
mandatory.
## General
- **Name** : ```Path for results```
    - **Type** : _string_
    - **doc** : The root of the APOLLO result path. This can be either relative or absolute
    from the current working directory you are running from. If this path does not exist, 
    it will be created.
- **Name** : ```Number of cores used```
    - **Type** : _integer_
    - **doc** : The numbers of processes spawned by APOLLO. Each process represents the
    run of one star or run. The allocation happens dynamically, meaning, if a run has
    finished, this process is automatically assigned another run.
- **Name** : ```Check Bayes factor after run```
    - **Type** : _boolean_ (true/false)
    - **doc** : Defines if APOLLO checks the Bayes factor _O_, meaning the ratio of the two
     evidences from the oscillation model and noise model. If this Bayes factor does not
     exceed strong significance (_O_ >= 5), APOLLO will refit both models. This is
     done up to three times. This setting might be useful for short observation lengths 
     or noisy stars.
- **Name** : ```Activate PCB```
    - **Type** : _boolean_ (true/false)
    - **doc** : DIAMONDS uses principal component analysis, to increase the speed of a fit.
    This setting allows you to enable/disable this feature.
    - **default** : true
- **Name** : ```Run DIAMONDS```
    - **Type** : _boolean_ (true/false)
    - **doc** : This setting enables/disables the run of DIAMONDS. If this is set to false,
    a DIAMONDS result must already exist. In principle, you shouldn't touch this setting,
    except if you change something in the code.
    - **default** : true`
- **Name** : ```Binary path```
    - **Type** : _string_
    - **doc** : Using this setting, you can point APOLLO to a different installation of
    DIAMONDS. If you set this, you also need to set ```Background result path``` and
    ```Background data path```. It is recommended, to use the [fork of the Background code used
    in APOLLO](https://github.com/MarcoMuellner/Background), if you make any adaptations, as we 
    adapted the Background code to suit APOLLO. Path can be absolute, or relative to working
    directory.
    - **default** : Background/build/background
- **Name** : ```Sequential run```
    - **Type** : _boolean_ (true/false)
    - **doc** : If this is set to true, the code will run each star sequentially, and won't
    open the default interface, but rather print to stdout. This might be useful in 
    environments where asciimatics (used to draw the interface) is not available. It will also
    not run stars in parallel, but rather sequentially.
    - **default** : false
- **Name** : ```Background data path```
    - **Type** : _string_
    - **doc** : This setting defines the data path of the Background code (i.e. where 
    DIAMONDS expect the data files to be). If changed, adapt ```Binary path``` and 
    ```Background result path``` as well. Path can be absolute, or relative to working
    directory.
    - **default** : Background/data/
- **Name** : ```Background result path```
    - **Type** : _string_
    - **doc** : Here the result path of the Background code (i.e. where DIAMONDS stores
    its results) is defined. If changed, adapt ```Binary path``` and 
    ```Background data path``` as well. Path can be absolute, or relative to working
    directory.
    - **default** : Background/results/
## Analysis
- **Name** : ```Paths to lightcurves``` 
    - **Type** : _string_
    - **doc** : Path to the stored light curves on your computer, i.e. the path where APOLLO 
    looks for the ids in the sample file. The id can be wherever in the file name, it only has
    to be one continuing string. Path can be absolute, or relative to working directory.
- **Name** : ```Prefix of folder``` 
    - **Type** : _string_
    - **doc** : String prefixed to id in result path. For example, the result for the id 123456 and
    the prefix **PRE** would look like this: ```PRE_123456```.
- **Name** : ```Number of repeats``` 
    - **Type** : _integer_
    - **doc** : The number you define here, is the number of repeats APOLLO will perform for one star.
    If this is set, the folder structure will change, giving each run a single folder.
    - **default** : none
- **Name** : ```Target observation time``` 
    - **Type** : _float_
    - **doc** : If this setting is applied, APOLLO will restrict the observation time for the star. 
    For example, if the baseline of a light curve is 1400 days and you set this value to 300, it 
    will use only the first 300 days of observation.
    - **default** : none
- **Name** : ```Nu max guess``` 
    - **Type** : _float_
    - **doc** : This setting allows you to set a global guess for nu max for the set of stars in the 
    sample file. This might be useful, if you want to test various guesses for a given star. 
    - **default** : none
## Plot
- **Name** : ```Show plots``` 
    - **Type** : _boolean_ (true/false)
    - **doc** : Setting this value to true, will interactively show plots and continue the run 
    after you closed the plot. If you run multiple stars in parallel, multiple plots may appear. It 
    is advisable to also set ```Sequential run``` to true if you want to use this setting
    - **default** : false
- **Name** : ```Save plots``` 
    - **Type** : _boolean_
    - **doc** : This value allows you to save plots from APOLLO if so needed. All plots will be in the
    png format, and saved under images in the result path for a run.
    - **default** : false
## File
A short note concerning FITS files: While it is possible to use FITS files with APOLLO,
it is highly recommandable to simply use a two column ascii file. With this said, if you want to
read fits files, use the settings below. Also, APOLLO automatically detects if the correct file is a
fits file or ascii file through the ending: If a file ends with ```.fits``` it will use the corresponding
functions in the code for fits files. 

**IMPORTANT**: Make sure that for each id there is only one responding file in a given directory. If there
are multiple files with the same id, an error will be raised!
 
- **Name** : ```Data folumn for hdulist``` 
    - **Type** : _integer_
    - **doc** : This value defines the _column_ in the hdulist where the data is stored. This value
    is zero based, i.e. the first column is represented with 0. You also need to set the parameters
    ```Flux column``` and  ```Time column```.
    - **default** : none
- **Name** : ```Time column``` 
    - **Type** : _string_
    - **doc** : With this value, you define the column that represents the temporal axis for the light curve.
    You also need to set ```Flux column``` and ```Data folumn for hdulist```
    - **default** : none
- **Name** : ```Flux column``` 
    - **Type** : _string_
    - **doc** : The value here represents the flux column of the fits file for the light curve. You also
    need to set ```Time column``` and  ```Data folumn for hdulist```
    - **default** : none
- **Name** : ```Skpped rows in ascii file``` 
    - **Type** : _integer_
    - **doc** : The number defined here defines the number of rows skipped, if the file used is an ascii
    file. Useful, if you have some header description in your light curves.
    - **default** : 0
- **Name** : ```Used columns in ascii file``` 
    - **Type** : _List[integer]_
    - **doc** : This 2 dimensional list of values defines the correct columns for time and flux values
    in a file. The first value should be the column used for the temporal axis, the second value
    for the flux column. 
    - **default** : The first two columns in a file are used.
## Miscellaneous
- **Name** : ```List of IDs``` 
    - **Type** : _string_ or _List[int,float,float]_
    - **doc** : Here you can set the sample file for a given run. The sample file must contain, at a minimum,
    id, temperature and magnitude of all objects. You can also set the list directly in the run file, rather
    than a file name. If you set a file name, the path to it can be absolute or relative to the working directory.    
