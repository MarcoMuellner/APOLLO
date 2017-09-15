import pytest
from evaluators.bcEvaluator import BCEvaluator
from uncertainties import ufloat
import os
import matplotlib as mpl

valueTestCases = {
    200:-1012.3831518705101,
    6000:-0.04488705990661401,
    ufloat(6000,200):ufloat(-0.04488705990661401,0.027592869344328363)
}

typeFailureCases = ["string",
                    {"dict":0},
                    {0:"dict"},
                    ["list","list"],
                    [],
]

@pytest.fixture(params=valueTestCases.keys())
def valueCalculator(request):
    return (BCEvaluator(request.param), request.param)

def testValueBCCalc(valueCalculator):
    assert abs(valueCalculator[0].BC - valueTestCases[valueCalculator[1]]) < 10**-6

def testFailureValueBCCalc():
    with pytest.raises(ValueError):
        BCEvaluator(0)

@pytest.mark.parametrize("value",typeFailureCases)
def testFailureTypeBCCalc(value):
    with pytest.raises(TypeError):
        BCEvaluator(value)
