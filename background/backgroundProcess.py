from logging import getLogger
import re
import subprocess
from multiprocessing.pool import ThreadPool,Pool
from itertools import product

from res.strings import *
from support.directoryManager import cd
import time
from res.conf_file_str import general_background_result_path,general_binary_path,general_kic,internal_noise_value,general_prior_mode
from support.printer import print_int

class BackgroundProcess:
    """
    Background Process allows for concurrent runs of diamonds for both modes. Use run() to get it started
    """

    def __init__(self,kwargs):
        if internal_noise_value not in kwargs:
            self.kicID = str(kwargs[general_kic])
        else:
            self.kicID = str(kwargs[general_kic]) + f"_{kwargs[internal_noise_value]}"
        self.binaryPath = kwargs[general_binary_path]
        self.model = strRunIDBoth
        self.kwargs = kwargs

        self.resultsPath = kwargs[general_background_result_path]

        self.modes = {strDiModeFull: strDiIntModeFull
            ,strDiModeNoise :  strDiIntModeNoise}

        self.status = {}
        self.priorChanges = {}
        self.run_count = {}

    def _getFullPath(self,path):
        '''
        This method will create an absolute path if the path it inputs wasn't that already
        :param path: The path you want to have the absolute of
        :type path: str
        :return: Absolute path
        :rtype: str
        '''
        if path[0] not in ["~", "/", "\\"]:
            path = os.getcwd() + "/" + path

        return path

    def _getCommandStrings(self):
        cmdStrings = {}
        self.check_paths = {}
        for runID,diIntMode in self.modes.items():
            if self.model not in [runID, strRunIDBoth]:
                print_int(f"Skipping {runID}",self.kwargs)
                continue

            self.priorChanges[runID] = {}

            binPath = self._getFullPath(self.binaryPath + strDiBinary)
            runResPath = f"{self.resultsPath}KIC{self.kicID}/{runID}/"

            if general_prior_mode in self.kwargs.keys():
                prior_mode = self.kwargs[general_prior_mode]
            else:
                prior_mode = "uniform"

            if not os.path.exists(runResPath):
                print_int(f"Directory {runResPath} does not exist. Creating ...",self.kwargs)
                os.makedirs(runResPath)

            self.check_paths[runID] = runResPath

            print_int(f"{runID}: Results path {runResPath}",self.kwargs)
            cmdStrings[runID] = [binPath,self.kicID,runID,diIntMode,prior_modecd ..]
            print_int(f"{runID}: Command --> {cmdStrings[runID]}",self.kwargs)

        return cmdStrings

    def run(self):
        cmdStrings = self._getCommandStrings()
        pList = []

        """
        if general_sequential_run in self.kwargs.keys() and self.kwargs[general_sequential_run]:
            pool = Pool(processes =2)
        else:
            pool = ThreadPool(processes=2)

        pool.starmap(self._runCmd, cmdStrings.items())
        """

        for key,value in cmdStrings.items():
            self._runCmd(key,value)



    def _runBinary(self,cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p

    def _runCmd(self,runID, cmd):
        for runCounter in range(1,11):
            self.run_count[runID] = runCounter
            print_int(f"Starting {runID}:no {runCounter}",self.kwargs)
            with cd(self.binaryPath):
                self.status[runID] = strDiStatRunning
                p = self._runBinary(cmd)

                logCounter = 0
                r = re.compile(r"(Nit:\s\d+).+(Ratio: [\w\d\.\+]+)")
                time.sleep(5)
                total=""
                while p.poll() is None:
                    line = p.stderr.readline().decode("utf-8")
                    total += line
                    logCounter = self._logRatio(runID,line,logCounter,r,runCounter)
                    self.status[runID] = self._checkDiamondsStdOut(self.status[runID], line)
                    logCounter +=1
                line = p.stderr.read().decode("utf-8")
                total += line
                self._logRatio(runID,line,10,r,runCounter)

                self.status[runID] = self._checkDiamondsStdOut(self.status[runID], line)
                time.sleep(1)
                self.status[runID] = self._checkIfAllFilesExist(runID,self.status[runID])

                if self.status[runID] == strDiStatRunning:
                    self.status[runID] = strDiamondsStatusGood
                    print_int(f"{runID}: Finished!",self.kwargs)
                    return

                else:
                    print_int(f"{runID}: Run {runCounter} --> Repeating run, due to failure due to {self.status[runID]}",self.kwargs)

        raise ValueError(f"{runID}: FAILED! Tried 10 runs, failed to find result",self.kwargs)



    def _logRatio(self,runID,line,counter,r,runCounter):
        match = r.findall(line)
        if len(match) > 0 and counter >= 10:
            for it,ratio in match:
                print_int(f"{runID} : no {runCounter}  --> {it},{ratio}",self.kwargs)

            counter = 0
        elif len(match) == 0 and counter >= 10:
            print_int(f"{runID} : no {runCounter} --> {line}",self.kwargs)
            counter = 0
        return counter

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
            print_int("Diamonds cannot find point with better likelihood. Repeat!",self.kwargs)
            status = strDiamondsStatusLikelihood

        elif strDiamondsErrCovarianceFailed in str(text):
            print_int("Diamonds cannot decompose covariance. Repeat!",self.kwargs)
            status = strDiamondsStatusCovariance

        elif strDiamondsErrAssertionFailed in str(text):
            print_int("Diamonds assertion failed. Repeat!",self.kwargs)
            status = strDiamondsStatusAssertion

        elif strDiamondsErrMatrixCompositionFailed in str(text):
            print_int("Diamonds matrix decomposition failed. Repeat!",self.kwargs)
            status = strDiamondsStatusMatrixDecomp
        elif strDiamondsErrCoreDumped in str(text):
            print_int("Diamonds matrix decomposition failed. Repeat!",self.kwargs)
            status = strDiamondsStatusMatrixDecomp
        elif strDiamondsErrAborted in str(text):
            print_int("Diamonds matrix decomposition failed. Repeat!",self.kwargs)
            status = strDiamondsStatusMatrixDecomp
        elif strDiamondsErrQuitting in str(text):
            print_int("Diamonds matrix decomposition failed. Repeat!",self.kwargs)
            status = strDiamondsStatusMatrixDecomp
        elif strDiamondsErrSegmentation in str(text):
            print_int("Diamonds matrix decomposition failed. Repeat!",self.kwargs)
            status = strDiamondsStatusMatrixDecomp
        return status

    def _checkIfAllFilesExist(self,runID,oldStatus):
        content = os.listdir(self.check_paths[runID])
        if "background_evidenceInformation.txt" not in content:
            print_int(f"Cant fine evidence in {self.check_paths[runID]}. Repeat!",self.kwargs)
            return strDiamondsStatusAssertion
        elif "background_parameterSummary.txt" not in content:
            print_int(f"Cant fine summary in {self.check_paths[runID]}. Repeat!",self.kwargs)
            return strDiamondsStatusAssertion

        return oldStatus




