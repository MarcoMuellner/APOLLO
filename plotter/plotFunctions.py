import pylab as pl
import numpy as np

from support.strings import *
#Todo maybe use a different plotting device, pylab is fairly ugly
def plotPSD(results,runGauss,psdOnly):
    psd = results.getPSD()
    backgroundModel = None
    if psdOnly is False:
        backgroundModel = results.createBackgroundModel(runGauss)
    smoothedData = results.getSmoothing()

    pl.figure(figsize=(16,7))
    pl.loglog(psd[0],psd[1],'k',alpha=0.5)
    if smoothedData is not None:
        pl.plot(psd[0],smoothedData)
    else:
        print("Smoothingdata is None!")

    if(psdOnly is not True):
        pl.plot(psd[0], backgroundModel[0], 'b', linestyle='dashed', linewidth=2)
        pl.plot(psd[0], backgroundModel[1], 'b', linestyle='dashed', linewidth=2)
        pl.plot(psd[0], backgroundModel[2], 'b', linestyle='dashed', linewidth=2)
        pl.plot(psd[0], backgroundModel[3], 'b', linestyle='dashed', linewidth=2)
        pl.plot(psd[0], backgroundModel[4], 'b', linestyle='dashed', linewidth=2)
        withoutGaussianBackground = np.sum(backgroundModel[0:4],axis=0)
        fullBackground = np.sum(backgroundModel,axis=0)
        pl.plot(psd[0],fullBackground,'c',linestyle='dashed',linewidth=2)
        pl.plot(psd[0],withoutGaussianBackground,'r',linestyle='solid',linewidth=3)

    pl.xlim(0.1,max(psd[0]))
    pl.ylim(np.mean(psd[1])/10**6,max(psd[1])*1.2)
    pl.xticks(fontsize=16)  ;pl.yticks(fontsize=16)
    pl.xlabel(r'Frequency [$\mu$Hz]',fontsize=18)
    pl.ylabel(r'PSD [ppm$^2$/$\mu$Hz]',fontsize=18)
    title = "Standardmodel" if runGauss else "Noise Backgroundmodel"
    title += ' KIC'+results.getKicID()
    pl.title(title)
    fig = pl.gcf()
    fig.canvas.set_window_title('Powerspectrum')

def plotMarginalDistributions(results):
    pl.figure(figsize=(23,12))
    marginalDists = results.createMarginalDistribution()
    summary = results.getSummary()

    par_median = summary.getData(strSummaryMedian)  # median values
    par_le = summary.getData(strSummaryLowCredLim)  # lower credible limits
    par_ue = summary.getData(strSummaryUpCredlim)  # upper credible limits

    for iii in range(0,len(marginalDists)):
        pl.subplot(2,5,iii+1)
        par, marg, fill_x, fill_y, par_err = marginalDists[iii].createMarginalDistribution()

        pl.xlim([par_median[iii]-5*par_err,par_median[iii]+5*par_err])
        pl.ylim([0,max(marg)*1.2])
        pl.plot(par, marg,linewidth=2,c='k')
        pl.fill_between(fill_x,fill_y,0,alpha=0.5,facecolor='green')
        pl.axvline(par_median[iii],c='r')
        pl.xlabel(marginalDists[iii].getName() + ' (' + marginalDists[iii].getUnit()+')',fontsize=16)

def plotParameterTrend(results):
    backgroundParameters = results.getBackgroundParameters()

    for iii in range(0,len(backgroundParameters)):
        par = backgroundParameters[iii].getData()
        pl.subplot(2, 5, iii + 1)
        pl.plot(par, linewidth=2, c='k')
        pl.xlabel(backgroundParameters[iii].getName() + ' (' + backgroundParameters[iii].getUnit()+')' , fontsize=16)

def plotDeltaNuFit(deltaNuCalculator,kicID):
    deltaNuEst = deltaNuCalculator.getDeltaNuEst()
    deltaF = deltaNuCalculator.getDeltaF()
    best_fit = deltaNuCalculator.getBestFit()
    corrs = deltaNuCalculator.getCorrelations()
    init_fit = deltaNuCalculator.getInitFit()

    pl.figure(figsize=(16, 7))
    pl.axvline(x=deltaNuEst, linestyle='dotted')
    pl.xlim(deltaNuEst - 0.2 * deltaNuEst, deltaNuEst + 0.2 * deltaNuEst)
    data = pl.plot(deltaF, corrs, 'b', linewidth=2,label='ACF')
    final_fit = pl.plot(deltaF, deltaNuCalculator.gaussian(deltaF, *best_fit), 'r', linestyle='dotted',label='Best Fit')
    start_fit = pl.plot(deltaF, deltaNuCalculator.gaussian(deltaF, *init_fit), 'g', linestyle='dashed',label='Init Fit')
    pl.legend()
    pl.xlabel("Delta nu (uHz)")
    pl.ylabel("ACF")
    pl.title("Autocorrelation Delta Nu KIC"+str(kicID))
    fig = pl.gcf()
    fig.canvas.set_window_title('DeltaNuFit')

def show():
    pl.show()