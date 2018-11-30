from logging import getLogger
import re
import subprocess
from multiprocessing import Process

from res.strings import *
from support.directoryManager import cd
import time
from res.conf_file_str import general_background_result_path,general_binary_path,general_kic
from support.printer import print_int

class BackgroundProcess:
    """
    Background Process allows for concurrent runs of diamonds for both modes. Use run() to get it started
    """

    def __init__(self,kwargs):
        self.kicID = kwargs[general_kic]
        self.binaryPath = kwargs[general_binary_path]
        self.model = strRunIDBoth
        self.kwargs = kwargs

        self.resultsPath = kwargs[general_background_result_path]

        self.modes = {strDiModeFull: strDiIntModeFull
            ,strDiModeNoise :  strDiIntModeNoise}

        self.status = {}
        self.priorChanges = {}

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
        for runID,diIntMode in self.modes.items():
            if self.model not in [runID, strRunIDBoth]:
                print_int(f"Skipping {runID}",self.kwargs)
                continue

            self.priorChanges[runID] = {}

            binPath = self._getFullPath(self.binaryPath + strDiBinary)
            runResPath = f"{self.resultsPath}KIC{self.kicID}/{runID}/"
            if not os.path.exists(runResPath):
                print_int(f"Directory {runResPath} does not exist. Creating ...",self.kwargs)
                os.makedirs(runResPath)

            print_int(f"{runID}: Results path {runResPath}",self.kwargs)
            cmdStrings[runID] = [binPath,self.kicID,runID,diIntMode]
            print_int(f"{runID}: Command --> {cmdStrings[runID]}",self.kwargs)

        return cmdStrings

    def run(self):
        cmdStrings = self._getCommandStrings()
        pList = []
        for runID,cmd in cmdStrings.items():
            p = Process(target=self._runCmd,args =(runID,cmd,))
            p.start()
            pList.append(p)

        for i in pList:
            i.join()



    def _runBinary(self,cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p

    def _runCmd(self,runID, cmd):
        for runCounter in range(1,6):
            print_int(f"Starting {runID}:no {runCounter}",self.kwargs)
            with cd(self.binaryPath):
                self.status[runID] = strDiStatRunning
                p = self._runBinary(cmd)

                logCounter = 0
                r = re.compile(r"(Nit:\s\d+).+(Ratio: [\w\d\.\+]+)")
                time.sleep(5)
                while p.poll() is None:
                    line = p.stderr.readline().decode("utf-8")
                    logCounter = self._logRatio(runID,line,logCounter,r)
                    self.status[runID] = self._checkDiamondsStdOut(self.status[runID], line)
                    logCounter +=1
                line = p.stderr.read().decode("utf-8")
                self._logRatio(runID,line,10,r)

                self.status[runID] = self._checkDiamondsStdOut(self.status[runID], line)
                if self.status[runID] == strDiStatRunning:
                    self.status[runID] = strDiamondsStatusGood
                    print_int(f"{runID}: Finished!",self.kwargs)
                    return True

                else:
                    print_int(f"{runID}: Run {runCounter} --> Repeating run, due to failure due to {self.status[runID]}",self.kwargs)

        print_int(f"{runID}: FAILED! Tried 5 runs, failed to find result",self.kwargs)
        return False



    def _logRatio(self,runID,line,counter,r):
        match = r.findall(line)
        if len(match) > 0 and counter >= 10:
            for it,ratio in match:
                print(f"{runID} --> {it},{ratio}")

            counter = 0
        elif len(match) == 0 and counter >= 10:
            print(f"{line}")
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
        return status
