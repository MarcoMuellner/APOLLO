import pytest
from calculations.powerspectraCalculations import PowerspectraCalculator
from uncertainties import ufloat
import numpy as np

typeFailureTestCases = [0,
                        5.0,
                        "string",
                        ufloat(20, 20),
                        {"dict": 0},
                        {0: "dict"},
                        ["list"],
                        []]

@pytest.mark.parametrize("value",typeFailureTestCases)
def testTypeFailureInitPowerspectraCalculator(value):
    with pytest.raises(TypeError):
        PowerspectraCalculator(lightCurve=value)
    with pytest.raises(TypeError):
        PowerspectraCalculator(powerSpectralDensity=value)

@pytest.fixture(scope='module')
def psdInitObject():
    return PowerspectraCalculator(powerSpectralDensity = np.loadtxt("tests/testFiles/PSD.txt"))

@pytest.fixture(scope='module')
def lightCurveInitObject():
    return PowerspectraCalculator(lightCurve = np.loadtxt("tests/testFiles/Lightcurve.txt"))

@pytest.fixture(scope='module')
def bothInitObject():
    return PowerspectraCalculator(np.loadtxt("tests/testFiles/Lightcurve.txt"),np.loadtxt("tests/testFiles/PSD.txt"))

def testPeriodogrammConversion(bothInitObject):
    """

    :type bothInitObject: PowerspectraCalculator
    """
    psd = np.loadtxt("tests/testFiles/PSD.txt")
    result = bothInitObject.lightCurveToPowerspectraPeriodogramm(bothInitObject.lightCurve)
    result = np.array((result[0][1:],result[1][1:]))
    assert np.allclose(psd,result)

@pytest.mark.skip("Numpy conversion doesn't work at the moment")
def testNumpyConversion(bothInitObject):
    """

    :type bothInitObject: PowerspectraCalculator
    """
    psd = np.loadtxt("tests/testFiles/PSD.txt")
    result = bothInitObject.lightCurveToPowerspectraFFT(bothInitObject.lightCurve)
    result = np.array((result[0][1:], result[1][1:]))
    assert np.allclose(psd,result)


def testConversion(bothInitObject):
    psd = np.loadtxt("tests/testFiles/PSD.txt")
    result = bothInitObject.lightCurveToPowerspectra(bothInitObject.lightCurve)
    result = np.array((result[0][1:], result[1][1:]))
    assert np.allclose(psd,result)

def testBehaviourLightCurveOnly(lightCurveInitObject):
    """

    :type lightCurveInitObject: PowerspectraCalculator
    """
    psd = np.loadtxt("tests/testFiles/PSD.txt")
    assert np.allclose(psd,lightCurveInitObject.powerSpectralDensity)

def testPhotonNoise(lightCurveInitObject):
    """

    :type lightCurveInitObject: PowerspectraCalculator
    """
    assert abs(lightCurveInitObject.photonNoise -0.032855057568791569)<10**-4

def testNyqFreq(lightCurveInitObject):
    """

    :type lightCurveInitObject: PowerspectraCalculator
    """
    assert abs(lightCurveInitObject.nyqFreq -24469084.036874708)<10**-4

@pytest.mark.parametrize("kics",[0,"hello",0.0])
def testKicID(lightCurveInitObject,kics):
    """

    :type lightCurveInitObject: PowerspectraCalculator
    """
    lightCurveInitObject.kicID = kics
    assert lightCurveInitObject.kicID == kics


