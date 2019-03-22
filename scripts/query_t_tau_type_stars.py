from astroquery.simbad import Simbad
import numpy as np
import matplotlib.pyplot as pl

Simbad.add_votable_fields('flux(U)')
Simbad.add_votable_fields('flux(B)')
Simbad.add_votable_fields('flux(V)')
Simbad.add_votable_fields('flux(R)')
Simbad.add_votable_fields('flux(I)')

result = Simbad.query_criteria(otype='TTau*')

ids = [f"{i}" for i in result['MAIN_ID']]
ra  = result['RA']
ra_h = []
ra_min = []
ra_sec = []

for i in ra:
    ra_list = i.split(' ')
    try:
        ra_h.append(int(ra_list[0]))
    except:
        ra_h.append(0)
    try:
        ra_min.append(int(ra_list[1]))
    except:
        ra_min.append(0)
    try:
        ra_sec.append(float(ra_list[2]))
    except:
        ra_sec.append(0)

dec_degree = []
dec_min = []
dec_sec = []

dec = result['DEC']

for i in dec:
    dec_list = i.split(' ')
    try:
        dec_degree.append(int(dec_list[0]))
    except:
        dec_degree.append(0)
    try:
        dec_min.append(int(dec_list[1]))
    except:
        dec_min.append(0)
    try:
        dec_sec.append(float(dec_list[2]))
    except:
        dec_sec.append(0)

mag_u = [float(i) for i in result['FLUX_U']]
mag_b = [float(i) for i in result['FLUX_B']]
mag_v = [float(i) for i in result['FLUX_V']]
mag_r = [float(i) for i in result['FLUX_R']]
mag_i = [float(i) for i in result['FLUX_I']]
data_t_tauri = zip(ids, ra_h,ra_min,ra_sec, dec_degree,dec_min,dec_sec, mag_u, mag_b, mag_v, mag_r, mag_i)
with open('t_tauri_types.txt','w') as f:
    f.write('id ra_h ra_min ra_sec dec_deg dec_min dec_sec umag bmag vmag rmag imag\n')
    for i in data_t_tauri:
        write_string = ""
        for j in i:
            j = str(j).replace('\\','')
            write_string += j.strip() + " "
        f.write(write_string + "\n")
arr_dat = np.genfromtxt('t_tauri_types.txt', names=True, usecols=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], invalid_raise = False)
print(arr_dat['umag'])

pl.figure()

ra = (np.array(ra_h) + np.array(ra_min)/60 + np.array(ra_sec)/3600)*15
dec = np.array(dec_degree) + np.array(dec_min)/60 + np.array(dec_sec)/3600

coords = np.array((ra,dec)).T
np.savetxt('coordinates.csv',coords,delimiter=",")

pl.hist(mag_u,alpha=0.5,label='umag',color='violet')
pl.hist(mag_b,alpha=0.5,label='bmag',color='blue')
pl.hist(mag_v,alpha=0.5,label='vmag',color='magenta')
pl.hist(mag_r,alpha=0.5,label='rmag',color='orange')
pl.hist(mag_i,alpha=0.5,label='imag',color='red')
pl.legend()
pl.show()

