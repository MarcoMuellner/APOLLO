import pylab as pl
import numpy as np
from ggplot import *
import pandas as pd

from support.strings import *

def plotPSD(results,runGauss,psdOnly):
    psd = results.getPSD()
    backgroundModel = None
    if psdOnly is False:
        backgroundModel = results.createBackgroundModel(runGauss)
    smoothedData = results.getSmoothing()

    title = "Standardmodel" if runGauss else "Noise Backgroundmodel"
    title += ' KIC' + results.getKicID()
    dataList = {}
    annotationList = {}
    dataList[r'Frequency [$\mu$Hz]'] = psd[0]
    dataList[r'PSD [ppm$^2$/$\mu$Hz]'] = psd[1]
    annotation = {'color': 'grey', 'linetype': 'solid'}
    annotationList[r'PSD [ppm$^2$/$\mu$Hz]'] = annotation

    dataList['Smoothed'] = smoothedData
    annotation = {'color': 'green', 'linetype': 'solid'}
    annotationList['Smoothed'] = annotation

    if psdOnly is False:
        withoutGaussianBackground = np.sum(backgroundModel[0:4], axis=0)
        fullBackground = np.sum(backgroundModel, axis=0)
        dataList['First Harvey'] = backgroundModel[0]
        annotation = {'color': 'blue', 'linetype': 'dashed'}
        annotationList['First Harvey'] = annotation

        dataList['Second Harvey'] = backgroundModel[1]
        annotationList['Second Harvey'] = annotation

        dataList['Third Harvey'] = backgroundModel[2]
        annotationList['Third Harvey'] = annotation

        dataList['Background'] = backgroundModel[3]
        annotation = {'color': 'blue', 'linetype': 'dotted'}
        annotationList['Background'] = annotation

        if runGauss:
            dataList['Poweraccess'] = backgroundModel[4]
            annotation = {'color': 'blue', 'linetype': 'dotted'}
            annotationList['Poweraccess'] = annotation

        dataList['Without Gaussian'] = withoutGaussianBackground
        annotation = {'color': 'red', 'linetype': 'solid'}
        annotationList['Without Gaussian'] = annotation

        dataList['Full Background'] = fullBackground
        annotation = {'color': 'cyan', 'linetype': 'dashed'}
        annotationList['Full Background'] = annotation

    dfData = pd.DataFrame.from_dict(dataList)
    p = ggplot(dfData, aes(x=r'Frequency [$\mu$Hz]'))
    p = p + geom_line(aes(y=r'PSD [ppm$^2$/$\mu$Hz]'), color=annotationList[r'PSD [ppm$^2$/$\mu$Hz]']['color'],
                      linetype=annotationList[r'PSD [ppm$^2$/$\mu$Hz]']['linetype'])
    for i in dataList.keys():
        if i != r'Frequency [$\mu$Hz]' and i != r'PSD [ppm$^2$/$\mu$Hz]':
            if i in annotationList.keys():
                print(i)
                print(annotationList[i])
                p = p + geom_line(aes(y=i), color=annotationList[i]['color'],
                                  linetype=annotationList[i]['linetype'])
            else:
                p = p + geom_line(aes(y=i))

    p = p + scale_x_log() + scale_y_log() + ylim(min(psd[1] * 0.95), max(psd[1]) * 1.2) + ggtitle(title) + ylab(
        r'PSD [ppm$^2$/$\mu$Hz]') + xlim(min(psd[0]),max(psd[0]))
    print(p)


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