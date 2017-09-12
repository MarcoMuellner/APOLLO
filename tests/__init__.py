import matplotlib as mpl
from loghandler.loghandler import *

if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')

setup_logging()