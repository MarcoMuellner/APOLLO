import os
import json
import logging.config
import coloredlogs,logging

logging.getLogger("matplotlib").setLevel(logging.WARNING)

def setup_logging(
    default_path='loghandler/logsettings.json', 
    default_level=logging.DEBUG,
):
    '''Setup logging configuration

    '''
    path = default_path
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

    coloredlogs.install()
