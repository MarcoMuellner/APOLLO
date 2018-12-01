from typing import Dict
from collections import OrderedDict as od
from multiprocessing import Queue
from res.conf_file_str import general_kic
import time
import platform


def print_int(msg: str, kwargs: Dict):
    Printer.queue.put((msg, kwargs))


class Printer:
    objMap = od()
    done_list = []
    screen = None
    kill = False
    queue = Queue()

    @staticmethod
    def run():
        while not Printer.kill:
            changed = False
            while not Printer.queue.empty():
                val = Printer.queue.get()
                Printer.objMap[val[1][general_kic]] = val[0]
                changed = True

            if changed:
                Printer.print_map()

            time.sleep(1)

    @staticmethod
    def print_map():

        if Printer.screen is None:
            for key, value in Printer.objMap.items():
                if "Done" in value:
                    Printer.done_list.append(key)

                print(f"{key}:{value}")
            return

        n = 0

        Printer.screen.clear()
        for key, value in Printer.objMap.items():
            if "Done" in value:
                Printer.done_list.append(key)

            Printer.screen.print_at(f"[{n+1}/{len(Printer.objMap)}]{key}:{value}\n", 0, n, colour=Printer.screen.COLOUR_YELLOW)
            n += 1

        for i in Printer.done_list:
            if i in Printer.objMap.keys():
                del Printer.objMap[i]


        Printer.screen.print_at(f"Done ids: {Printer.done_list}", 0, Printer.screen.height - 2,
                                colour=Printer.screen.COLOUR_GREEN)
        Printer.screen.print_at(f"Current ids: {list(Printer.objMap.keys())}", 0, Printer.screen.height - 1,
                                colour=Printer.screen.COLOUR_CYAN)

        Printer.screen.refresh()

    @staticmethod
    def set_screen(screen):
        Printer.screen = screen

    @staticmethod
    def kill_printer():
        Printer.kill = True
