import pytest
from evaluators.priorEvaluator import PriorEvaluator
from evaluators.inputDataEvaluator import InputDataEvaluator
from uncertainties import ufloat
import numpy as np

typeErrorTestCases = [
    "hello",
    (1,2),
    [1,2,3],
    {1:2,"drei":"vier"}
]

typeWorkingCases = [
    55,
    55.6,
    ufloat(55.6,10)
]

@pytest.fixture()
def psdCalc():
    lc  = np.loadtxt("tests/testFiles/Lightcurve.txt")
    return InputDataEvaluator(lightCurve= lc)


@pytest.mark.parametrize("value",typeErrorTestCases)
def testTypeFailure(psdCalc,value):
    with pytest.raises(TypeError):
        PriorEvaluator(value, psdCalc)

@pytest.mark.parametrize("value",typeWorkingCases)
def testTypeOk(psdCalc,value):
    assert PriorEvaluator(value, psdCalc).nuMax == value
