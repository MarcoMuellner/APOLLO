from runner.StandardRunner import StandardRunner
from readerWriter.inputFileReader import InputFileReader
from evaluators.inputDataEvaluator import InputDataEvaluator
from runner.StandardRunner import StandardRunner
from plotter.plotFunctions import *
from loghandler.loghandler import setup_logging
from uncertainties import ufloat_fromstr
import argparse
from os import mkdir
from json import dump

setup_logging()
logger = logging.getLogger(__name__)

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

def computeWeights(x):
    run = 10**(100*x/x[len(x)-1])
    return run/max(run)

def run(kic,filePath):
    resInst = ResultsWriter.getInstance(kic)
    obj = StandardRunner(kic,filePath)
    obj.resInst = resInst
    filePath = obj._lookForFile(kic,filePath)
    psd = obj._readAndConvertLightCurve(filePath)
    pl.figure()
    pl.loglog(psd.powerSpectralDensity[0],psd.powerSpectralDensity[1],color='k')
    weight = computeWeights(psd.powerSpectralDensity[0])
    #pl.loglog(psd.powerSpectralDensity[0],weight,color='grey')
    mean = np.average(psd.powerSpectralDensity[1],weights=weight)
    pl.axhline(y=mean/10, ls="dotted", color="r")
    pl.axhline(y=mean,ls="dashed",color="r",label=f'New photon noise {mean}')
    pl.axhline(y=mean*10, ls="dotted", color="r")
    pl.axhline(y=psd.photonNoise,color='g',ls="dashed",label=f'Old photon noise {psd.photonNoise}')
    pl.axhline(y=psd.photonNoise/4, color='g', ls="dotted")
    pl.axhline(y=psd.photonNoise*4, color='g', ls="dotted")
    pl.legend()
    pl.show()
    ResultsWriter.removeInstance(kic)




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
    fitMode = strRunIDFull
elif args.mode == "NO":
    fitMode = strRunIDNoise
elif args.mode == "BC":
    fitMode = strRunIDBoth

logger.info("Mode is " + fitMode)
Settings.ins().getSetting(strDiamondsSettings,strSectFittingMode).value = fitMode
starMode = ""

if args.starType == "RG":
    starMode = strStarTypeRedGiant
elif args.starType == "YS":
    starMode = strStarTypeYoungStar
    Settings.ins().getSetting(strDataSettings, strSectDataRefinement).value = strRefineStray
else:
    raise IOError("Startype must be either YS or RG")

Settings.ins().getSetting(strDataSettings,strSectStarType).value = starMode

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



