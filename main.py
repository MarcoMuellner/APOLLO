from loghandler import loghandler
from filehandler.Diamonds.diamondsResultsFile import Results
from plotter.plotFunctions import *


loghandler.setup_logging()

result = Results('002436458','00')
#plotPSD(result,True,False)
plotMarginalDistributions(result)

show()




