from filehandler.Diamonds.InternalStructure.backgroundParameterSummaryFile import ParameterSummary
from filehandler.Diamonds.InternalStructure.backgroundEvidenceInformationFile import Evidence
from filehandler.Diamonds.InternalStructure.backgroundParameterFile import BackgroundParameter
from filehandler.Diamonds.InternalStructure.backgroundMarginalDistributionFile import MarginalDistribution
from filehandler.Diamonds.diamondsPriorsFile import Priors
from filehandler.Diamonds.dataFile import DataFile
import glob
from settings.settings import Settings
import numpy as np

class Results:
    m_summary = None
    m_evidence = None
    m_backgroundParameter = {}
    m_marginalDistributions = {}
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
        self.m_dataFolder = Settings.Instance().getSetting("Files", "dataFolder")
        nyqFile = glob.glob(self.m_dataFolder + 'KIC*{}*/NyquistFrequency.txt'.format(kicID))[0]
        self.m_nyq = np.loadtxt(nyqFile)

        self.m_names = ['w', '$\sigma_\mathrm{long}$', '$b_\mathrm{long}$','$\sigma_\mathrm{gran,1}$',
                  '$b_\mathrm{gran,1}$', '$\sigma_\mathrm{gran,2}$', '$b_\mathrm{gran,2}$']

        self.m_units = ['ppm$^2$/$\mu$Hz', 'ppm', '$\mu$Hz','ppm','$\mu$Hz', 'ppm', '$\mu$Hz']

        for i in range(0,9):
            self.m_backgroundParameter[self.m_names[i]] = BackgroundParameter(self.m_names[i],self.m_units[i],kicID,runID,i)
            self.m_marginalDistributions[self.m_names[i]] = MarginalDistribution(self.m_names[i], self.m_units[i], kicID, runID, i)

    def getBackgroundParameters(self,key = None):
        if key is None:
            return self.m_backgroundParameter
        else:
            if key in self.m_backgroundParameter.keys():
                return self.m_backgroundParameter[key]
            else:
                return self.m_backgroundParameter

    def getMarginalDistributions(self,key = None):
        if key is None:
            return self.m_marginalDistributions
        else:
            if key in self.m_marginalDistributions.keys():
                return self.m_marginalDistributions[key]
            else:
                return self.m_marginalDistributions

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


    def createBackgroundModel(self, runGauss):
        freq, psd = self.m_dataFile.getPSD()
        par_median = self.m_backgroundParameter[1].getData()
        par_le = self.m_backgroundParameter[4].getData()
        par_ue = self.m_backgroundParameter[5].getData()
        if runGauss:
            hg = par_median[
                7]  # third last parameter TODO these Parameters need to be added when plotting with gaussian
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