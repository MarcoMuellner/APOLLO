from typing import Dict
from collections import OrderedDict as od
from multiprocessing import Queue
from res.conf_file_str import general_kic,internal_noise_value,internal_run_number,internal_id,internal_multiple_mag,internal_mag_value
import time
import numpy as np
import platform
import datetime
from res.conf_file_str import general_nr_of_cores


def print_int(msg: str, kwargs: Dict):
    Printer.queue.put((msg, kwargs))


class Printer:
    objMap = od()
    done_list = []
    timer = []
    screen = None
    kill = False
    queue = Queue()
    total_runs = 0

    @staticmethod
    def run():
        while not Printer.kill:
            changed = False
            while not Printer.queue.empty():
                val = Printer.queue.get()
                key = val[1][internal_id]
                name = val[1][general_kic]
                if "time" in val[1].keys():
                    Printer.timer.append(val[1]["time"]/val[1][general_nr_of_cores])

                if internal_run_number in val[1]:
                    name = f"{name}_r_{val[1][internal_run_number]}"

                if internal_noise_value in val[1]:
                    name = f"{name}_n_{val[1][internal_noise_value]}"

                if (internal_multiple_mag in val[1].keys() and val[1][internal_multiple_mag]):
                    name = f"{name}_m_{val[1][internal_mag_value]}"


                Printer.objMap[(key,name)] = val[0]

                changed = True

            if changed:
                Printer.print_map()

            time.sleep(1)

    @staticmethod
    def print_map():

        if Printer.screen is None:
            for (key,name), value in Printer.objMap.items():
                try:
                    if "Done" in value:
                        Printer.done_list.append(name)
                except:
                    return

                print(f"{name}:{value}")
            return

        n = 0
        text = ""
        Printer.screen.clear()
        for (key,name), value in Printer.objMap.items():
            if "Done" in value:
                Printer.done_list.append((key,name))
            elif "KILL_SIR" in value:
                Printer.kill = True
                return
            try:
                print_text = f"[{n+1}/{len(Printer.objMap)}]{name}:{value}\n"
                Printer.screen.print_at(print_text, 0, n, colour=Printer.screen.COLOUR_YELLOW)
                text +=print_text
            except IndexError:
                pass
            n += 1

        for i in Printer.done_list:
            if i in Printer.objMap.keys():
                del Printer.objMap[i]

        n = Printer.screen.width - 1

        str_done_list = f"Done ids ({len(Printer.done_list)}): {[name for i,name in Printer.done_list[-30:]]}"
        str_current = f"Current ids ({len(Printer.objMap.keys())}): {list([name for i,name in Printer.objMap.keys()])}"

        done_list = [str_done_list[i:i + n] for i in range(0, len(str_done_list), n)]
        current_list = [str_current[i:i + n] for i in range(0, len(str_current), n)]

        offset = len(done_list) + len(current_list) + 1
        start = Printer.screen.height - offset

        j = 0

        total = len(Printer.done_list)

        for i in done_list:
            Printer.screen.print_at(i, 0, start+j,colour=Printer.screen.COLOUR_GREEN)
            j+=1

        for i in current_list:
            Printer.screen.print_at(i, 0, start+j,colour=Printer.screen.COLOUR_CYAN)
            j+=1

        if Printer.timer != []:
            time_left = str(datetime.timedelta(seconds=float(np.mean(np.array(Printer.timer))*(Printer.total_runs - total))))
        else:
            time_left = f"{np.nan}"

        worked_off_str = f"Worked off: {total}/{Printer.total_runs}, time left: {time_left}"
        Printer.screen.print_at(worked_off_str,0,Printer.screen.height -1,colour=Printer.screen.COLOUR_WHITE)
        with open('worked_off.txt','w') as f:
            f.write(text)
            f.write(f"{done_list}\n")
            f.write(f"{current_list}\n")
            f.writelines(worked_off_str)

        Printer.screen.refresh()

    @staticmethod
    def set_screen(screen):
        Printer.screen = screen

    @staticmethod
    def kill_printer():
        Printer.kill = True
