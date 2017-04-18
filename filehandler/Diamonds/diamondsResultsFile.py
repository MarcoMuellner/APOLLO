import glob
import numpy as np

from filehandler.Diamonds.InternalStructure.backgroundParameterSummaryFile import ParameterSummary
from filehandler.Diamonds.InternalStructure.backgroundEvidenceInformationFile import Evidence
from filehandler.Diamonds.InternalStructure.backgroundParameterFile import BackgroundParameter
from filehandler.Diamonds.InternalStructure.backgroundMarginalDistributionFile import MarginalDistribution
from filehandler.Diamonds.diamondsPriorsFile import Priors
from filehandler.Diamonds.dataFile import DataFile
from settings.settings import Settings
from support.strings import *


class Results:
    m_summary = None
    m_evidence = None
    m_backgroundParameter = {}
    m_marginalDistributions = []
    m_prior = None
    m_backgroundPriors = None
    m_kicID = None
    m_runID = None
    m_dataFile = None
    m_names = []
    m_units = []
    m_nyq = None
    m_dataFolder = None

    def __init__(self,kicID,runID):
        self.m_kicID = kicID
        self.m_runID = runID
        self.m_dataFile = DataFile(kicID)
        self.m_summary = ParameterSummary(kicID,runID)
        self.m_evidence = Evidence(kicID,runID)
        self.m_prior = Priors(kicID)
        self.m_backgroundPriors = Priors(kicID,runID)
        self.m_dataFolder = Settings.Instance().getSetting(strDataSettings, strSectBackgroundResPath).value
        nyqFile = glob.glob(self.m_dataFolder + 'KIC{}/NyquistFrequency.txt'.format(kicID))[0]
        self.m_nyq = np.loadtxt(nyqFile)

        self.m_names = ['w', '$\sigma_\mathrm{long}$', '$b_\mathrm{long}$','$\sigma_\mathrm{gran,1}$',
                  '$b_\mathrm{gran,1}$', '$\sigma_\mathrm{gran,2}$', '$b_\mathrm{gran,2}$',
                  '$H_\mathrm{osc}$','$f_\mathrm{max}$ ', '$\sigma_\mathrm{env}$']

        self.m_units = ['ppm$^2$/$\mu$Hz', 'ppm', '$\mu$Hz','ppm','$\mu$Hz', 'ppm', '$\mu$Hz','(ppm$^2$/$\mu$Hz)',
                        '($\mu$Hz)','($\mu$Hz)']

        for i in range(0,10):
            par_median = self.m_summary.getData(strSummaryMedian)[i]  # median values
            par_le = self.m_summary.getData(strSummaryLowCredLim)[i]  # lower credible limits
            par_ue = self.m_summary.getData(strSummaryUpCredlim)[i]  # upper credible limits
            backGroundParameters = np.vstack((par_median, par_le, par_ue))

            self.m_backgroundParameter[self.m_names[i]] = BackgroundParameter(self.m_names[i],self.m_units[i],kicID,runID,i)

            self.m_marginalDistributions.append(MarginalDistribution(self.m_names[i], self.m_units[i], kicID, runID, i))
            print(self.m_names[i])
            self.m_marginalDistributions[i].setBackgroundParameters(backGroundParameters)

    def getBackgroundParameters(self,key = None):
        if key is None:
            return self.m_backgroundParameter
        else:
            if key in self.m_backgroundParameter.keys():
                return self.m_backgroundParameter[key]
            else:
                return self.m_backgroundParameter

    def getPrior(self):
        return self.m_prior

    def getBackgroundPrior(self):
        return self.m_backgroundPriors

    def getEvidence(self):
        return self.m_evidence

    def getSummary(self):
        return self.m_summary

    def getNyquistFrequency(self):
        return self.m_nyq

    def getPSD(self):
        return self.m_dataFile.getPSD()

    def getSmoothing(self):
        return None #TODO return useful value here

    def getKicID(self):
        return self.m_kicID


    def createBackgroundModel(self, runGauss):
        freq, psd = self.m_dataFile.getPSD()
        par_median = self.m_summary.getData(strSummaryMedian)  # median values
        par_le = self.m_summary.getData(strSummaryLowCredLim)  # lower credible limits
        par_ue = self.m_summary.getData(strSummaryUpCredlim) # upper credible limits
        if runGauss:
            hg = par_median[
                7]  # third last parameter
            numax = par_median[8]  # second last parameter
            sigma = par_median[9]  # last parameter

            print("Height is '" + str(hg) + "'")
            print("Numax is '" + str(numax) + "'")
            print("Sigma is '" + str(sigma) + "'")

        zeta = 2. * np.sqrt(2.) / np.pi  # !DPI is the pigreca value in double precision
        r = (np.sin(np.pi / 2. * freq / self.m_nyq) / (
        np.pi / 2. * freq / self.m_nyq)) ** 2  # ; responsivity (apodization) as a sinc^2
        w = par_median[0]  # White noise component
        g = 0
        if runGauss:
            g = hg * np.exp(-(numax - freq) ** 2 / (2. * sigma ** 2))  ## Gaussian envelope TODO this too

        ## Long-trend variations
        sigma_long = par_median[1]
        freq_long = par_median[2]
        h_long = (sigma_long ** 2 / freq_long) / (1. + (freq / freq_long) ** 4)

        ## First granulation component
        sigma_gran1 = par_median[3]
        freq_gran1 = par_median[4]
        h_gran1 = (sigma_gran1 ** 2 / freq_gran1) / (1. + (freq / freq_gran1) ** 4)

        ## Second granulation component
        sigma_gran2 = par_median[5]
        freq_gran2 = par_median[6]
        h_gran2 = (sigma_gran2 ** 2 / freq_gran2) / (1. + (freq / freq_gran2) ** 4)

        ## Global background model
        w = np.zeros_like(freq) + w
        b1 = zeta * (h_long + h_gran1 + h_gran2) * r + w
        print("Whitenoise is '" + str(w) + "'")
        if runGauss:
            b2 = (zeta * (h_long + h_gran1 + h_gran2) + g) * r + w
            return zeta * h_long * r, zeta * h_gran1 * r, zeta * h_gran2 * r, w, g * r
        else:
            return zeta * h_long * r, zeta * h_gran1 * r, zeta * h_gran2 * r, w

    def createMarginalDistribution(self,key = None):
        if key is None:
            return self.m_marginalDistributions
        else:
            for i in self.m_marginalDistributions:
                if i.getName() == key:
                    return self.m_marginalDistributions[i]

