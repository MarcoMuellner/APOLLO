import argparse
import numpy as np
from loghandler.loghandler import *
from res.strings import *
from settings.settings import Settings
from runner.StandardRunner import StandardRunner
from evaluators.nuMaxEvaluator import NuMaxEvaluator
from fitter.fitFunctions import *
from scipy.signal import argrelextrema
from readerWriter.resultsWriter import ResultsWriter
from evaluators.inputDataEvaluator import InputDataEvaluator
from readerWriter.inputFileReader import InputFileReader
import pylab as pl

setup_logging()
logger = logging.getLogger(__name__)


def _readAndConvertLightCurve(kicID,filename):
    '''
    This method will take the fileName, check if it exists and than read it using the FitsReader class. The read
    file will than be pushed into the PowerSpectraCalculator class, where it will be converted into a PSD
    :param filename: Complete filename of the lightCurve
    :type filename: str
    :return: The Powerspectraobject containing the lightcurve and psd
    :rtype: InputDataEvaluator
    '''
    file = InputFileReader(filename, kicID)

    originalData = file._readData(filename).T
    gapsX = originalData[0]
    gapsY = originalData[1]
    gapList = [(3000,10000),
               (15000,20000),
               (25000, 26000),
               (30000,39000),
               (45000, 52000),]
    gapList = []

    for low,up in gapList:
        gapsX = np.delete(gapsX,np.s_[low:up])
        gapsY = np.delete(gapsY, np.s_[low:up])

    rawData = np.array((gapsX,gapsY)).T

    combinigData = file._refineDataCombiningMethod(rawData)
    cuttingData = file._refineDataCuttingMethod(rawData)
    interpolatingData = file._refineDataInterpolation(rawData)
    fullData = originalData

    returnValue = [
        ("Original data", file._removeStray(fullData[0],fullData[1])),
        ("Combining method",file._removeStray(combinigData[0],combinigData[1])),
        ("Cutting method",file._removeStray(cuttingData[0],cuttingData[1])),
        ("Interpolation method",file._removeStray(interpolatingData[0],interpolatingData[1]))
    ]

    return returnValue

def debugRun(kic,filePath):
    resInst = ResultsWriter.getInstance(i)

    runner = StandardRunner(kic,filePath)
    runner.resInst = resInst
    filePath = runner._lookForFile(kic,filePath)
    lightCurves = _readAndConvertLightCurve(kic,filePath)
    fig, axes = pl.subplots(2, len(lightCurves), figsize=(10, 5))
    fig.suptitle(f"KIC{kic}")

    n = 0
    for name,data in lightCurves:
        powerCalc = InputDataEvaluator(np.conjugate(data))
        powerCalc.kicID = kic
        nuMaxObj = NuMaxEvaluator(kic, data)
        nu_final = nuMaxObj.computeNuMax()
        axes[0, n].set_title(name)
        axes[0, n].plot(data[0]/3600/24,data[1],'o',color='k', markersize=1)
        axes[0, n].set_xlabel(r"Time (days)")
        if n == 0:
            axes[0, n].set_ylabel(r"Flux")
        axes[1, n].loglog(powerCalc.powerSpectralDensity[0],powerCalc.powerSpectralDensity[1],color='k', markersize=4)
        f = nuMaxObj._init_nu_filter
        text = r"$%.2f\mu$Hz" % round(f, 2)

        text_nu_final = r"$%.2f\mu$Hz" % round(nu_final, 2)
        axes[1, n].axvline(x=f,ls='dashed',color='k')
        axes[1, n].axvline(x=nu_final, ls='dotted', color='k')
        axes[1, n].text(f+0.5, 7*10**5, text, rotation=90,fontsize=6)
        axes[1, n].text(nu_final+0.5, 7 * 10 ** 5, text_nu_final, rotation=90, fontsize=6)
        axes[1, n].set_ylim(10**-4,3*10**6)
        axes[1, n].set_xlabel(r"Frequency ($\mu$Hz)")
        if n == 0:
            axes[1, n].set_ylabel(r"PSD ($ppm^2/\mu$Hz)")

        n=n+1

    pl.show()



    #nuMaxObj = NuMaxEvaluator(kic,fileObj.lightCurve)


    ResultsWriter.removeInstance(i)

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

for i in kicList:
    logger.info("************************************")
    logger.info("Debug Run " + i)
    logger.info("************************************")
    debugRun(i,filePath)

    logger.info("************************************")
    logger.info("Debug Run " + i +" FINISHED")
    logger.info("************************************")