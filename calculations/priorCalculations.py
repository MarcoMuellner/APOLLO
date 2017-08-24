from math import log10

class PriorCalculator:
    def __init__(self,nuMax,photonNoise):
        self.__nuMax = nuMax
        self.__photonNoise=photonNoise
        self.calculateFirstHarveyFrequency(nuMax)
        self.calculateHarveyFrequencies(nuMax)
        self.calculateHarveyAmplitudes(nuMax)
        self.calculateAmplitude(nuMax)
        self.calculateSigma(nuMax)

        return

    def calculateHarveyFrequencies(self,nuMax):
        '''
        k_1 = 0.317 #Fit done by myself: 0.451
        k_2 = 0.948 #Fit done by myself: 0.871
        s_1 = 0.970 #Fit done by myself: 0.884
        s_2 = 0.992 #Fit done by myself: 1.018
'''
        k_1 = 0.317  # Fit done by myself: 0.451
        k_2 = 0.948  # Fit done by myself: 0.871
        s_1 = 0.970  # Fit done by myself: 0.884
        s_2 = 0.992  # Fit done by myself: 1.018

        self.__b_1 = k_1 * pow(nuMax, s_1)
        self.__b_2 = k_2 * pow(nuMax, s_2)

        return self.__b_1, self.__b_2

    def calculateHarveyAmplitudes(self,nuMax):
        k = 3335 #Second Harvey Fit done by myself: 2078
        s = -0.564 #Second Harvey  Fit done by myself: -0,496

        #Third Harvey Fit done by myself: 4545
        #Third Harvey Fit done by myself: -0.704

        self.__a = k * pow(nuMax, s)
        return self.__a

    def calculateSigma(self,nuMax):
        k = 1.124
        s = 0.505

        #k = 1.66 # my values
        #s = 0.6

        self.__sigma = k * pow(nuMax,s)

    def calculateAmplitude(self,nuMax):
        k = 216833
        s = -1.52

        self.__amplitude = k*pow(nuMax,s)

    def calculateFirstHarveyFrequency(self,nuMax):
        #k = 1.951
        k = 19.51
        s = -0.071
        #s = -0.06 # test

        self.__b_0 = k*pow(nuMax,s)

    def getFirstHarveyFrequencyBoundary(self):
        return (0.04*self.__b_0,1.15*self.__b_0)

    def getSecondHarveyFrequencyBoundary(self):
        return (0.3 * self.__b_1,1.48 * self.__b_1)

    def getThirdHarveyFrequencyBoundary(self):
        return (0.6 * self.__b_2,1.3 * self.__b_2)

    def getHarveyAmplitudesBoundary(self):
        return (0.018 * self.__a,0.31*self.__a)

    def getNuMaxBoundary(self):
        return (0.9*self.__nuMax,1.2*self.__nuMax)

    def getSigmaBoundary(self):
        return (0.2*self.__sigma,1.5*self.__sigma)

    def getAmplitudeBounday(self):
        return (0.007*self.__amplitude,0.2
                *self.__amplitude)

    def getPhotonNoiseBoundary(self):
        return (0.2*self.__photonNoise,2*self.__photonNoise)

    def getPhotonNoise(self):
        return self.__photonNoise

    def getHarveyAmplitude(self):
        return self.__a

    def getHarveyFrequency1(self):
        return self.__b_0

    def getHarveyFrequency2(self):
        return self.__b_1

    def getHarveyFrequency3(self):
        return self.__b_2

    def getSigma(self):
        return self.__sigma

    def getHarveyFrequencies(self):
        return self.__b_0,self.__b_1,self.__b_2

    def getHarveyAmplitudes(self):
        return self.__a

    def getAmplitude(self):
        return self.__amplitude
