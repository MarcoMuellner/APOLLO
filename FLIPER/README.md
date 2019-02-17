# FLIPER SURFACE GRAVITY and NUMAX estimation

author: Lisa Bugnet

contact: lisa.bugnet@cea.fr

This repository is the property of L. Bugnet (please see and cite Bugnet et al.,2018).

# Description of the files

The FLIPER python code is made for the estimation of surface gravity of Kepler Solar-type oscillating targets with 0.1 < logg < 4.5 dex.

The user should first use the FLIPER class to calculate FliPer values from 0.2,0.7,7,20 and 50 muHz (see Bugnet et al.,2018). These values are the parameters needed by the machine learning Random Forest (along with the effective temperature and the Kepler magnitude of the star).

The Random Forest regressors are already trained and stored in the "ML_logg_training_paper" and "ML_numax_training_paper" files to estimate logg or numax. They should be download on this GitHub repository before running the FLIPER code. The estimation of surface gravity should be made by the use of the "ML" class (see CALLING SEQUENCE at the end of the code).

# What you need:

The power density spectrum of the star filtered with a 20 days high pass filter.
The power density spectrum of the star filtered with a 80 days high pass filter.
The Kepler magnitude of the star
The effective temperature of the star (from Mathur et al., 2017 for instance)
The "ML_logg_training_paper" and "ML_numax_training_paper" files containing the training of the Random Forest algorithms, to be dowload on GitHub.


## CALLING SEQUENCE

Paths to PSD fits files computed from light curves filtered with 20 and 80 days
```
psd_path_20             =   '/???/???'
psd_path_80             =   '/???/???'
```

Path to trained random forest (to be dowloaded on GitHub)
```
PATH_TO_TRAINING_FILE_LOGG   =   '/???/ML_logg_training_paper'
PATH_TO_TRAINING_FILE_NUMAX  =   '/???/ML_numax_training_paper'
```

Give star parameters
```
kepmag          =   12.349
teff            =   4750.0698938311934
error_teff      =   55.844606659634337
```


Open data from PSD_paths from 20 and 80 days light curves.
```
star_tab_psd_20 =   DATA_PREPARATION().PSD_PATH_TO_PSD(psd_path_20)
star_tab_psd_80 =   DATA_PREPARATION().PSD_PATH_TO_PSD(psd_path_80)
```

Calculate FliPer values.
```
Fliper_20_d =   FLIPER().Fp_20_days(star_tab_psd_20, kepmag)
Fliper_80_d =   FLIPER().Fp_80_days(star_tab_psd_80, kepmag)
Fp02        =   Fliper_80_d.fp02[0]
Fp07        =   Fliper_20_d.fp07[0]
Fp7         =   Fliper_20_d.fp7[0]
Fp20        =   Fliper_20_d.fp20[0]
Fp50        =   Fliper_20_d.fp50[0]
Teff        =   teff
KP          =   kepmag
```
Compute 100 stars per star by taking into account uncertainties on parameters.   (OPTIONNAL, ONLY TO REPRODUCE PAPER)
```
Fp02    =   FLIPER().RANDOM_PARAMS(Fliper_80_d.fp02[0], Fliper_80_d.sig_fp02[0])
Fp07    =   FLIPER().RANDOM_PARAMS(Fliper_20_d.fp07[0], Fliper_20_d.sig_fp07[0])
Fp7     =   FLIPER().RANDOM_PARAMS(Fliper_20_d.fp7[0] , Fliper_20_d.sig_fp7[0] )
Fp20    =   FLIPER().RANDOM_PARAMS(Fliper_20_d.fp20[0], Fliper_20_d.sig_fp20[0])
Fp50    =   FLIPER().RANDOM_PARAMS(Fliper_20_d.fp50[0], Fliper_20_d.sig_fp50[0])
Teff    =   FLIPER().RANDOM_PARAMS(teff, error_teff)
KP      =   np.full((100),kepmag)                                                      
```

Estimation of surface gravity and/or numax from the "ML_logg_training_paper" or "ML_numax_training_paper" file.
```
logg=ML().PREDICTION(Teff, KP, Fp02, Fp07, Fp7, Fp20, Fp50, PATH_TO_TRAINING_FILE_LOGG)
numax=10**(ML().PREDICTION(Teff, KP, Fp02, Fp07, Fp7, Fp20, Fp50, PATH_TO_TRAINING_FILE_NUMAX))
```


