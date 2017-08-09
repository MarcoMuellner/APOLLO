import pylab as pl
import numpy as np
from ggplot import *
import pandas as pd
from fitter.fitFunctions import *
import random as r
import logging
from support.strings import *

pl.style.use('ggplot')
logger = logging.getLogger(__name__)

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
    if len(dataList['Smoothed']) != len(dataList[r'Frequency [$\mu$Hz]']):
        dataList['Smoothed'] = smoothedData[1:] #todo this is a hack. Not terribly important, but we should investigate at some point

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

    logger.debug(dataList)
    logger.debug(len(dataList[r'Frequency [$\mu$Hz]']))
    logger.debug(len(dataList[r'PSD [ppm$^2$/$\mu$Hz]']))
    logger.debug(len(dataList['Smoothed']))

    dfData = pd.DataFrame.from_dict(dataList)

    p = ggplot(dfData, aes(x=r'Frequency [$\mu$Hz]'))
    p = p + geom_line(aes(y=r'PSD [ppm$^2$/$\mu$Hz]'), color=annotationList[r'PSD [ppm$^2$/$\mu$Hz]']['color'],
                      linetype=annotationList[r'PSD [ppm$^2$/$\mu$Hz]']['linetype'])
    for i in dataList.keys():
        if i != r'Frequency [$\mu$Hz]' and i != r'PSD [ppm$^2$/$\mu$Hz]':
            if i in annotationList.keys():
                logger.debug(i)
                logger.debug(annotationList[i])
                p = p + geom_line(aes(y=i), color=annotationList[i]['color'],
                                  linetype=annotationList[i]['linetype'])
            else:
                p = p + geom_line(aes(y=i))

    p = p + scale_x_log() + scale_y_log() + ylim(min(psd[1] * 0.95), max(psd[1]) * 1.2) + ggtitle(title) + ylab(
        r'PSD [ppm$^2$/$\mu$Hz]') + xlim(min(psd[0]),max(psd[0]))


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

    dfData = pd.DataFrame({r'Frequency [$\mu$Hz]':deltaF,
                           'Correlation':corrs,
                           'Best fit':deltaNuCalculator.gaussian(deltaF, *best_fit)
    })

    p = ggplot(dfData, aes(x=r'Frequency [$\mu$Hz]'))
    p = p + geom_line(aes(y=r'Correlation'), color='black',
                      linetype='solid',label='Correlated Data')
    p = p + geom_line(aes(y='Best fit'),color='red',linetype='dotted',label='Best Fit')
    p = p + ggtitle(r'Autocorrelation and $\Delta$$\nu$ Fit for KIC'+kicID)
    #p = p + ggtitle(r'Autocorrelation for KIC' + kicID)
    p = p +ylab('Autocorrelation')
    p = p +xlab(r'Frequency [$\mu$Hz]')
    p = p +ylim(0,1.5*max(deltaNuCalculator.gaussian(deltaF, *best_fit)))
    p = p + xlim(deltaNuEst - 0.2 * deltaNuEst, deltaNuEst + 0.2 * deltaNuEst)
    p = p +geom_vline(x=[deltaNuEst],linetype='dashed',color='blue')
    logger.debug(p)


def plotStellarRelations(kicList,x,y,xError,yError,xLabel,yLabel,Title,scaley='linear',scalex='linear',fitDegree = None,fill=True):
    fig = pl.figure()
    ax = fig.add_subplot(111)
    legendList = []
    datapoints = pl.errorbar(x,y,
                xerr=xError,
                yerr=yError,
                fmt='o',
                capsize=5,
                color='k',
                ecolor='k',
                markerfacecolor= 'g',
                label='Datapoints')
    ax.set_yscale(scaley, nonposx='clip')
    ax.set_xscale(scalex, nonposx='clip')
    xlen = 1.2*max(x) - 0.8*min(x)
    ylen = 1.2*max(y) - 0.8*min(y)

    idOffset ={"002436458":(0.008,0),
               "008264006":(0.008,0),
               "008263801":(0.042,0.057),
               "008329894":(0.008,0),
               "008264074":(0.008,0.023),
               "008196817":(-0.19,-0.023),
               "008366239":(-0.19,-0.037),
               "008264079":(0.012,0)}
    for xyz in zip(x, y,kicList):  # <--
        string = "KIC "+xyz[2][2:]
        ax.annotate('%s' % string, xy=(xyz[0]+idOffset[xyz[2]][0]*xlen,xyz[1]+idOffset[xyz[2]][1]*ylen), textcoords='data',fontsize=10)

    legendList.append(datapoints)
    pl.xlim(0.8*min(x),1.2*max(x))
    pl.ylim(0.8*min(y),1.2*max(y))

    if fitDegree is not None:
        yError = np.power(np.array(yError),1)
        popt,cov = np.polyfit(np.array(x),np.array(y),deg=fitDegree,w=yError,cov=True)
        perr = np.sqrt(np.diag(cov))
        chi_squared = np.sum((np.polyval(popt, x) - y) ** 2)
        f = np.poly1d(popt)

        x=np.linspace(0,1000,10000)
        fit = pl.plot(x, f(x), linewidth=0.5, label='Polynomial fit of degree ' + str(fitDegree))
        if fill:
            pl.fill_between(x,popt[0]-perr[0],popt[0]+perr[0],color='grey',alpha=0.5)
            pl.fill_between(x, popt[0] - 2*perr[0], popt[0] + 2*perr[0], color='dimgrey', alpha=0.5)
        legendList.append(fit)
        logger.debug("Polynomial fit degree '"+str(fitDegree)+"', parameters '"+str(popt)+"' and uncertainties '"+str(perr)+"'")
        logger.debug("Chi squared is '"+str(chi_squared)+"'")

    pl.legend()
    pl.xlabel(xLabel)
    pl.ylabel(yLabel)
    pl.title(Title)

def show():
    pl.show()
