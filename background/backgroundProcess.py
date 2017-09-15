import logging
import subprocess

from res.strings import *
from settings.settings import Settings
from support.directoryManager import cd


class BackgroundProcess:
    '''
    This class will run DIAMONDS. Dependent on the settings, it will run one or both models (full Background model,
    noise Background model). To be able to run it successfully the prior File has to be set up, as well as the
    results path in background/results/KIC***/. So you need to run all the calculators and filehandlers prior to
    running diamonds. This class also does some rudimentary errorhandling of diamonds. It parses the log provided by
    DIAMONDS to do so.
    '''
    def __init__(self,kicID):
        '''
        The constructor of the Process class. It sets up the binaries that need to be executed, gets various settings
        and sets the proper KicID
        :param kicID: The KicID of the star
        :type kicID: str
        '''
        self._status = {}
        self.logger = logging.getLogger(__name__)
        self.diamondsBinaryPath = Settings.Instance().getSetting(strDiamondsSettings, strSectDiamondsBinaryPath).value
        self.diamondsModel = Settings.Instance().getSetting(strDiamondsSettings, strSectFittingMode).value
        self.diamondsResultsPath = Settings.Instance().getSetting(strDiamondsSettings,strSectBackgroundResPath).value
        self.binaryListToExecute = {}
        self._dummyObject = self._dummyProcessObject()
        self.testErrorMode = "NoError"

        models = {strFitModeFullBackground:(strDiamondsModeFull,strDiamondsExecFull)
            ,strFitModeNoiseBackground:(strDiamondsModeNoise,strDiamondsExecNoise)}

        for fitModel,(runID,binary) in models.items():
            if self.diamondsModel in [fitModel,strFitModeBayesianComparison]:
                self.binaryListToExecute[runID] = binary

        self.kicID = kicID
        return

    def _getFullPath(self,path):
        '''
        This method will create an absolute path if the path it inputs wasn't that already
        :param path: The path you want to have the absolute of
        :type path: str
        :return: Absolute path
        :rtype: str
        '''
        if path[0] not in ["~", "/", "\\"]:
            self.logger.debug("Setting binary to full path")
            self.logger.debug("Prepending"+os.getcwd())
            path = os.getcwd() + "/" + path
            self.logger.debug("New path: "+path)
        else:
            self.logger.debug("Path is already absolute path")

        return path


    def start(self):
        '''
        Runs the processes setup in the constructor. It also creates the proper directories, for each run it will create
        one. Also logs the output of background. Will raise a ValueError if DIAMONDS cannot finish the fitting (too many
        runs). It will also set the status flag properly depending on the state
        '''
        self.logger.debug("Starting background process(es).")
        for runID,binary in self.binaryListToExecute.items():

            self.logger.debug("RunID is : '"+runID+"'")
            self.logger.debug("Binary path: '"+self.diamondsBinaryPath+"'")
            self.logger.debug("Binary used: '"+binary+"'")
            self.logger.debug("KicID: '"+self.kicID+"'")

            path = self._getFullPath(self.diamondsBinaryPath + binary)

            resultsPath = self.diamondsResultsPath + "KIC" + self.kicID + "/" + runID + "/"
            if not os.path.exists(resultsPath):
                self.logger.debug("Directory "+resultsPath+" doesn't exist. Creating...")
                os.makedirs(resultsPath)

            self.logger.debug("Results directory '" + resultsPath + "'")

            cmd = [path,self.kicID,runID]
            self.logger.debug("Full Command: '"+str(cmd)+"'")

            finished = False

            for errorCount in range(1,3):
                self._status[runID] = strDiamondsStatusRunning
                with cd(self.diamondsBinaryPath):
                    p =self._runBinary(cmd)

                    while p.poll() is None:
                        line = p.stderr.readline()
                        self.logger.debug(line)

                        if strDiamondsErrBetterLikelihood in str(line):
                            self.logger.warning("Diamonds cannot find point with better likelihood. Repeat!")
                            self._status[runID] = strDiamondsStatusLikelihood

                        elif strDiamondsErrCovarianceFailed in str(line):
                            self.logger.warning("Diamonds cannot decompose covariance. Repeat!")
                            self._status[runID] = strDiamondsStatusCovariance

                        elif strDiamondsErrAssertionFailed in str(line):
                            self.logger.warning("Diamonds assertion failed. Repeat!")
                            self._status[runID] = strDiamondsStatusAssertion

                    self.logger.debug(p.stderr.read())
                    self.logger.debug("Command '"+str(cmd)+"' done")
                    if self._status[runID] == strDiamondsStatusRunning:
                        finished = True
                        self._status[runID] = strDiamondsStatusGood

            if not finished:
                self.logger.error("Diamonds failed to find good values!")
                raise ValueError

                #Some error handling needs to take place here!
        return

    @property
    def status(self):
        '''
        Property for the status flag on background. See strings.py for possible values
        :return:Status flag
        :rtype:string
        '''
        return self._status

    def _runBinary(self,cmd):
        self._dummyObject._dummyPollCounter = 0
        self._dummyObject.stderr._dummyPollCounter = 0
        p = self._dummyObject

        if bool(Settings.Instance().getSetting(strMiscSettings,strSectRunBinaries).value) is True:
            self.logger.debug("Running binaries is true")
        else:
            self.logger.debug("Running binaries is false")
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p

    class _dummyProcessObject:
        def __init__(self):
            self._dummyPollCounter = 0
            self.stderr = self.out()
            self.stderr.testErrorMode = "NoError"

        def poll(self):
            if self._dummyPollCounter == 10 or self.stderr.testErrorMode != "NoError":
                return "Finished"
            self.stderr._dummyPollCounter = self._dummyPollCounter
            self._dummyPollCounter +=1

        class out:
            def __init__(self):
                self._dummyPollCounter = 0
                self.testErrorMode = "NoError"

            def readline(self):
                if self._dummyPollCounter == 5 and self.testErrorMode != "NoError":
                    return self.testErrorMode
                return "NoError"

            def read(self):
                return("DUMMY OBJECT DONE")

    @property
    def testErrorMode(self):
        return self._dummyObject.stderr.testErrorMode

    @testErrorMode.setter
    def testErrorMode(self,value):
        self._dummyObject.stderr.testErrorMode = value


