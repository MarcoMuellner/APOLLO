from math import log10

class PriorCalculator:
    def __init__(self,initNuFilter,nuMax,photonNoise):
        self.__nuMax = nuMax

        self.calculateFirstHarveyFrequency(nuMax)
        self.calculatePhotonNoise(nuMax)
        self.calculateHarveyFrequencies(nuMax)
        self.calculateHarveyAmplitudes(nuMax)
        self.calculateAmplitude(nuMax)
        self.calculateSigma(nuMax)

        return

    def calculateHarveyFrequencies(self,nuMax):
        k_1 = 0.317 #Fit done by myself: 0.451
        k_2 = 0.948 #Fit done by myself: 0.871
        s_1 = 0.970 #Fit done by myself: 0.884
        s_2 = 0.992 #Fit done by myself: 1.018

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

        self.__sigma = k * pow(nuMax,s)

    def calculateAmplitude(self,nuMax):
        k = 67.163
        s = 1.187

        self.__amplitude = k*1/pow(nuMax,s)

    def calculatePhotonNoise(self,nuMax): #todo This seems fairly wrong, physically speaking. Why would the photon noise be dependend on nuMax?
        k = 119228.1
        s = 1.1811

        self.__photonNoise = k*1/pow(nuMax,s)

    def calculateFirstHarveyFrequency(self,nuMax):
        k = 1.951
        s = -0.071

        self.__b_0 = k*pow(nuMax,s)

    def getFirstHarveyFrequencyBoundary(self):
        return (0.7*self.__b_0,2.5*self.__b_0)

    def getSecondHarveyFrequencyBoundary(self):
        return (0.5 * self.__b_1,2 * self.__b_1)

    def getThirdHarveyFrequencyBoundary(self):
        return (0.5 * self.__b_2,1.5 * self.__b_2)

    def getHarveyAmplitudesBoundary(self):
        return (0.1 * self.__a,2.5*self.__a)

    def getNuMaxBoundary(self):
        return (0.5*self.__nuMax,1.5*self.__nuMax)

    def getSigmaBoundary(self):
        return (0.5*self.__sigma,1.5*self.__sigma)

    def getAmplitudeBounday(self):
        return (0.5*self.__amplitude,1.5*self.__amplitude)

    def getPhotonNoiseBoundary(self):
        return (0.1*self.__photonNoise,1.5*self.__photonNoise)

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
