# Author: Dr. Paul G. Beck - CEA Saclay
# e-mail: paul.beck@cea.fr
# Modified by: Dr. Enrico Corsaro
# e-mail: enrico.corsaro@cea.fr
# Date: June 2016

import sys, math, os
import pylab as pl
import numpy as np
import glob
from scipy.signal import butter, filtfilt

pl.style.use('ggplot')

def readPowerspectrumTxt(kicID):
    print(kicID)
    psdFile = glob.glob('../Background/data/KIC*{}*.txt'.format(kicID))[0]
    psd = np.loadtxt(psdFile).T
    return psd

def readBackground(kicID,runID):
    print(glob.glob('../Background/results/KIC*{}*/*{}*/background_parameterSummary.txt'.format(kicID,runID)))
    bckGrdFile = glob.glob('../Background/results/KIC*{}*/*{}*/background_parameterSummary.txt'.format(kicID,runID))[0]
    backGroundParameters = np.loadtxt(bckGrdFile).T
    par_median = backGroundParameters[1] #median values
    par_le = backGroundParameters[4]     #lower credible limits
    par_ue = backGroundParameters[5]     #upper credible limits
    backGroundParameters = np.vstack((par_median,par_le,par_ue))
    return backGroundParameters


def readNyquistFrequency(kicID):
    nyqFile = glob.glob('../Background/results/KIC*{}*/NyquistFrequency.txt'.format(kicID))[0]
    nyquistFrequency = np.loadtxt(nyqFile)
    return nyquistFrequency


def creatingBackgroundModel(psd,nyq,backGroundParameters,kicID,runGauss):
    freq,psd = psd
    par_median,par_le,par_ue = backGroundParameters
    if runGauss:
        hg     = par_median[7] # third last parameter TODO these Parameters need to be added when plotting with gaussian
        numax  = par_median[8] # second last parameter
        sigma  = par_median[9] # last parameter

        print("Height is '"+str(hg)+"'")
        print("Numax is '"+str(numax)+"'")
        print("Sigma is '"+str(sigma)+"'")

    zeta = 2.*np.sqrt(2.)/np.pi # !DPI is the pigreca value in double precision
    r = (np.sin(np.pi/2. * freq/nyq) / (np.pi/2. * freq/nyq))**2 #; responsivity (apodization) as a sinc^2
    w = par_median[0] # White noise component
    g=0
    if runGauss:
        g = hg * np.exp(-(numax-freq)**2/(2.*sigma**2))    ## Gaussian envelope TODO this too

    ## Long-trend variations
    sigma_long = par_median[1]
    freq_long = par_median[2]
    h_long = (sigma_long**2/freq_long) / (1. + (freq/freq_long)**4)

    ## First granulation component
    sigma_gran1 = par_median[3]
    freq_gran1 = par_median[4]
    h_gran1 = (sigma_gran1**2/freq_gran1) / (1. + (freq/freq_gran1)**4)

    ## Second granulation component
    sigma_gran2 = par_median[5]
    freq_gran2 = par_median[6]
    h_gran2 = (sigma_gran2**2/freq_gran2) / (1. + (freq/freq_gran2)**4)

    ## Global background model
    w = np.zeros_like(freq) + w
    b1 = zeta*(h_long + h_gran1 + h_gran2)*r + w
    print("Whitenoise is '"+str(w)+"'")
    if runGauss:
        print("RUnGauss")
        b2 = (zeta*(h_long + h_gran1 + h_gran2) + g)*r + w
        return zeta*h_long*r,zeta*h_gran1*r,zeta*h_gran2*r,w,g*r
    else:
        return zeta * h_long * r, zeta * h_gran1 * r, zeta * h_gran2 * r,w


