import matplotlib as mpl
from loghandler.loghandler import *
from settings.settings import Settings

if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')

setup_logging()
Settings.ins().customPath = "tests/testFiles/lightCurveAnalyzer.json"