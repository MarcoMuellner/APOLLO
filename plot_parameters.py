import pylab as pl
import numpy as np
import glob
import sys
import pandas as pd


pl.style.use('ggplot')


arg = str(sys.argv)
kicID = str(sys.argv[1])
runID = str(sys.argv[2])
runGauss = True if str(sys.argv[3]) == "True" else False
print("Running Gauss is '"+str(sys.argv[3])+"'")
labelx = ['w (ppm$^2$/$\mu$Hz)', '$\sigma_\mathrm{long}$ (ppm)', '$b_\mathrm{long}$ ($\mu$Hz)',
          '$\sigma_\mathrm{gran,1}$ (ppm)',
          '$b_\mathrm{gran,1}$ ($\mu$Hz)', '$\sigma_\mathrm{gran,2}$ (ppm)', '$b_\mathrm{gran,2}$ ($\mu$Hz)']
if runGauss:
    labelx.append('$H_\mathrm{osc}$ (ppm$^2$/$\mu$Hz)')
    labelx.append('$f_\mathrm{max}$ ($\mu$Hz)')
    labelx.append('$\sigma_\mathrm{env}$ ($\mu$Hz)')

upperLimit = 10 if runGauss else 7
parList = {}
length = 0

for iii in range(0, upperLimit):  # change this parameter depending on how many priors you have!
    mpFile = glob.glob('../Background/results/KIC*{}*/{}/background_parameter*{}.txt'.format(kicID, runID, iii))[0]
    par = np.loadtxt(mpFile).T
    length = len(par)
    parList[str(iii)] = par

print(parList)
counter = 9
for iiii in range(len(par)-1,len(par)):
    pl.figure(figsize=(12, 23))
    pl.title("KIC"+str(kicID))
    print(iiii)
    for index in parList.keys():
        #pl.xlim(0,length)
        #pl.ylim(0,max(parList[index]))
        pl.subplot(5, 2, int(index) + 1)
        pl.plot(parList[index][0:iiii],'o',markersize=1, c='k')
        pl.xlabel(labelx[int(index)], fontsize=16)
    counter +=1
    if counter ==10:
        counter = 0
'''
for x in range(0,len(par)):
    for iii in range(1, upperLimit): #change this parameter depending on how many priors you have!
        mpFile = glob.glob('../Background/results/KIC*{}*/{}/background_parameter*{}.txt'.format(kicID, runID, iii))[0]
        par = np.loadtxt(mpFile).T


        pl.figure()
        pl.xlim(0,len(par))
        pl.ylim(0,max(par))
        pl.subplot(2, 5, iii + 1)
        pl.plot(par[0:x], linewidth=2, c='k')
        pl.xlabel(labelx[iii], fontsize=16)
        pl.savefig("/Users/Marco/Google Drive/Astroseismology/Bachelor_Präsentation/video/"+str(x)+".png")
        pl.close()
'''
pl.show()
pl.savefig(f"{kicID}_parametertrend.png")
