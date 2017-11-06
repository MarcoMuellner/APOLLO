import pytest
import numpy as np
from uncertainties import ufloat
from evaluators.nuMaxEvaluator import NuMaxEvaluator
from shutil import copy2

typeIterativeFilterFailureTestCases = [
    "string",
    ufloat(20,20),
    {"dict":0},
    {0:"dict"},
    ["list"],
    []
]

typeFailureTestCases = [0,
                        5.0,
                        typeIterativeFilterFailureTestCases]

valueFailureTestCases  = [
    np.zeros(5),
    np.arange(1,5,1),
    np.array((np.arange(1,5,1),np.arange(1,5,1),np.arange(1,5,1))),
    np.array((np.arange(10**8,10**9,10**7),np.arange(0,10,1)))
]

@pytest.fixture(scope='module')
def nuMaxObject():
    copy2("tests/testFiles/lightCurveAnalyzer.json","~")
    lightCurve = np.loadtxt("tests/testFiles/Lightcurve.txt", skiprows=1)
    return NuMaxEvaluator("testKIC", lightCurve)

@pytest.mark.parametrize("value",typeFailureTestCases)
def testFailureTypeNuMaxCalc(value):
    with pytest.raises(TypeError):
        NuMaxEvaluator("testKIC", value)

@pytest.mark.parametrize("value",valueFailureTestCases)
def testFailureValueNuMaxCalc(value):
    with pytest.raises(ValueError):
        NuMaxEvaluator("testKIC", value)

def testFlickerandInitFilter(nuMaxObject):
    '''

    :type nuMaxObject: NuMaxEvaluator
    '''
    assert abs(nuMaxObject._amp_flic -376.24946261729275) < 10**-6
    assert abs(nuMaxObject._init_nu_filter - 14.765821506000474) < 10 ** -6
    assert len(nuMaxObject.marker) == 1
    assert nuMaxObject.marker["InitialFilter"][0] == nuMaxObject._init_nu_filter

@pytest.mark.parametrize("value",typeIterativeFilterFailureTestCases)
def testFailureIterativeFilter(nuMaxObject,value):
    '''

    :type nuMaxObject: NuMaxEvaluator
    '''
    with pytest.raises(TypeError):
        nuMaxObject._iterativeFilter(value)

    with pytest.raises(ValueError):
        nuMaxObject._iterativeFilter(0)

@pytest.mark.parametrize("input,output",[
                            (15,80.33954376499203),
                            (15.0,80.33954376499203),
                            (80.33954376499203,112.37891726222568 )
                                        ])
def testIterativeFilterValues(nuMaxObject,input,output):
    '''

    :type nuMaxObject: NuMaxEvaluator
    '''
    assert abs(nuMaxObject._iterativeFilter(input) - output) < 10**-6

@pytest.mark.parametrize("input,output",[
                             (None,63.253425165010093),
                             (10,63.253425165010093),
                             (20,63.253425165010093)
                         ])
def testComputeNuMax(nuMaxObject,input,output):
    '''

    :type nuMaxObject: NuMaxEvaluator
    '''
    if input is None:
        input = nuMaxObject._init_nu_filter

    nuMaxObject._init_nu_filter = input
    assert (nuMaxObject.computeNuMax() - output) < 1
