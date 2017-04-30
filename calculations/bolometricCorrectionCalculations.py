from math import log10

class BCCalculator:
    def __init__(self,Teff):
        self.__logTeff = log10(Teff)
        self.__setFitParameters()
        self.calculateBC()
        return

    def __setFitParameters(self):
        self.__a = 0
        self.__b = 0
        self.__c = 0
        self.__d = 0
        self.__e = 0
        self.__f = 0

        if self.__logTeff < 3.70:
            self.__a = -0.190537291496456*10**5
            self.__b = 0.155144866764412*10**5
            self.__c = -0.421278819301717*10**4
            self.__d = 0.381476328422343*10**3
        elif 3.70 <= self.__logTeff <= 3.90:
            self.__a = - 0.370510203809015*10**5
            self.__b = 0.385672629965804*10**5
            self.__c = -0.150651486316025*10**5
            self.__d = 0.261724637119416*10**4
            self.__e = -0.170623810323864*10**3
        elif self.__logTeff > 3.90:
            self.__a = -0.118115450538963*10**6
            self.__b = 0.137145973583929*10**6
            self.__c = -0.636233812100225*10**5
            self.__d = 0.147412923562646*10**5
            self.__e = -0.170587278406872*10**4
            self.__f = 0.788731721804990*10**2
        return

    def calculateBC(self):
        self.__BC = (self.__a + self.__b * self.__logTeff + self.__c *self.__logTeff**2
                    + self.__d * self.__logTeff**3 + self.__e * self.__logTeff ** 4
                    + self.__f * self.__logTeff ** 5)
        return self.__BC

    def getBC(self):
        return self.__BC