def readMarginalDistributions(kicID,runID,backGroundParameters,runGauss):
    par_median,par_le,par_ue = backGroundParameters
    pl.figure(figsize=(10,8))

    labelx = ['w (ppm$^2$/$\mu$Hz)','$\sigma_\mathrm{long}$ (ppm)','$b_\mathrm{long}$ ($\mu$Hz)','$\sigma_\mathrm{gran,1}$ (ppm)',
    '$b_\mathrm{gran,1}$ ($\mu$Hz)','$\sigma_\mathrm{gran,2}$ (ppm)','$b_\mathrm{gran,2}$ ($\mu$Hz)','$H_\mathrm{osc}$ (ppm$^2$/$\mu$Hz)',
    '$f_\mathrm{max}$ ($\mu$Hz)','$\sigma_\mathrm{env}$ ($\mu$Hz)']

    upperBoundary = 10 if runGauss else 7

    for iii in range(0,upperBoundary
                     ): #change this parameter depending on the priors!
        mpFile =glob.glob('../Background/results/KIC*{}*/{}/background_marginalDistribution*{}.txt'.format(kicID,runID,iii))[0]
        par, marg = np.loadtxt(mpFile).T

        pl.subplot(2,5,iii+1)
        par_err_le = par_median[iii] - par_le[iii]
        par_err_ue = par_ue[iii] - par_median[iii]
        par_err = (par_err_le**2 + par_err_ue**2)**(0.5)/2**(0.5)
        pl.xlim([par_median[iii]-5*par_err,par_median[iii]+5*par_err])
        pl.ylim([0,max(marg)*1.2])
        pl.plot(par, marg,linewidth=2,c='k')
        pl.fill_between(par[(par >= par_le[iii]) & (par <= par_ue[iii])],
                        marg[(par >= par_le[iii]) & (par <= par_ue[iii])],0,alpha=0.5,facecolor='green')
        pl.axvline(par_median[iii],c='r')
        pl.xlabel(labelx[iii],fontsize=16)
    pl.savefig("marginal_distributions.png")


def butter_lowpass_filtfilt(data, nyq, order=5):
    b, a = butter_lowpass(0.7, nyq, order=order)
    y = filtfilt(b, a, data)
    print(y)
    return y

def butter_lowpass(cutoff, nyq, order=5):
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    print("------------------------------------------")
    print(b,a)
    print("------------------------------------------")
    return b, a

def plotPSD(psd,backgroundModel,data,runGauss,psdOnly,kicID):
    pl.figure(figsize=(16,7))
    #print(data)
    pl.loglog(psd[0],psd[1],'k',alpha=0.5)
    #pl.loglog(psd[0], data)
    if(psdOnly is not True):
        pl.plot(psd[0],backgroundModel[0],'b',linestyle='dashed',linewidth=2) 
        pl.plot(psd[0],backgroundModel[1],'b',linestyle='dashed',linewidth=2)
        pl.plot(psd[0],backgroundModel[2],'b',linestyle='dashed',linewidth=2)
        pl.plot(psd[0], backgroundModel[3], 'b', linestyle='dotted', linewidth=2)
        if runGauss:
            pl.plot(psd[0],backgroundModel[4],'b',linestyle='dotted',linewidth=2)
        withoutGaussianBackground = np.sum(backgroundModel[0:4],axis=0)
        fullBackground = np.sum(backgroundModel,axis=0)
        pl.plot(psd[0],fullBackground,'c',linestyle='dashed',linewidth=2)
        pl.plot(psd[0],withoutGaussianBackground,'r',linestyle='solid',linewidth=3)
    pl.xlim(0.1,max(psd[0]))
    pl.ylim(min(psd[1]*0.95),max(psd[1])*1.2)
    pl.xticks(fontsize=16)  ;pl.yticks(fontsize=16)
    pl.xlabel(r'Frequency [$\mu$Hz]',fontsize=18)
    pl.ylabel(r'PSD [ppm$^2$/$\mu$Hz]',fontsize=18)
    title = "Standardmodel" if runGauss else "Noise Backgroundmodel"
    title += ' KIC'+kicID
    pl.title(title)


if __name__ == "__main__":
    os.system('clear')
    backgroundModel = 0
    data = 0

    arg = str(sys.argv)
    kicID = str(sys.argv[1])
    runID = str(sys.argv[2])
    runGauss = True if str(sys.argv[3]) == "True" else False
    psdOnly = False

    print("Running Gauss is '"+str(sys.argv[3])+"'")
    print(psdOnly)


    psd = readPowerspectrumTxt(kicID)
    nyquistFrequency = 283
    print('Nyquist Frequency (microHz):', nyquistFrequency)
    #data = butter_lowpass_filtfilt(psd[1], nyquistFrequency)

    if(psdOnly is False):
        print("Checking for results")
        backGroundParameters = readBackground(kicID,runID)
        # print np.shape(backGroundParameters)
        print ('Background parameters (median values):', backGroundParameters[0])

        backgroundModel = creatingBackgroundModel(psd,nyquistFrequency,backGroundParameters,kicID,runGauss)
        readMarginalDistributions(kicID, runID, backGroundParameters,runGauss)


    else:
        print("Only plotting Powerspectrum")

    #print(data)
    plotPSD(psd,backgroundModel,data,runGauss= runGauss,psdOnly = psdOnly,kicID = kicID)
    pl.show(block=False)
    input("Hit Enter To Close")
    pl.close()
