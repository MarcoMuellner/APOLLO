import numpy as np
from scipy.signal import butter, filtfilt
from scipy import optimize

class DeltaNuCalculator:
    m_nuMax = None
    m_sigma = None
    m_psd = None
    m_backgroundModel = None
    m_backgroundParameters = None
    m_gaussBoundaries = None
    m_deltaNuEst = None
    m_nyq = None
    m_y0 = (0,0)
    m_amp = (0,0)
    m_cen = (0,0)
    m_wid = (0,0)
    m_multiplicator = 2

    def __init__(self,nuMax,sigma,psd,nyq,backGroundParameters,backGroundModel):
        self.m_nuMax = nuMax
        self.m_sigma = sigma
        self.m_psd = psd
        self.m_backgroundModel = backGroundModel
        self.m_backgroundParameters = backGroundParameters
        self.m_nyq = nyq
        return

    def calculateFit(self):
        background = np.sum(self.m_backgroundModel[0:4], axis=0)

        # Divide raw Spectrum by background
        clearedData = np.divide(self.m_psd[1], background)

        par_median, par_le, par_ue = self.m_backgroundParameters
        hg = par_median[7]  # Amplitude of Gauss
        numax = par_median[8]  # xc of Gauss
        sigma = par_median[9]  # Standard Deviation
        minima, maxima, indexMin, indexMax = self.findGaussBoundaries(self.m_multiplicator)  # get Boundaries of Gauss, 2-3 Sigma is recommended

        # Estimate Delta Nu from numax
        self.m_deltaNuEst = self.estimateDeltaNu()

        # smooth data
        clearedData = self.butter_lowpass_filtfilt(clearedData, self.m_nyq, self.m_deltaNuEst)
        oscillatingData = np.vstack((self.m_psd[0][indexMin:indexMax], clearedData[indexMin:indexMax]))

        # calculate autocorrelation
        corrs = self.calculateAutocorrelation(oscillatingData)

        # Calculte stepsize and x-Axis for Autocorrelation
        stepFreq = self.m_psd[0][2] - self.m_psd[0][1]
        deltaF = np.zeros(len(corrs))
        for i in range(0, len(deltaF)):
            deltaF[i] = i * stepFreq

        # calculate Fit
        self.scipyFit(np.array((deltaF, corrs)), self.m_deltaNuEst)

    def findGaussBoundaries(self,multiplicator,data = None,cen = None,sigma = None):
        minima = 0
        maxima = 0
        deltaMinima = 1000
        deltaMaxima = 1000
        indexMin = 0
        indexMax = 0
        psd = data if data is not None else self.m_psd
        cen = cen if cen is not None else self.m_nuMax
        sigma = sigma if sigma is not None else self.m_sigma
        for i in range(0, len(psd[0]) - 1):
            if (abs(psd[0][i] - (cen - multiplicator*sigma)) < deltaMinima):
                deltaMinima = abs(psd[0][i] - (cen  - multiplicator*sigma))
                minima = psd[0][i]
                indexMin = i

            if (abs(psd[0][i] - (cen  + multiplicator*sigma)) < deltaMaxima):
                deltaMaxima = abs(psd[0][i] - (cen  + multiplicator*sigma))
                maxima = psd[0][i]
                indexMax = i

        print("Final minima: '" + str(minima) + "', final maxima: '" + str(maxima) + "', numax: '"
              + str(cen ) + "', sigma: '" + str(sigma) + "'")

        self.m_gaussBoundaries = (minima, maxima, indexMin, indexMax)
        return self.m_gaussBoundaries

    def butter_lowpass_filtfilt(self,data, nyq, level, order=5):
        b, a = self.butter_lowpass(level, nyq, order=order)
        y = filtfilt(b, a, data)
        return y

    def butter_lowpass(self,cutoff, nyq, order=5):
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def calculateAutocorrelation(self,oscillatingData):
        psd = self.m_psd
        backgroundModel = self.m_backgroundModel
        background = np.sum(backgroundModel[0:4],axis=0)
        clearedData = np.divide(psd[1], background)

        oscillatingData = np.vstack((psd[0][self.m_gaussBoundaries[2]:self.m_gaussBoundaries[3]],
                                     clearedData[self.m_gaussBoundaries[2]:self.m_gaussBoundaries[3]]))


        corrs2 = np.correlate(oscillatingData[1], oscillatingData[1], mode='full')
        N = len(corrs2)
        corrs2 = corrs2[N // 2:]
        lengths = range(N, N // 2, -1)
        corrs2 /= lengths
        corrs2 /= corrs2[0]
        return corrs2

    def estimateDeltaNu(self,nuMax = None):
        nuMax = nuMax if nuMax is not None else self.m_nuMax
        self.m_deltaNuEst = 0.263 * pow(nuMax, 0.772)
        return self.m_deltaNuEst

    def gaussian(self,x, y0, amp, cen, wid):
        return y0 + (amp / (np.sqrt(2 * np.pi) * wid)) * np.exp(-(x - cen) ** 2 / (2 * wid ** 2))

    def scipyFit(self,data, deltaNuEst):
        y = data[1]
        x = data[0]
        minima, maxima, indexMin, indexMax = self.findGaussBoundaries(self.m_multiplicator,data,deltaNuEst,0.2*deltaNuEst)
        print(indexMin,indexMax)
        index = np.where(y == np.amax(y[indexMin:indexMax]))

        initY0 = np.mean(y[indexMin:indexMax])
        initAmp = np.amax(y[indexMin:indexMax] / 4)
        initCen = data[0][index[0]]
        initWid = 0.10
        arr = [initY0, initAmp, initCen, initWid]

        bounds = ([np.mean(y[indexMin:indexMax]) - 0.05, np.amax(y[indexMin:indexMax]) / 8, initCen - 0.01, 0.05]
                  , [np.mean(y[indexMin:indexMax]) + 0.05, np.amax(y[indexMin:indexMax]) / 2, initCen + 0.01, 0.3])

        self.m_popt, pcov = optimize.curve_fit(self.gaussian, x, y, p0=arr, bounds=bounds)
        self.m_perr = np.sqrt(np.diag(pcov))

        self.m_y0 = (self.m_popt[0],self.m_perr[0])
        self.m_amp = (self.m_popt[1],self.m_perr[1])
        self.m_cen = (self.m_popt[2],self.m_perr[2])
        self.m_wid = (self.m_popt[3],self.m_perr[3])

        print("y0 = '" + str(self.m_y0[0]) + " (" + str(self.m_y0[1]) + ")'")
        print("amp = '" + str(self.m_amp[0]) + " (" + str(self.m_amp[1]) + ")'")
        print("cen = '" + str(self.m_cen [0]) + " (" + str(self.m_cen [1]) + ")'")
        print("wid = '" + str(self.m_wid[0]) + " (" + str(self.m_wid[1]) + ")'")

        return self.m_popt

    def getY0(self):
        return self.m_y0

    def getAmp(self):
        return self.m_amp

    def getCen(self):
        return self.m_cen

    def getWid(self):
        return self.m_wid


