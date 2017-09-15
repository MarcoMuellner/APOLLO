from runner.StandardRunner import StandardRunner
import logging
from loghandler.loghandler import *

starList = []
starList.append("004770846_1435") #works
starList.append("003744681_983") #works
starList.append("004448777_771") #works
starList.append("004659821_1181") #okayish
starList.append("004770846_1435") #okayish
starList.append("005184199_539") #works
starList.append("005356201_979") #failed
starList.append("005858947_2366") #not perfect, nuMax is a bit off
starList.append("006144777_350") #works
starList.append("007467630_1088") #perfect
starList.append("007581399_1298") #nuMax and Hosc to high
starList.append("008366239_1241") #okayish
starList.append("008962923_2846")
starList.append("009267654_634")
starList.append("009332840_813")
starList.append("009346602_873")
starList.append("009574650_1445")
starList.append("009882316_2399")
starList.append("010777816_1965")
starList.append("010866415_2167")
starList.append("011550492_1262")
starList.append("012008916_19")

setup_logging()
logger = logging.getLogger(__name__)

for i in starList:
    logger.info("************************************")
    logger.info("STARTING STAR " + i)
    logger.info("************************************")
    runner = StandardRunner(i,"../Sterndaten/RG_ENRICO/")
    runner.run()
    try:
        runner.join()
    except AssertionError:
        logger.debug("Runner already finished.")
    logger.info("************************************")
    logger.info("STAR" + i +"FINISHED")
    logger.info("************************************")