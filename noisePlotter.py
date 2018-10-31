import numpy as np
import json
from support.directoryManager import cd
import os
from res.strings import *
from uncertainties import ufloat_fromstr,ufloat
import pylab as pl

for subdir, dirs, files in os.walk("noiseResults"):
    for dir in dirs:
        print(f"{subdir}/{dir}")
        for _,_,files in os.walk(f"{subdir}/{dir}"):
            pl.figure()
            for i in range(0,5):
                with cd(f"{subdir}/{dir}"):
                    try:
                        with open(f"results_noise_{i}.json") as f:
                            data = json.load(f)
                    except:
                        continue


                bayes = ufloat_fromstr(data[strAnalyzerResSectAnalysis][strAnalyzerResValBayes])
                signal = data[strAnalyseSectDiamonds][strDiModeFull][strPriorHeight]
                noise = data[strAnalyseSectDiamonds][strDiModeFull][strPriorFlatNoise]

                snr = ufloat_fromstr(signal)/ufloat_fromstr(noise)
                print(i,bayes)
                pl.plot(i,bayes.nominal_value,'x')
            pl.show()