# standard imports
from collections import OrderedDict as od
from typing import List, Dict,Tuple
import json
# scientific imports
import numpy as np
# project imports
from background.backgroundResults import BackgroundResults


def save_results(priors: List[List[float]], data : np.ndarray, kwargs: Dict):
    res_set,psd = compose_results(priors,kwargs)

    with open("results.json", 'w') as f:
        json.dump(res_set, f, indent=4)

    np.savetxt("psd.txt",psd)
    np.savetxt("lc.txt", data)


def compose_results(priors: List[List[float]], kwargs: Dict)->Tuple[od,np.ndarray]:
    result_full = BackgroundResults(kwargs, runID="FullBackground")
    result_noise = BackgroundResults(kwargs, runID="NoiseOnly")

    full_res_set = od()

    full_res_set["priors"] = get_priors(priors, result_full)

    full_res_set["Full Background result"] = get_resulting_values(result_full)
    full_res_set["Noise Background result"] = get_resulting_values(result_noise)

    full_res_set["Evidence Full Background"] = f"{result_full.evidence._evidence['Skillings log with Error']}"
    full_res_set["Evidence Noise Background"] = f"{result_noise.evidence._evidence['Skillings log with Error']}"
    full_res_set["Conclusion"] = bayes_factor(result_full.evidence._evidence["Skillings log with Error"],
                                              result_noise.evidence._evidence["Skillings log with Error"])

    psd = result_full.powerSpectralDensity

    return full_res_set,psd


def bayes_factor(evidence_full_background: float, evidence_noise_background: float):
    evidence = evidence_full_background - evidence_noise_background

    if evidence < 1:
        conclusion = "Inconclusive"
    elif 1 < evidence < 2.5:
        conclusion = "Weak evidence"
    elif 2.5 < evidence < 5:
        conclusion = "Moderate evidence"
    else:
        conclusion = "Strong evidence"

    return conclusion


def get_priors(priors: List[List[float]], res_set: BackgroundResults):
    res = od()

    for i in range(0, len(priors)):
        res[res_set._names[i]] = (priors[i][0], priors[i][1])

    return res


def get_resulting_values(res_set: BackgroundResults) -> od:
    res = od()

    res[res_set._names[0]] = f"{res_set.backgroundNoise}"
    res[res_set._names[1]] = f"{res_set.firstHarveyAmplitude}"
    res[res_set._names[2]] = f"{res_set.firstHarveyFrequency}"
    res[res_set._names[3]] = f"{res_set.secondHarveyAmplitude}"
    res[res_set._names[4]] = f"{res_set.secondHarveyFrequency}"
    res[res_set._names[5]] = f"{res_set.thirdHarveyAmplitude}"
    res[res_set._names[6]] = f"{res_set.thirdHarveyFrequency}"

    try:
        res[res_set._names[7]] = f"{res_set.oscillationAmplitude}"
        res[res_set._names[8]] = f"{res_set.nuMax}"
        res[res_set._names[9]] = f"{res_set.sigma}"
    except ValueError:
        pass
    finally:
        return res
