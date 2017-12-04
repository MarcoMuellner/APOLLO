import os
import json
from uncertainties import ufloat,ufloat_fromstr
from res.strings import *


path = "results/"

inconclusiveList = []
weakEvidenceList = []
strongEvidenceList = []

for i in os.listdir(path):
    if "YS" not in i:
        continue
    with open(path+i+"/results.json", 'rt') as f:
        resultDict = json.load(f)

    analyzeSection = resultDict[strAnalyzerResSectAnalysis]
    bayesFactor = analyzeSection[strAnalyzerResValBayes]
    bayesFactor = ufloat_fromstr(bayesFactor)
    if bayesFactor > 5:
        valuesOk = True
        for key,value in analyzeSection[strDiamondsModeFull].items():
            if value != "Okay":
                valuesOk = False

        for key,value in analyzeSection[strDiamondsModeNoise].items():
            if value != "Okay":
                valuesOk = False

        if valuesOk:
            print("Star "+i+" is good with Bayyes Factor of "+str(bayesFactor))
            strongEvidenceList.append(i[3:])

print(strongEvidenceList)