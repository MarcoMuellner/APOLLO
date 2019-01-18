import numpy as np
from data_handler.file_reader import load_file
from res.conf_file_str import general_kic, analysis_file_path, ascii_skiprows, ascii_use_cols
from support.exceptions import InputFileNotFound

kwargs = {
    analysis_file_path: "/home/marco/Sterndaten/APOKASC_targets/",
    ascii_skiprows: 0,
    ascii_use_cols: (0, 1)
}
missing = []
working = []
data = np.loadtxt("apokasc_targets_1000.txt")
n = 0
for i in data:
    kwargs[general_kic] = int(i[0])
    print(f"{n}/{len(data)}")
    try:
        load_file(kwargs)
        working.append(i)
    except InputFileNotFound:
        print(int(i[0]))
        missing.append(int(i[0]))
    finally:
        n+=1

print(len(data))
print(len(missing))
np.savetxt("Missing.txt", np.array(missing))
np.savetxt("Working.txt", np.array(working))
