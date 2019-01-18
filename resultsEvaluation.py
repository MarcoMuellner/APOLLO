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
    for key, value in analyzeSection[strDiModeFull].items():
        if value != "Okay":
            valuesOk = False

    for key, value in analyzeSection[strDiModeNoise].items():
        if value != "Okay":
            valuesOk = False

    return valuesOk

for i in os.listdir(path):
    try:
        with open(path+i+"/results.json", 'rt') as f:
            resultDict = json.load(f)
    except:
        continue

    bayesFactor = ufloat_fromstr(resultDict["Bayes factor"])
    if bayesFactor >= 5:
        strongEvidenceList.append(i[3:])
    elif 2.5 <= bayesFactor and bayesFactor < 5:
        moderateEvidenceList.append(i[3:])
    elif 1 <= bayesFactor and bayesFactor <2.5:
        weakEvidenceList.append(i[3:])

print("STRONG EVIDENCE")
print(strongEvidenceList)
print("MODERATE EVIDENCE")
print(moderateEvidenceList)
print("WEAK EVIDENCE")
print(weakEvidenceList)