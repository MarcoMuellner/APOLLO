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
import pylab as pl
from scipy import signal
import traceback
import sys

setup_logging()
logger = logging.getLogger(__name__)

def _calculateAutocorrelation(oscillatingData):
    '''
    The numpy variant of computing the autocorrelation. See the documentation of the numpy function for more
    information
    :type oscillatingData: 1-D numpy array
    :rtype: 1-D numpy array
    :param oscillatingData:The data that should be correlated (in our case the y function)
    :return: The correlation of oscillatingData
    '''
    corrs2 = np.correlate(oscillatingData, oscillatingData, mode='same')
    N = len(corrs2)
    corrs2 = corrs2[N // 2:]
    lengths = range(N, N // 2, -1)
    corrs2 /= lengths
    corrs2 /= corrs2[0]
    maxcorr = np.argmax(corrs2)
    corrs2 = corrs2 / corrs2[maxcorr]
    return corrs2

def autocorrelation(x):
    result = np.correlate(x, x, mode='full')
    return result[int(result.size/2):]


def _iterativeFit(data,tau,ax):
    minima = argrelextrema(data[1], np.less)[0][0]
    counter = 0
    minimaFactor = int(30 * np.exp(-minima / 3) + minima)  # kinda arbitrary, just need enough points
    y = data[1][counter:minimaFactor]
    x = data[0][counter:minimaFactor] - data[0][0]
    plotX = np.linspace(0, max(x), num=max(x) * 5)

    x = x[int(np.where(y == max(y))[0]):]
    y = y[int(np.where(y ==max(y))[0]):]


    p0SincOne = [1,tau]
    bounds = (
        [0,0],[1,np.inf]
    )

    sincPopt, pcov = optimize.curve_fit(sinc, x, y,p0=p0SincOne,bounds=bounds)

    residuals = y-sinc(x,*sincPopt)

    p0 = [max(residuals),sincPopt[1]*4]

    sinPopt,pcov = optimize.curve_fit(sin,x,residuals,p0=p0)

    sinResiduals = y - sin(x,*sinPopt)

    p0 = [1,sincPopt[1]]

    lastSincPopt,pcov = optimize.curve_fit(sinc,x,sinResiduals,p0=p0,bounds=bounds)

    ax.set_title(f"Filterfrequency {computeFinalFrequency(tau)}")
    ax.plot(x, y, 'o')
    ax.plot(plotX,sinc(plotX,*lastSincPopt))
    ax.axvline(x=np.abs(lastSincPopt[1]), color='r')
    ax.axvline(x=np.abs(lastSincPopt[1] / 4), color='g')

    return lastSincPopt[1]

def computeFilterFrequency(tau):
    log_y = 3.098 -0.932*np.log10(tau) - 0.025*(np.log10(tau))**2
    return 10 ** log_y

def computeFinalFrequency(tau):
    return 10 ** 6 / (tau * 60)
def computeTau(f):
    return 1428.19/f**(500/491)

def _iterativeFilter(inputReader : InputDataEvaluator, filterFrequency : float, lightCurve :  np.ndarray, t_step : float, elements,ax):
    tau = 10**6/filterFrequency
    normalizedBinSize = int(np.round(tau / t_step))
    filteredLightCurve = lightCurve[1] - trismooth(lightCurve[1],normalizedBinSize)

    corr = np.correlate(filteredLightCurve,filteredLightCurve,mode='full')
    corr = corr[corr.size//2:]
    corr /=max(corr)
    corr = corr**2

    data = _iterativeFit(np.array((lightCurve[0][1:]/60,corr[1:])),tau/60,ax)
    return data



def debugRun(kic,filePath):
    resInst = ResultsWriter.getInstance(i)

    runner = StandardRunner(kic,filePath)
    runner.resInst = resInst
    filePath = runner._lookForFile(kic,filePath)
    fileObj = runner._readAndConvertLightCurve(filePath)

    nuMaxObj = NuMaxEvaluator(kic,fileObj.lightCurve)

    logger.info(f"Initial filter {nuMaxObj._init_nu_filter}")
    fig,axes = pl.subplots(2,2,figsize=(20,10))
    fig.suptitle(f"KIC {kic}")



    tau_1 = _iterativeFilter(fileObj,nuMaxObj._init_nu_filter,nuMaxObj.lightCurve,nuMaxObj.t_step,nuMaxObj.elements,axes[0,0])
    filter_1 = computeFilterFrequency(tau_1)
    logger.info(f"Second filter {filter_1} with tau {tau_1}")
    tau_2 = _iterativeFilter(fileObj, filter_1, nuMaxObj.lightCurve, nuMaxObj.t_step,nuMaxObj.elements,axes[0,1])
    filter_2 = computeFilterFrequency(tau_2)
    logger.info(f"Third filter {filter_2} with tau {tau_2}")
    tau_3 = _iterativeFilter(fileObj, filter_2, nuMaxObj.lightCurve, nuMaxObj.t_step, nuMaxObj.elements, axes[1, 1])
    final_mu = computeFinalFrequency(tau_3)
    logger.info(f"Final mu {final_mu} with tau {tau_3}")

    axes[1,0].set_title(f"Normal PSD")
    axes[1, 0].loglog(fileObj.powerSpectralDensity[0], fileObj.powerSpectralDensity[1], label='Data', color='black')
    axes[1, 0].axvline(x=nuMaxObj._init_nu_filter,color='r',label='init')
    axes[1, 0].axvline(x=filter_1, color='g',label='first')
    axes[1, 0].axvline(x=filter_2, color='c',label='second')
    axes[1, 0].axvline(x=final_mu, color='b',label='final')
    axes[1, 0].legend()
    fig.savefig(f"debugResults/KIC{kic}.png",dpi=fig.dpi)
    #pl.show()


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
    try:
        debugRun(i,filePath)
    except:
        pass

    logger.info("************************************")
    logger.info("Debug Run " + i +" FINISHED")
    logger.info("************************************")