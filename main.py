import argparse
import numpy as np
from loghandler.loghandler import *
from res.strings import *
from settings.settings import Settings
from runner.StandardRunner import StandardRunner
import traceback

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

setup_logging()
logger = logging.getLogger(__name__)

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

for i in kicList:
    logger.info("************************************")
    logger.info("STARTING STAR " + i)
    logger.info("************************************")
    runner = StandardRunner(i,filePath)
    try:
        runner._internalRun()

    except Exception as e:
        trace = traceback.format_exc()
        logger.warning("Run for "+i +"failed")
        logger.warning(str(e.__class__.__name__) +":"+ str(e))
        logger.warning(trace[:1023])
        continue

    logger.info("************************************")
    logger.info("STAR " + i +" FINISHED")
    logger.info("************************************")