from runner.StandardRunner import StandardRunner
from readerWriter.inputFileReader import InputFileReader
from evaluators.inputDataEvaluator import InputDataEvaluator
from plotter.plotFunctions import *
from loghandler.loghandler import setup_logging
from uncertainties import ufloat_fromstr
import argparse
from os import mkdir
from json import dump

setup_logging()
logger = logging.getLogger(__name__)

class NoiseRunner(StandardRunner):
    def __init__(self,kic,fileName,noiseLevel):
        self.noiseLevel = noiseLevel
        StandardRunner.__init__(self,kic,filePath=fileName)

    def _readAndConvertLightCurve(self, filename):
        '''
        This method will take the fileName, check if it exists and than read it using the FitsReader class. The read
        file will than be pushed into the PowerSpectraCalculator class, where it will be converted into a PSD
        :param filename: Complete filename of the lightCurve
        :type filename: str
        :return: The Powerspectraobject containing the lightcurve and psd
        :rtype: InputDataEvaluator
        '''
        file = InputFileReader(filename, self.kicID)

        noise = np.random.normal(0, 1, file.lightCurve[1].size)
        file.lightCurve[1] = file.lightCurve[1] + self.noiseLevel*max(file.lightCurve[1])*noise/5

        powerCalc = InputDataEvaluator(np.conjugate(file.lightCurve))
        powerCalc.kicID = self.kicID

        try:
            self.resInst.powerSpectraCalculator = powerCalc
        except:
            pass

        plotLightCurve(powerCalc, 2, fileName="Lightcurve.png")
        plotPSD(powerCalc, True, visibilityLevel=2, fileName="PSD.png")

        return powerCalc


def run(kic,filePath):
    resInst = ResultsWriter.getInstance(kic)
    pl.figure()
    pl.title(f"KIC{kic}")
    pl.xlabel("Noise level")
    pl.ylabel("Bayes factor")
    noiseValues = []
    try:
        mkdir(f"noiseResults/KIC{kic}/")
    except FileExistsError:
        pass

    for i in range(0,5):
        try:
            obj = NoiseRunner(kic,filePath,i)
            result,lc,psd = obj._internalRun()
            bayes = ufloat_fromstr(result[strAnalyzerResSectAnalysis][strAnalyzerResValBayes])
            with open(f"noiseResults/KIC{kic}/results_noise_{i}.json", 'w') as f:
                dump(result, f)
            np.savetxt(f"noiseResults/KIC{kic}/Lightcurve_n_{i}.txt", lc, header="Time(days) Flux")
            np.savetxt(f"noiseResults/KIC{kic}/PSD_n_{i}.txt", psd, header="Frequency(uHz) PSD(ppm^2/uHz)")
            noiseValues.append((i,bayes))
            pl.plot(i,bayes.nominal_value)
        except:
            logger.error(f"Failed {kic} for noise runner {i}")
            pass

    pl.show()
    ResultsWriter.removeInstance(kic)


parser = argparse.ArgumentParser()
parser.add_argument("kicFolder",help="The folder where the KIC files are stored.",type=str)
parser.add_argument("kicID",help="The KicIDs that should be processed. Split the IDs with a ','. You can also provide "
                                 "a file containig the KICs. Has to end with txt and every KicID has to be in its "
                                 "own line",type=str)
parser.add_argument("-m","--mode",help="The DIAMONDS modes that should be applied. Modes available: "
                                       "FullBackground -> only (F)ull(B)ackground,(N)oise(O)nly -> only Noise model,"
                                       "(B)ayesian(C)omparison -> both and comparison. BC is default"
                                        ,type=str,choices=["FB","NO","BC"],default="BC")
parser.add_argument("-t","--starType",help="The star type that should be processed. Specify with RG (red giant) or "
                                           "YS(young star). Default is red giant",
                                            type=str,choices=["RG","YS"],default="RG")
parser.add_argument("-v","--verbose",help="If this is true, more logging is printed to stdout. Default "
                                          "is False",action="store_true",default=False)

args = parser.parse_args()



filePath = args.kicFolder
if not os.path.exists(filePath):
    logger.error("Filepath "+filePath+" does not exist")
    raise IOError("Filepath "+filePath+" does not exist")

filePath = os.path.abspath(filePath) + "/"
logger.info("Filepath of Kic Files is "+filePath)

kicList = []

if '.txt' in args.kicID:
    logger.info("Provided a file of KIC IDs")
    if not os.path.exists(args.kicID):
        logger.error("File "+args.kicID+" does not exist!")
        raise IOError("File "+args.kicID+" does not exist!")

    kicList = np.genfromtxt(args.kicID,dtype='str')
elif ',' in args.kicID:
    kicList = args.kicID.split(",")
else:
    kicList.append(args.kicID)

logger.info("kicList is "+str(kicList))

fitMode = ""

if args.mode == "FB":
    fitMode = strFitModeFullBackground
elif args.mode == "NO":
    fitMode = strFitModeNoiseBackground
elif args.mode == "BC":
    fitMode = strFitModeBayesianComparison

logger.info("Mode is " + fitMode)
Settings.Instance().getSetting(strDiamondsSettings,strSectFittingMode).value = fitMode
starMode = ""

if args.starType == "RG":
    starMode = strStarTypeRedGiant
elif args.starType == "YS":
    starMode = strStarTypeYoungStar
    Settings.Instance().getSetting(strDataSettings, strSectDataRefinement).value = strRefineStray
else:
    raise IOError("Startype must be either YS or RG")

Settings.Instance().getSetting(strDataSettings,strSectStarType).value = starMode

if args.verbose:
    logging.getLogger().setLevel(level=logging.DEBUG)
else:
    logging.getLogger().setLevel(level=logging.INFO)

try:
    mkdir("noiseResults/")
except FileExistsError:
    pass
for i in kicList:
    logger.info("************************************")
    logger.info("Debug Run " + i)
    logger.info("************************************")
    run(i,filePath)

    logger.info("************************************")
    logger.info("Debug Run " + i +" FINISHED")
    logger.info("************************************")



