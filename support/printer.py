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

        n = Printer.screen.width - 1

        str_summary_err = f"No summary file ids: {Printer.summary_err}"
        str_no_file_avail = f"No files ids: {Printer.no_file_avail}"
        str_failed_list = f"Failed ids: {Printer.failed_list}"
        str_done_list = f"Done ids: {Printer.done_list}"
        str_current = f"Current ids: {list(Printer.objMap.keys())}"

        summary_err_list = [str_summary_err[i:i + n] for i in range(0, len(str_summary_err), n)]
        no_file_list = [str_no_file_avail[i:i + n] for i in range(0, len(str_no_file_avail), n)]
        failed_list = [str_failed_list[i:i + n] for i in range(0, len(str_failed_list), n)]
        done_list = [str_done_list[i:i + n] for i in range(0, len(str_done_list), n)]
        current_list = [str_current[i:i + n] for i in range(0, len(str_current), n)]

        offset = len(summary_err_list) + len(no_file_list) + len(failed_list) + len(done_list) + len(current_list) + 1
        start = Printer.screen.height - offset

        j = 0
        for i in summary_err_list:
            Printer.screen.print_at(i, 0, start+j,colour=Printer.screen.COLOUR_RED)
            j+=1

        for i in no_file_list:
            Printer.screen.print_at(i, 0, start+j,colour=Printer.screen.COLOUR_RED)
            j+=1

        for i in failed_list:
            Printer.screen.print_at(i, 0, start+j,colour=Printer.screen.COLOUR_RED)
            j+=1

        for i in done_list:
            Printer.screen.print_at(i, 0, start+j,colour=Printer.screen.COLOUR_GREEN)
            j+=1

        for i in current_list:
            Printer.screen.print_at(i, 0, start+j,colour=Printer.screen.COLOUR_CYAN)
            j+=1

        if Printer.done_list != []:
            np.savetxt("done_list.txt", np.array(Printer.done_list))
        if Printer.failed_list != []:
            np.savetxt("failed.txt", np.array(Printer.failed_list))
        if Printer.no_file_avail != []:
            np.savetxt("no_files.txt", np.array(Printer.no_file_avail))
        if Printer.summary_err:
            np.savetxt("summ_err.txt", np.array(Printer.summary_err))

        Printer.screen.refresh()

    @staticmethod
    def set_screen(screen):
        Printer.screen = screen

    @staticmethod
    def kill_printer():
        Printer.kill = True
