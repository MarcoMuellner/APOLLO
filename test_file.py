from evaluators.nuMaxEvaluator import NuMaxEvaluator
from readerWriter.inputFileReader import InputFileReader
from evaluators.inputDataEvaluator import InputDataEvaluator
import numpy as np
import logging
from loghandler.loghandler import *


setup_logging()
logger = logging.getLogger(__name__)
logging.getLogger().setLevel(level=logging.DEBUG)

file = InputFileReader("idlFiles/kplr003744681_983_COR_filt_inp.fits")
print(file.lightCurve.T.shape)
np.savetxt("idlFiles/KIC003744681.txt",file.lightCurve.T)
powerCalc = InputDataEvaluator(np.conjugate(file.lightCurve))
powerCalc.kicID = "008196817"
nuMaxCalc = NuMaxEvaluator("008196817", powerCalc.lightCurve)
nuMaxCalc.computeNuMax()