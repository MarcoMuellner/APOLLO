# standard imports
from collections import OrderedDict as od
from typing import List, Dict,Tuple
import json
# scientific imports
import numpy as np
# project imports
from background.backgroundResults import BackgroundResults
from plotter.plot_handler import plot_f_space,plot_parameter_trend
from res.conf_file_str import internal_literature_value
from support.printer import print_int


def save_results(priors: List[List[float]], data : np.ndarray, nu_max : float, kwargs: Dict):
    res_set,psd = compose_results(priors,nu_max,kwargs)

    with open("results.json", 'w') as f:
        json.dump(res_set, f, indent=4)

    np.savetxt("psd.txt",psd)
    np.savetxt("lc.txt", data)


def create_parameter_trend_plot(result : BackgroundResults,kwargs : Dict):
    params = result.getBackgroundParameters()
    plot_dict = od()

    for param in params:
        plot_dict[param.name] = (param.getData(),param.unit)

    plot_parameter_trend(plot_dict,kwargs)


def compose_results(priors: List[List[float]],nu_max : float, kwargs: Dict)->Tuple[od,np.ndarray]:
    result_full = BackgroundResults(kwargs, runID="FullBackground")
    result_noise = BackgroundResults(kwargs, runID="NoiseOnly")

    create_parameter_trend_plot(result_full,kwargs)
    create_parameter_trend_plot(result_noise,kwargs)

    if result_full._summary is None or result_noise._summary is None:
        print_int("summaryErr",kwargs)
        raise ValueError("Summary file not found!")

    full_res_set = od()

    full_res_set["priors"] = get_priors(priors, result_full)

    full_res_set["Full Background result"] = get_resulting_values(result_full)
    full_res_set["Noise Background result"] = get_resulting_values(result_noise)

    full_res_set["Evidence Full Background"] = f"{result_full.evidence._evidence['Skillings log with Error']}"
    full_res_set["Evidence Noise Background"] = f"{result_noise.evidence._evidence['Skillings log with Error']}"

    conc,factor = bayes_factor(result_full.evidence._evidence["Skillings log with Error"],
                                              result_noise.evidence._evidence["Skillings log with Error"])
    full_res_set["Bayes factor"] = factor
    full_res_set["Conclusion"] = conc

    full_res_set["Nu max guess"] = nu_max

    if internal_literature_value in kwargs.keys():
        full_res_set[internal_literature_value] = kwargs[internal_literature_value]



    psd = result_full.powerSpectralDensity

    plot_f_space(psd.T, kwargs, bg_model=result_full.createBackgroundModel())
    plot_f_space(psd.T, kwargs, bg_model=result_noise.createBackgroundModel())

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

    return conclusion,str(evidence)


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
