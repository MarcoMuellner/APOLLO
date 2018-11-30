from typing import Dict
from support.singleton import Singleton
from collections import OrderedDict as od
from multiprocessing import Lock
from res.conf_file_str import general_kic
import time

def print_int(msg : str, kwargs : Dict):
    Printer.Instance().print_int(msg,kwargs)


@Singleton
class Printer:
    def __init__(self):
        self._objMap = od()
        self.lock = Lock()

    def change_message(self,msg : str,kwargs : Dict):
        self.lock.acquire()
        self._objMap[kwargs[general_kic]] = msg

    def print_map(self):
        msg = ""
        for key,value in self._objMap.items():
            msg += f"{key}:{value}\n"

        print(msg,end='\r')

        time.sleep(1)