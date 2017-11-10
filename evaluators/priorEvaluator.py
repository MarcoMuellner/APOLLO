from math import log10
from evaluators.inputDataEvaluator import InputDataEvaluator
import numpy as np

class PriorEvaluator:
    '''
    The prior calculator class computes initial guesses for the priors, which then can be used as Priors for DIAMONDS.
    Most of the equations here are taken from the paper by Kallinger(2014), others are determined empirically. All of
    the values are initial guesses. Proper values can be determined by fitting the PSD
    '''
    def __init__(self, nuMax, powerCalc: InputDataEvaluator):
        '''
        Constructor of the priorCalculator. Automatically triggers the computation of the priors by setting the
        nuMax property
        :param psd: Object of the PSD calculator
        :type psd: InputDataEvaluator
        :param nuMax: Represents the frequency of maximum oscillation -> in uHz
        :type nuMax: float
        '''
        self._powerCalc = powerCalc
        self.photonNoise=powerCalc.photonNoise
        self.nuMax = nuMax

    def _runComputation(self):
        '''
        Runs the computation of the priors. Triggered by setting the nuMax property
        '''
        self._calculateFirstHarveyFrequency()
        self._calculate2nd3rdHarveyFrequencies()
        self._calculateHarveyAmplitudes()
        self._calculateOscillationAmplitude()
        self._calculateSigma()

    def _calculate2nd3rdHarveyFrequencies(self):
        '''
        Calculates the 2nd and 3rd Harvey frequencies
        '''
        k_1 = 0.317  # Fit done by myself: 0.451
        k_2 = 0.948  # Fit done by myself: 0.871
        s_1 = 0.970  # Fit done by myself: 0.884
        s_2 = 0.992  # Fit done by myself: 1.018

        self._secondHarveyFrequency = k_1 * pow(self.nuMax, s_1)
        self._thirdHarveyFrequency = k_2 * pow(self.nuMax, s_2)

    def _calculateHarveyAmplitudes(self):
        '''
        Calculates the Harvey amplitude. Only one amplitude is computed, and given big enough boundaries so that the
        fit does it properly
        '''
        k = 3383 #Second Harvey Fit done by myself: 2078
        s = -0.609 #Second Harvey  Fit done by myself: -0,496

        #Third Harvey Fit done by myself: 4545
        #Third Harvey Fit done by myself: -0.704

        self._harveyAmplitude = k * pow(self.nuMax, s)

    def _calculateSigma(self):
        '''
        Calculates the standard deviation of the power excess of the area of oscillation
        '''
        k = 1.124
        s = 0.505

        #k = 1.66 # my values
        #s = 0.6

        self._sigma = k * pow(self.nuMax, s)

    def _calculateOscillationAmplitude(self):
        '''
        Computes the amplitude of the oscillation by cutting of the signal at nuMax and taking the maximum of the
        smoothed value of the interestingRegion that is left after the cutoff.
        '''
        interestingRegion = np.array((self._powerCalc.powerSpectralDensity[0],self._powerCalc.smoothedData))
        interestingRegion = interestingRegion[1][interestingRegion[0] > self.nuMax]
        self._oscillationAmplitude = max(interestingRegion)

    def _calculateFirstHarveyFrequency(self):
        '''
        Calculates first harvey frequency
        '''
        #k = 1.951
        k = 19.51
        s = -0.071
        #s = -0.06 # test

        self._firstHarveyFrequency = k * pow(self.nuMax, s)

    @property
    def firstHarveyFrequencyBoundary(self):
        '''
        Property for the boundaries of the first Harvey frequency
        :return: Min-Max value for the first harvey frequency in uHz
        :rtype: tuple, 2 values as float
        '''
        return (0.04 * self._firstHarveyFrequency, 1.15 * self._firstHarveyFrequency)

    @property
    def secondHarveyFrequencyBoundary(self):
        '''
        Property for the boundaries of the second Harvey frequency
        :return: Min-Max value for the second harvey frequency in uHz
        :rtype: tuple, 2 values as float
        '''
        return (0.3 * self._secondHarveyFrequency, 1.48 * self._secondHarveyFrequency)

    @property
    def thirdHarveyFrequencyBoundary(self):
        '''
        Property for the boundaries of the third Harvey frequency
        :return: Min-Max value for the third harvey frequency in uHz
        :rtype: tuple, 2 values as float
        '''
        return (0.6 * self._thirdHarveyFrequency, 1.3 * self._thirdHarveyFrequency)

    @property
    def harveyAmplitudeBoundary(self):
        '''
        Property for the boundaries of harvey amplitudes
        :return: Min-Max value for the harvey amplitudes in ppm^2
        :rtype: tuple, 2 values as float
        '''
        return (0.1 * self._harveyAmplitude, 1.75 * self._harveyAmplitude)

    @property
    def nuMaxBoundary(self):
        '''
        Property for the boundaries of nuMax
        :return: Min-Max value for nuMax in uHz
        :rtype: tuple, 2 values as float
        '''
        return (0.8 * self._nuMax, 1.2 * self._nuMax)

    @property
    def sigmaBoundary(self):
        '''
        Property for the boundaries of the standard deviation of the power excess
        :return: Min-Max value for the standard deviation in uHz
        :rtype: tuple, 2 values as float
        '''
        return (0.2 * self._sigma, 1.5 * self._sigma)

    @property
    def oscillationAmplitudeBoundary(self):
        '''
        Property for the amplitude of the area of oscillation
        :return: Min-Max value for the amplitude of oscillation in ppm^2
        :rtype: tuple, 2 values as float
        '''
        return (0.25 * self._oscillationAmplitude, 1.5
                * self._oscillationAmplitude)

    @property
    def photonNoiseBoundary(self):
        '''
        Property for the boundaries of the photon noise
        :return: Min-Max value for the photon noise in ppm^2
        :rtype: tuple, 2 values as float
        '''
        return (0.2 * self._photonNoise, 4 * self._photonNoise)

    @property
    def photonNoise(self):
        '''
        Property for the photon noise
        :return: Value representing the photon noise in ppm^2
        :rtype: float
        '''
        return self._photonNoise

    @photonNoise.setter
    def photonNoise(self,value):
        '''
        Setter property for the photon noise
        :param value: value representing the photon noise in ppm^2
        :type value: float
        '''
        self._photonNoise = value

    @property
    def harveyAmplitude(self):
        '''
        Property for the harvey amplitude
        :return: Value representing the harvey amplitude in ppm^2
        :rtype: float
        '''
        return self._harveyAmplitude

    @property
    def firstHarveyFrequency(self):
        '''
        Property for first Harvey frequency
        :return: Value representing the first harvey frequency in uHz
        :rtype: float
        '''
        return self._firstHarveyFrequency

    @property
    def secondHarveyFrequency(self):
        '''
        Property for the second harvey frequency
        :return: Value representing the second harvey frequency in uHz
        :rtype: float
        '''
        return self._secondHarveyFrequency

    @property
    def thirdHarveyFrequency(self):
        '''
        Property for the third harvey frequency
        :return: Value representing the third harvey frequency in uHz
        :rtype: float
        '''
        return self._thirdHarveyFrequency

    @property
    def sigma(self):
        '''
        Property for the standard deviation of the power excess
        :return: Value representing the standard deviation in uHz
        :rtype: float
        '''
        return self._sigma

    @property
    def oscillationAmplitude(self):
        '''
        Property for the amplitude of oscillation
        :return: Value representing the amplitude of oscillation in ppm^2
        :rtype: float
        '''
        return self._oscillationAmplitude

    @property
    def nuMax(self):
        '''
        Property for frequency of maximum oscillation
        :return: Value representing the frequency of maximum oscillation in uHz
        :rtype: float
        '''
        return self._nuMax

    @nuMax.setter
    def nuMax(self,value):
        '''
        Setter property for the frequency of maximum oscillation. Triggers the computation of all the other values, you
        should therefore reread all other values
        :param value: Value representing the frequency of maximum oscillation in uHz
        :type value: float
        '''
        self._nuMax = value
        self._runComputation()

