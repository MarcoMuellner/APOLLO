class PriorCalculator:
    def __init__(self,initNuFilter,nuMax,photonNoise):
        self.__nuMax = nuMax
        self.__initNuFilter = initNuFilter
        self.__photonNoise = photonNoise

        self.calculateHarveyFrequencies(nuMax)
        self.calculateHarveyAmplitudes(nuMax)
        self.calculateAmplitude(nuMax)
        self.calculateSigma(nuMax)

        return

    def calculateHarveyFrequencies(self,nuMax):
        k_1 = 0.317
        k_2 = 0.948
        s_1 = 0.970
        s_2 = 0.992

        self.__b_1 = k_1 * pow(nuMax, s_1)
        self.__b_2 = k_2 * pow(nuMax, s_2)

        return self.__b_1, self.__b_2

    def calculateHarveyAmplitudes(self,nuMax):
        k = 3335
        s = -0.564

        self.__a = k * pow(nuMax, s)
        return self.__a

    def calculateSigma(self,nuMax):
        k = 1.0652
        s = 0.542

        self.__sigma = k * pow(nuMax,s)

    def calculateAmplitude(self,nuMax):
        k = 55980.9
        s = 1.353

        self.__amplitude = k*1/pow(nuMax,s)

    def getFirstHarveyFrequencyBoundary(self):
        return (0.5*self.__initNuFilter,1.5*self.__initNuFilter)

    def getSecondHarveyFrequencyBoundary(self):
        return (0.5 * self.__b_1, 1.5 * self.__b_1)

    def getThirdHarveyFrequencyBoundary(self):
        return (0.5 * self.__b_2, 1.5 * self.__b_2)

    def getHarveyAmplitudesBoundary(self):
        return (0.5 * self.__a,1.5*self.__a)

    def getNuMaxBoundary(self):
        return (0.5*self.__nuMax,1.5*self.__nuMax)

    def getSigmaBoundary(self):
        return (0.5*self.__sigma,1.5*self.__sigma)

    def getAmplitudeBounday(self):
        return (0.5*self.__amplitude,1.5*self.__amplitude)

    def getPhotonNoiseBoundary(self):
        return (0.5*self.__photonNoise,1.5*self.__photonNoise)

    def getSigma(self):
        return self.__sigma

    def getHarveyFrequencies(self):
        return self.__initNuFilter,self.__b_1,self.__b_2

    def getHarveyAmplitudes(self):
        return self.__a

    def getAmplitude(self):
        return self.__amplitude
