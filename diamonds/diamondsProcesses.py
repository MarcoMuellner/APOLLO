import logging
import subprocess

from plotter.fileAnimator import FileAnimator
from settings.settings import Settings
from support.directoryManager import cd
from support.strings import *


class DiamondsProcess:
    """
    This class will run DIAMONDS. Dependent on the settings, it will run one or both models (full Background model,
    noise Background model). To be able to run it successfully the prior File has to be set up, as well as the
    results path in background/results/KIC***/. So you need to run all the calculators and filehandlers prior to
    running diamonds. This class also does some rudimentary errorhandling of diamonds. It parses the log provided by
    DIAMONDS to do so.
    """
    def __init__(self,kicID):
        """
        The constructor of the Process class. It sets up the binaries that need to be executed, gets various settings
        and sets the proper KICId
        :param kicID: The KICId of the star
        :type kicID: string
        """
        self._status = {}
        self.logger = logging.getLogger(__name__)
        self.diamondsBinaryPath = Settings.Instance().getSetting(strDiamondsSettings, strSectDiamondsBinaryPath).value
        self.diamondsModel = Settings.Instance().getSetting(strDiamondsSettings, strSectFittingMode).value
        self.diamondsResultsPath = Settings.Instance().getSetting(strDiamondsSettings,strSectBackgroundResPath).value
        self.binaryListToExecute = {}

        if self.diamondsModel in [strFitModeFullBackground,strFitModeBayesianComparison]:
            self.binaryListToExecute[strDiamondsModeFull]=(strDiamondsExecFull)

        if self.diamondsModel in [strFitModeNoiseBackground,strFitModeBayesianComparison]:
            self.binaryListToExecute[strDiamondsModeNoise]=(strDiamondsExecNoise)

        self.kicID = kicID
        return

    def start(self):
        """
        Runs the processes setup in the constructor. It also creates the proper directories, for each run it will create
        one. Also logs the output of diamonds. Will raise a ValueError if DIAMONDS cannot finish the fitting.
        """
        self.logger.debug("Starting diamonds process(es).")
        for i in self.binaryListToExecute.keys():
            resultsPath = self.diamondsResultsPath+"KIC"+self.kicID+"/"+i+"/"
            self.logger.debug("Mode is : '"+i+"'")
            self.logger.debug("Binary path: '"+self.diamondsBinaryPath+"'")
            self.logger.debug("Binary used: '"+self.binaryListToExecute[i]+"'")
            self.logger.debug("KicID: '"+self.kicID+"'")

            cmd = [(self.diamondsBinaryPath + self.binaryListToExecute[i]),self.kicID,i]
            self.logger.debug("Full Command: '"+str(cmd)+"'")
            self.logger.debug("Results directory '"+resultsPath+"'")


            if not os.path.exists(resultsPath):
                self.logger.debug("Directory "+resultsPath+" doesn't exist. Creating...")
                os.makedirs(resultsPath)

            finished = False
            errorCount = 0

            mode = strDiamondsModeNoise if i == strDiamondsModeNoise else strDiamondsModeFull

            while finished == False:
                errorCount +=1
                self._status[mode] = strDiamondsStatusRunning
                with cd(self.diamondsBinaryPath):
                    p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    while p.poll() is None:
                        line = p.stderr.readline()
                        self.logger.debug(line)
                        if strDiamondsErrBetterLikelihood in str(line):
                            self.logger.warning("Diamonds cannot find point with better likelihood. Repeat!")
                            self._status[mode] = strDiamondsStatusLikelihood
                        elif strDiamondsErrCovarianceFailed in str(line):
                            self.logger.warning("Diamonds cannot decompose covariance. Repeat!")
                            self._status[mode] = strDiamondsStatusCovariance
                        elif strDiamondsErrAssertionFailed in str(line):
                            self.logger.warning("Diamonds assertion failed. Repeat!")
                            self._status[mode] = strDiamondsStatusAssertion

                    self.logger.debug(p.stdout.read())
                    self.logger.debug("Command '"+str(cmd)+"' done")
                    if self._status[mode] == strDiamondsStatusRunning:
                        finished = True
                        self._status[mode] = strDiamondsStatusGood
                    elif errorCount >3:
                        self.logger.error("Diamonds failed to find good values!")
                        raise ValueError

                #Some error handling needs to take place here!
        return

    @property
    def status(self):
        """
        Property for the status flag on diamonds. See strings.py for possible values
        :return:Status flag
        :rtype:string
        """
        return self._status


