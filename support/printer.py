from typing import Dict
from support.singleton import Singleton
from collections import OrderedDict as od
from multiprocessing import Lock
from res.conf_file_str import general_kic
import time
import sys
from subprocess import call
import os

def print_int(msg : str, kwargs : Dict):
    Printer.ins().change_message(msg,kwargs)

# define clear function
def clear():
    # check and make call for specific operating system
    _ = call('clear' if os.name =='posix' else 'cls')

@Singleton
class Printer:
    def __init__(self):
        self._objMap = od()
        self.lock = Lock()

    def change_message(self,msg : str,kwargs : Dict):
        self.lock.acquire()
        self._objMap[kwargs[general_kic]] = msg
        self.print_map()
        if not self.lock.acquire(False):
            self.lock.release()

    def print_map(self):
        msg = ""
        for key,value in self._objMap.items():
            msg += f"{key}:{value}\n"

        clear()
        print(msg)