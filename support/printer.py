from typing import Dict
from collections import OrderedDict as od
from multiprocessing import Queue
from res.conf_file_str import general_kic
import time
import numpy as np
import platform


def print_int(msg: str, kwargs: Dict):
    Printer.queue.put((msg, kwargs))


class Printer:
    objMap = od()
    done_list = []
    failed_list = []
    no_file_avail = []
    summary_err = []
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
            elif "Failed" in value:
                Printer.failed_list.append(key)
            elif "NoFile" in value:
                Printer.no_file_avail.append(key)
            elif "summaryErr" in value:
                Printer.summary_err.append(key)
            elif "KILL_SIR" in value:
                np.savetxt("done_list.txt",np.array(Printer.done_list),fmt='%10.0')
                np.savetxt("failed.txt", np.array(Printer.failed_list),fmt='%10.0')
                np.savetxt("no_files.txt",np.array(Printer.failed_list),fmt='%10.0')
                np.savetxt("summ_err.txt",np.array(Printer.summary_err),fmt='%10.0')
                Printer.kill = True
                return

            Printer.screen.print_at(f"[{n+1}/{len(Printer.objMap)}]{key}:{value}\n", 0, n, colour=Printer.screen.COLOUR_YELLOW)
            n += 1

        for i in Printer.done_list:
            if i in Printer.objMap.keys():
                del Printer.objMap[i]

        for i in Printer.failed_list:
            if i in Printer.objMap.keys():
                del Printer.objMap[i]

        for i in Printer.summary_err:
            if i in Printer.objMap.keys():
                del Printer.objMap[i]

            if i not in Printer.failed_list:
                Printer.failed_list.append(i)

        Printer.screen.print_at(f"No summary file ids: {Printer.summary_err}", 0, Printer.screen.height - 5,
                                colour=Printer.screen.COLOUR_RED)
        Printer.screen.print_at(f"No files ids: {Printer.failed_list}", 0, Printer.screen.height - 4,
                                colour=Printer.screen.COLOUR_RED)
        Printer.screen.print_at(f"Failed ids: {Printer.failed_list}", 0, Printer.screen.height - 3,
                                colour=Printer.screen.COLOUR_RED)
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
