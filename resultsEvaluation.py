import os
import json
from uncertainties import ufloat,ufloat_fromstr
from res.strings import *


path = "results/"

inconclusiveList = []
weakEvidenceList = []
moderateEvidenceList = []
strongEvidenceList = []

def checkValues(analyzeSection):
    valuesOk = True
    for key, value in analyzeSection[strDiamondsModeFull].items():
        if value != "Okay":
            valuesOk = False

    for key, value in analyzeSection[strDiamondsModeNoise].items():
        if value != "Okay":
            valuesOk = False

    return valuesOk

for i in os.listdir(path):
    if "YS" not in i:
        continue
    try:
        with open(path+i+"/results.json", 'rt') as f:
            resultDict = json.load(f)
    except:
        continue

    analyzeSection = resultDict[strAnalyzerResSectAnalysis]
    bayesFactor = analyzeSection[strAnalyzerResValBayes]
    bayesFactor = ufloat_fromstr(bayesFactor)
    if bayesFactor >= 5:
        valuesOk = checkValues(analyzeSection)

        if valuesOk:
            #print("Star "+i+" is good with Bayyes Factor of "+str(bayesFactor))
            strongEvidenceList.append(i[3:])
    elif 2.5 <= bayesFactor and bayesFactor < 5:
        valuesOk = checkValues(analyzeSection)

        if valuesOk:
            moderateEvidenceList.append(i[3:])
    elif 1 <= bayesFactor and bayesFactor <2.5:
        valuesOk = checkValues(analyzeSection)

        if valuesOk:
            weakEvidenceList.append(i[3:])

print("STRONG EVIDENCE")
print(strongEvidenceList)
print("MODERATE EVIDENCE")
print(moderateEvidenceList)
print("WEAK EVIDENCE")
print(weakEvidenceList)