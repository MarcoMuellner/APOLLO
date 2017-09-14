import numpy as np
import pytest
from uncertainties import ufloat

from calculations.powerspectraCalculations import PowerspectraCalculator

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

@pytest.mark.skip("Conversion tests disabled")
def testPeriodogrammConversion(bothInitObject):
    '''

    :type bothInitObject: PowerspectraCalculator
    '''
    psd = bothInitObject.powerSpectralDensity
    result = bothInitObject.lightCurveToPowerspectraPeriodogramm(bothInitObject.lightCurve)
    result = np.array((result[0],result[1]))
    assert abs(np.amax(result[1] - psd[1])) < 10 ** -4

@pytest.mark.skip("Numpy conversion doesn't work at the moment")
def testNumpyConversion(bothInitObject):
    '''

    :type bothInitObject: PowerspectraCalculator
    '''
    psd = np.loadtxt("tests/testFiles/PSD.txt")
    result = bothInitObject.lightCurveToPowerspectraFFT(bothInitObject.lightCurve)
    result = np.array((result[0], result[1]))
    assert abs(np.amax(result[1]-psd[1])) < 10**-4

@pytest.mark.skip("Conversion tests disabled")
def testConversion(bothInitObject):
    psd = np.loadtxt("tests/testFiles/PSD.txt")
    result = bothInitObject.lightCurveToPowerspectra(bothInitObject.lightCurve)
    result = np.array((result[0], result[1]))
    assert abs(np.amax(result[1] - psd[1])) < 10 ** -4

@pytest.mark.skip("Conversion tests disabled")
def testBehaviourLightCurveOnly(lightCurveInitObject):
    '''

    :type lightCurveInitObject: PowerspectraCalculator
    '''
    psd = np.loadtxt("tests/testFiles/PSD.txt")
    assert abs(np.amax(lightCurveInitObject.powerSpectralDensity[1] - psd[1])) < 10 ** -4

def testPhotonNoise(lightCurveInitObject):
    '''

    :type lightCurveInitObject: PowerspectraCalculator
    '''
    assert abs(lightCurveInitObject.photonNoise -4.174009048728105)<10**-4

def testNyqFreq(lightCurveInitObject):
    '''

    :type lightCurveInitObject: PowerspectraCalculator
    '''
    assert abs(lightCurveInitObject.nyqFreq -283.20699116753133)<10**-4

@pytest.mark.parametrize("kics",[0,"hello",0.0])
def testKicID(lightCurveInitObject,kics):
    '''

    :type lightCurveInitObject: PowerspectraCalculator
    '''
    lightCurveInitObject.kicID = kics
    assert lightCurveInitObject.kicID == kics

def testSmoothing(lightCurveInitObject):
    '''

    :type lightCurveInitObject: PowerspectraCalculator
    '''
    x = lightCurveInitObject.powerSpectralDensity[0]
    y = lightCurveInitObject.smoothedData

    y = y[x>45]

    assert abs(max(y)-1796.7633307147535)<1



