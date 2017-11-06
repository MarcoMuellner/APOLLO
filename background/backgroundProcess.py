import logging
import subprocess
import io
from contextlib import redirect_stderr
from pyDiamondsBackground import Background
from pyDiamondsBackground.models import WhiteNoiseOnlyModel,WhiteNoiseOscillationModel,BackgroundModel

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
        self._binaryDictToExecute = {}
        self._dummyObject = self._dummyProcessObject()
        self.testErrorMode = "NoError"

        models = {strFitModeFullBackground:(strDiamondsModeFull,strDiamondsExecFull)
            ,strFitModeNoiseBackground:(strDiamondsModeNoise,strDiamondsExecNoise)}

        for fitModel,(runID,binary) in models.items():
            if self.diamondsModel in [fitModel,strFitModeBayesianComparison]:
                self._binaryDictToExecute[runID] = (binary, True)

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

        for runID,(binary,statusFlag) in self._binaryDictToExecute.items():

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
                if Settings.Instance().getSetting(strDiamondsSettings,strSectDiamondsRunMode).value == strPythonMode:
                    if binary == strDiamondsExecNoise:
                        model = WhiteNoiseOnlyModel
                    elif binary == strDiamondsExecFull:
                        model = WhiteNoiseOscillationModel
                    finished = self._runPyDIAMONDS(runID,model)
                else:
                    finished = self._runDiamondsBinaries(runID,cmd)
                if finished:
                    self._binaryDictToExecute[runID] = (binary, True)
                    break

            if not finished:
                self.logger.error("Diamonds failed to find good values!")
                self._binaryDictToExecute[runID] = (binary, False)

        self.evaluateRun(self._binaryDictToExecute)

    def _checkDiamondsStdOut(self,oldStatus,text):
        """
        Checks the stdout of DIAMONDS and returns the status, that DIAMONDS has.
        :param text: stderr/stdout of diamonds that is analyzed.
        :type text: str
        :return: Statusflag
        :rtype: str
        """
        status = oldStatus
        if strDiamondsErrBetterLikelihood in str(text):
            self.logger.warning("Diamonds cannot find point with better likelihood. Repeat!")
            status = strDiamondsStatusLikelihood

        elif strDiamondsErrCovarianceFailed in str(text):
            self.logger.warning("Diamonds cannot decompose covariance. Repeat!")
            status = strDiamondsStatusCovariance

        elif strDiamondsErrAssertionFailed in str(text):
            self.logger.warning("Diamonds assertion failed. Repeat!")
            status = strDiamondsStatusAssertion
        return status

    def _runPyDIAMONDS(self,runID,model):
        """
        This method runs DIAMONDS via the python bindings and PyDIAMONDS-Background. It also checks if DIAMONDS ran
        correctly. To analyze the result it redericts the whole stdout to a buffer, which than is analyzed
        :param model: The model used in the run
        :type model: BackgroundModel
        :param runID: The runID for the run
        :type runID: str
        """
        finished = False
        rootPath = Settings.Instance().getSetting(strDiamondsSettings,strSectPyDIAMONDSRootPath).value
        self.logger.info("Root path is "+rootPath)
        with io.StringIO() as buf, redirect_stderr(buf):
            bg = Background(kicID=self.kicID,modelObject=model,rootPath=rootPath)
            bg.run()
            bg.writeResults(rootPath,"background_")
            status = self._checkDiamondsStdOut(strDiamondsStatusRunning,buf.getvalue())
            if  status == strDiamondsStatusRunning:
                finished = True
                self._status[runID] = strDiamondsStatusGood
            else:
                self._status[runID] = status

        return finished

    def _runDiamondsBinaries(self,runID,cmd):
        """
        This method runs Diamonds by running the background binary provided in the settings. It also checks if DIAMONDS
        ran correctly. This method sets the proper
        :param runID: runID of the star
        :type runID: str
        :param cmd: command to run
        :type cmd: dict
        :return: Finished flag, indicating if diamonds ran correctly
        :rtype: bool
        """
        finished = False
        with cd(self.diamondsBinaryPath):
            self._status[runID] = strDiamondsStatusRunning
            p = self._runBinary(cmd)

            while p.poll() is None:
                line = p.stderr.readline()
                self.logger.info(line)

                self._status[runID] = self._checkDiamondsStdOut(self._status[runID],line)

            self.logger.debug(p.stderr.read())
            self.logger.info("Command '" + str(cmd) + "' done")
            self.logger.info("Status is "+str(self._status[runID])+"'")
            if self._status[runID] == strDiamondsStatusRunning:
                finished = True
                self._status[runID] = strDiamondsStatusGood

        return finished

    def evaluateRun(self, binaryDict):
        '''
        This method evaluates a run, by checking the status flag for every run. If a statusflag in the dict
        is False, this method raises a ValueError, else it will return True
        :param binaryDict: Binary dict, used for the run. {runID,(binary,statusFlag)}
        :type binaryDict: dict[str,(str,bool)]
        :return: Returns true if run was ok. Else it will raise a ValueError
        :rtype: bool
        '''
        for runID,(_,statusFlag) in binaryDict.items():
            if statusFlag is False:
                self.logger.error("RunID "+runID+" failed the run!")
                raise ValueError("RunID "+runID+" failed the run!")

        return True

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

        if Settings.Instance().getSetting(strMiscSettings,strSectRunBinaries).value == "True":
            self.logger.debug("Running binaries is true")
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            self.logger.debug("Running binaries is false")
        return p

    class _dummyProcessObject:
        def __init__(self):
            self._dummyPollCounter = 0
            self.stderr = self.out()
            self.stderr.testErrorMode = "NoError"

        def poll(self):
            if self._dummyPollCounter == 10:
                return "Finished"
            self.stderr._dummyPollCounter = self._dummyPollCounter
            self._dummyPollCounter +=1
            return None

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


