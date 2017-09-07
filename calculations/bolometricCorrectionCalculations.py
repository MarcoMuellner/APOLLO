from math import log10


class BCCalculator:
    """
    This class computes the bolometric correction, when inputting an effective temperature. This stems from the paper
    by  Flower (1996) and the correction applied by Torres 2010. Meaning here is the (B-V) correction used.
    """
    def __init__(self,Teff):
        """
        Constructor for BCCalculator. Initializes fitparameter and calculates the Bolometric Correction.
        :param Teff: Effective temperature for the star
        :type: float/int
        """
        self.logTeff = log10(Teff)
        self.__setFitParameters()
        self.calculateBC()
        return

    def __setFitParameters(self):
        """
        Initializes the fitparameter introduced in Torres (2010).
        """
        self.a = 0
        self.b = 0
        self.c = 0
        self.d = 0
        self.e = 0
        self.f = 0

        if self.logTeff < 3.70:
            self.a = -0.190537291496456*10**5
            self.b = 0.155144866764412*10**5
            self.c = -0.421278819301717*10**4
            self.d = 0.381476328422343*10**3
        elif 3.70 <= self.logTeff <= 3.90:
            self.a = - 0.370510203809015*10**5
            self.b = 0.385672629965804*10**5
            self.c = -0.150651486316025*10**5
            self.d = 0.261724637119416*10**4
            self.e = -0.170623810323864*10**3
        elif self.logTeff > 3.90:
            self.a = -0.118115450538963*10**6
            self.b = 0.137145973583929*10**6
            self.c = -0.636233812100225*10**5
            self.d = 0.147412923562646*10**5
            self.e = -0.170587278406872*10**4
            self.f = 0.788731721804990*10**2

    def calculateBC(self):
        """
        Computes the BC and returns it. Formula taken from Flower (1996)
        :return: The Bolometric Correction
        :rtype: float
        """
        self._BC = (self.a + self.b * self.logTeff + self.c *self.logTeff**2
                    + self.d * self.logTeff**3 + self.e * self.logTeff ** 4
                    + self.f * self.logTeff ** 5)
        return self.BC

    @property
    def BC(self):
        """
        Property for the BC
        :return: Bolometric Correction (B-V)
        :rtype: float
        """
        return self._BC