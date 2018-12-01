from typing import Dict
from collections import OrderedDict as od
from multiprocessing import Queue
from res.conf_file_str import general_kic
import time
import platform


def print_int(msg: str, kwargs: Dict):
    if platform.system() == 'Darwin':
        Printer.change_message(msg, kwargs)
    else:
        Printer.queue.put((msg, kwargs))


class Printer:
    objMap = od()
    screen = None
    kill = False
    queue = Queue()

    @staticmethod
    def run():
        while not Printer.kill:
            while not Printer.queue.empty():
                val = Printer.queue.get()
                Printer.change_message(val[0], val[1])

            time.sleep(1)

    @staticmethod
    def change_message(msg, kwargs):

        Printer.objMap[kwargs[general_kic]] = msg
        Printer.print_map()

    @staticmethod
    def print_map():

        n = 0

        Printer.screen.clear()
        for key, value in Printer.objMap.items():
            if "Done" in value:
                color = Printer.screen.COLOUR_GREEN
            else:
                color = Printer.screen.COLOUR_YELLOW

            Printer.screen.print_at(f"{key}:{value}\n", 0, n,colour=color)
            n += 1
        Printer.screen.print_at(f"Current ids: {Printer.objMap.keys()}", 0, Printer.screen.height - 1,
                                colour=Printer.screen.COLOUR_CYAN)
        Printer.screen.refresh()

    @staticmethod
    def set_screen(screen):
        Printer.screen = screen

    @staticmethod
    def kill_printer():
        Printer.kill = True
