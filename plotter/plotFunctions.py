import logging

import pandas as pd
import pylab as pl
from plotnine import *

import numpy as np
from readerWriter.resultsWriter import ResultsWriter
from res.strings import *
from settings.settings import Settings

pl.switch_backend('Agg')
pl.style.use('ggplot')
logger = logging.getLogger(__name__)


def plotPSD(data, psdOnly, markerList=None, smooth=True, visibilityLevel=0, fileName=""):
    '''
    This function creates a possibility to plot a powerSpectralDensity. Depending on the parameters, you can plot
    the PSD only, with markers, with smoothing, the full fit and all combinations of them.
    :param data:The data which you want to plot. Depending on what you want to plot, this parameter needs different
    objects as an input. The following things are used:
    - data.kicID -> must have. Defines the title of the plot
    - data.powerSpectralDensity -> must have. The actual data of the plot. x-Axis has to be frequency, y-Axis has to be
        ppm^2
    - data.smoothedData -> optional. Has to be provided if the smooth flag is True. Plots the smoothed variant of the
        psd
    - data.createBackgroundModel(bool) -> optional. This is needed if you want to actually plot a fit inside the psd
    :param psdOnly: The psdOnly flag defines if you only want to plot the psd of the data object.
    :type psdOnly:bool
    :param markerList: The markerList gives you the possibility to draw vertical lines into the PSD.
    You can mark frequencies with this method
    :type markerList:dict[float,tuple[string,string]]
    :param smooth:This flag defines if the smoothed variant should be plotted.
    :type smooth:bool
    :param visibilityLevel:This parameter defines if the plot is shown or not. If visibilityLevel<SettingsLevel it will
    be shown
    :type visibilityLevel:int
    :param fileName:The filename with which you want to save the plot. If it is empty, the plot will not be saved
    :type fileName:str
    :return:
    :rtype:
    '''
    debugLevel = int(Settings.Instance().getSetting(strMiscSettings, strSectDevMode).value)
    psd = data.powerSpectralDensity
    backgroundModel = None
    if not psdOnly:
        backgroundModel = data.createBackgroundModel()
        if len(backgroundModel) == 5:
            runGauss = True
            title = "Full fit model"
        else:
            runGauss = False
            title = "Noise only model"
    else:
        runGauss = False
        title = "PSD"

    title += ' KIC' + data.kicID
    dataList = {}
    annotationList = {}

    yAxisAnnotation = {'color': 'grey', 'linetype': 'solid'}
    smoothingAnnotation = {'color': 'green', 'linetype': 'solid'}
    harveyAnnotation = {'color': 'blue', 'linetype': 'dashed'}
    backgroundAnnotation = {'color': 'yellow', 'linetype': 'dotted'}
    powerExcessAnnotation = {'color': 'blue', 'linetype': 'dotted'}
    withoutGaussAnnotation = {'color': 'red', 'linetype': 'solid'}
    fullBackgroundAnnotation = {'color': 'cyan', 'linetype': 'dashed'}

    dataDescriptor = {r'Frequency [$\mu$Hz]': (None, psd[0]),
                      r'PSD [ppm$^2$/$\mu$Hz]': (yAxisAnnotation, psd[1])
                      }
    if not psdOnly:
        dataDescriptor['First Harvey'] = (harveyAnnotation, backgroundModel[0])
        dataDescriptor['Second Harvey'] = (harveyAnnotation, backgroundModel[1])
        dataDescriptor['Third Harvey'] = (harveyAnnotation, backgroundModel[2])
        dataDescriptor['Background'] = (backgroundAnnotation, backgroundModel[3])
        dataDescriptor['Without Gaussian'] = (withoutGaussAnnotation, np.sum(backgroundModel[0:4], axis=0))
        dataDescriptor['Full Background'] = (fullBackgroundAnnotation, np.sum(backgroundModel, axis=0))

    if smooth:
        try:
            dataDescriptor['Smoothed'] = (smoothingAnnotation, data.smoothedData)
        except AttributeError:
            logger.warning("No smoothing available for object type " + str(type(data)))

    if runGauss:
        dataDescriptor['Poweraccess'] = (powerExcessAnnotation, backgroundModel[4])

    for name, (annotation, dataSet) in dataDescriptor.items():
        dataList[name] = dataSet
        if annotation is not None:
            annotationList[name] = annotation

    dfData = pd.DataFrame.from_dict(dataList)

    p = ggplot(dfData, aes(x=r'Frequency [$\mu$Hz]'))
    p = p + geom_line(aes(y=r'PSD [ppm$^2$/$\mu$Hz]'), color=annotationList[r'PSD [ppm$^2$/$\mu$Hz]']['color'],
                      linetype=annotationList[r'PSD [ppm$^2$/$\mu$Hz]']['linetype'])

    for i in dataList.keys():
        logger.debug("Key '" + i + "' will be plotted")
        if i != r'Frequency [$\mu$Hz]' and i != r'PSD [ppm$^2$/$\mu$Hz]':
            if i in annotationList.keys():
                logger.debug(i)
                logger.debug(annotationList[i])
                p = p + geom_line(aes(y=i), color=annotationList[i]['color'],
                                  linetype=annotationList[i]['linetype'])
            else:
                p = p + geom_line(aes(y=i))
    if markerList is not None:
        try:
            for i in markerList.keys():
                logger.debug("Add marker with name '" + i + "'")
                logger.debug("Add marker at '" + str(markerList[i][0]) + "'")
                logger.debug("Min x-value: '" + str(min(psd[0])))
                logger.debug("Max x-value: '" + str(max(psd[0])))
                idx = (np.abs(psd[0] - markerList[i][0])).argmin()
                logger.debug("Real plotted value: '" + str(psd[0][idx]) + "'")
                p = p + geom_vline(x=psd[0][idx], color=markerList[i][1])
        except:
            logger.error("MarkerList needs to be a dict with name,(tuple)")

    p = p + ggtitle(title) + ylab(r'PSD [ppm$^2$/$\mu$Hz]') + \
        scale_x_log10(limits=(min(psd[0]), max(psd[0]))) + scale_y_log10(limits=(min(psd[1] * 0.95), max(psd[1]) * 1.2))

    if visibilityLevel <= debugLevel:
        print(p)

    if fileName != "":
        saveFigToResults(data.kicID, fileName, p)


def plotMarginalDistributions(data,visibilityLevel=0,fileName=0):
    '''
        This method provides the possibility to plot the marginal Distributions of the DIAMONDS run. Using the raw data
    from the summaryFileModel, and the MarginalDistribution of the data it draws the plot. The size of the plot
    is determined by the count of the parameters.Due to the inconsistency and different plotting devices, show() needs
    to be called.
    :param data: The data which will be plotted. Has to have a getMarginalDistribution() method and a summary property
    assigned to it
    :param visibilityLevel:This parameter defines if the plot is shown or not. If visibilityLevel<SettingsLevel it will
    be shown
    :type visibilityLevel:int
    :param fileName:The filename with which you want to save the plot. If it is empty, the plot will not be saved
    :type fileName:str
    '''
    pl.figure(figsize=(23, 12))
    marginalDists = data.getMarginalDistribution()
    summary = data.summary

    par_median = summary.getRawData(strSummaryMedian)  # median values

    for iii in range(0, len(marginalDists)):
        pl.subplot(2, 5, iii + 1)
        par, marg, fill_x, fill_y, par_err = marginalDists[iii].getMarginalDistribution()

        pl.xlim([par_median[iii] - 5 * par_err, par_median[iii] + 5 * par_err])
        pl.ylim([0, max(marg) * 1.2])
        pl.plot(par, marg, linewidth=2, c='k')
        pl.fill_between(fill_x, fill_y, 0, alpha=0.5, facecolor='green')
        pl.axvline(par_median[iii], c='r')
        pl.xlabel(marginalDists[iii].name + ' (' + marginalDists[iii].unit + ')', fontsize=16)


def plotParameterTrend(data,fileName):
    """
    Plots the parametertrend of the data. Size is automatically determined. Due to the inconsistency and different
    plotting devices, show() needs to be called.
    :param data: Dataset which is to be plotted. It has to have a getBackgroundParameters()  method and a KicID property
    assigned to it.
    """
    backgroundParameters = data.getBackgroundParameters()
    fig = pl.figure()
    for iii in range(0, len(backgroundParameters)):
        par = backgroundParameters[iii].getData()
        pl.subplot(2, 5, iii + 1)
        pl.plot(par, linewidth=2, c='k')
        pl.xlabel(backgroundParameters[iii].name + ' (' + backgroundParameters[iii].unit + ')', fontsize=16)

    if fileName != "":
        saveFigToResults(data.kicID, fileName, fig)
    return fig


def plotDeltaNuFit(deltaNuCalculator, kicID, visibilityLevel=0):
    """
    Legacy
    """
    debugLevel = int(Settings.Instance().getSetting(strMiscSettings, strSectDevMode).value)
    deltaNuEst = deltaNuCalculator.deltaNuEst
    deltaF = deltaNuCalculator.deltaF
    best_fit = deltaNuCalculator.bestFit
    corrs = deltaNuCalculator.correlations

    dfData = pd.DataFrame({r'Frequency [$\mu$Hz]': deltaF,
                           'Correlation': corrs,
                           'Best fit': deltaNuCalculator.gaussian(deltaF, *best_fit)
                           })

    p = ggplot(dfData, aes(x=r'Frequency [$\mu$Hz]'))
    p = p + geom_line(aes(y=r'Correlation'), color='black',
                      linetype='solid', label='Correlated Data')
    p = p + geom_line(aes(y='Best fit'), color='red', linetype='dotted', label='Best Fit')
    p = p + ggtitle(r'Autocorrelation and $\Delta$$\nu$ Fit for KIC' + kicID)
    p = p + ylab('Autocorrelation')
    p = p + xlab(r'Frequency [$\mu$Hz]')
    p = p + ylim(0, 1.5 * max(deltaNuCalculator.gaussian(deltaF, *best_fit)))
    p = p + xlim(deltaNuEst - 0.2 * deltaNuEst, deltaNuEst + 0.2 * deltaNuEst)
    p = p + geom_vline(x=[deltaNuEst], linetype='dashed', color='blue')
    if visibilityLevel <= debugLevel:
        print(p)
    return p


def plotStellarRelations(kicList, x, y, xError, yError, xLabel, yLabel, Title, scaley='linear', scalex='linear',
                         fitDegree=None, fill=True):
    """
    Legacy
    """
    fig = pl.figure()
    ax = fig.add_subplot(111)
    legendList = []
    datapoints = pl.errorbar(x, y,
                             xerr=xError,
                             yerr=yError,
                             fmt='o',
                             capsize=5,
                             color='k',
                             ecolor='k',
                             markerfacecolor='g',
                             label='Datapoints')
    ax.set_yscale(scaley, nonposx='clip')
    ax.set_xscale(scalex, nonposx='clip')
    xlen = 1.2 * max(x) - 0.8 * min(x)
    ylen = 1.2 * max(y) - 0.8 * min(y)

    idOffset = {"002436458": (0.008, 0),
                "008264006": (0.008, 0),
                "008263801": (0.042, 0.057),
                "008329894": (0.008, 0),
                "008264074": (0.008, 0.023),
                "008196817": (-0.19, -0.023),
                "008366239": (-0.19, -0.037),
                "008264079": (0.012, 0)}
    for xyz in zip(x, y, kicList):  # <--
        string = "KIC " + xyz[2][2:]
        ax.annotate('%s' % string, xy=(xyz[0] + idOffset[xyz[2]][0] * xlen, xyz[1] + idOffset[xyz[2]][1] * ylen),
                    textcoords='data', fontsize=10)

    legendList.append(datapoints)
    pl.xlim(0.8 * min(x), 1.2 * max(x))
    pl.ylim(0.8 * min(y), 1.2 * max(y))

    if fitDegree is not None:
        yError = np.power(np.array(yError), 1)
        popt, cov = np.polyfit(np.array(x), np.array(y), deg=fitDegree, w=yError, cov=True)
        perr = np.sqrt(np.diag(cov))
        chi_squared = np.sum((np.polyval(popt, x) - y) ** 2)
        f = np.poly1d(popt)

        x = np.linspace(0, 1000, 10000)
        fit = pl.plot(x, f(x), linewidth=0.5, label='Polynomial fit of degree ' + str(fitDegree))
        if fill:
            pl.fill_between(x, popt[0] - perr[0], popt[0] + perr[0], color='grey', alpha=0.5)
            pl.fill_between(x, popt[0] - 2 * perr[0], popt[0] + 2 * perr[0], color='dimgrey', alpha=0.5)
        legendList.append(fit)
        logger.debug(
            "Polynomial fit degree '" + str(fitDegree) + "', parameters '" + str(popt) + "' and uncertainties '" + str(
                perr) + "'")
        logger.debug("Chi squared is '" + str(chi_squared) + "'")

    pl.legend()
    pl.xlabel(xLabel)
    pl.ylabel(yLabel)
    pl.title(Title)
    return fig


def plotLightCurve(data, visibilityLevel=0, fileName=""):
    """
    Plots the lightCurve from data.
    :param data: The data object from which the plot will be generated. Has to have a lightCurve property and a kicID
    property associated to it
    :param visibilityLevel:This parameter defines if the plot is shown or not. If visibilityLevel<SettingsLevel it will
    be shown
    :type visibilityLevel:int
    :param fileName:The filename with which you want to save the plot. If it is empty, the plot will not be saved
    :type fileName:str
    """
    debugLevel = int(Settings.Instance().getSetting(strMiscSettings, strSectDevMode).value)
    lightCurve = data.lightCurve
    title = "Lightcurve " + data.kicID
    dataList = {}
    annotationList = {}
    dataList[r'Observation Time [d]'] = lightCurve[0]
    dataList[r'Flux'] = lightCurve[1]
    annotation = {'color': 'grey', 'linetype': 'solid'}
    annotationList[r'Flux'] = annotation
    dfData = pd.DataFrame.from_dict(dataList)
    p = ggplot(dfData, aes(x=r'Observation Time [d]'))
    p = p + geom_point(aes(y=r'Flux'), color=annotationList[r'Flux']['color'])
    p = p + ylab(r'Flux')
    p = p + xlab(r'Observation Time [d]')
    p = p + ylim(1.1 * min(lightCurve[1]), 1.1 * max(lightCurve[1]))
    p = p + xlim(min(lightCurve[0]), max(lightCurve[0]))
    p = p + ggtitle(title)
    if visibilityLevel <= debugLevel:
        print(p)

    if fileName != "":
        saveFigToResults(data.kicID, fileName, p)

def plotCustom(kicID, title, data, xLabel="", yLabel="", fileName ="", visibilityLevel = 0):
    """
    Custom Plotter, designed to be a convinient function to plot a certain dataset.
    :param kicID: The KICID for the plot. Needed for saving the plot
    :type kicID: str
    :param data: Dataset containing the plotData and other parameters. Should look like this:
                    {name:(data,linestyle,linetype)}
                    name:Name of the dataset
                    data:Dataset to plot. First axis is x-Axis, Second is y-Axis
                    linestyle: The linestyle used, i.e geom_line, geom_point, etc.
                    linetype: dashed, solid etc. Can be None
    :type data: dict
    :param title: The title of the plot
    :type title: str
    :param xLabel: The xLabel of the plot
    :type xLabel: str
    :param yLabel: The yLabel of the plot
    :type yLabel: str
    :param fileName:The filename with which you want to save the plot. If it is empty, the plot will not be saved
    :type fileName:str
    :param visibilityLevel:This parameter defines if the plot is shown or not. If visibilityLevel<SettingsLevel it will
    be shown
    :type visibilityLevel:int
    :return:
    """
    p = ggplot()
    debugLevel = int(Settings.Instance().getSetting(strMiscSettings, strSectDevMode).value)
    for name,(data,linestyle,linetype) in data.items():
        linetype = 'solid' if linetype is None else linetype
        plotData = pd.DataFrame({'x':data[0],'y':data[1],'Legend':[name]*len(data[1])})
        if linestyle == geom_point:
            p = p+linestyle(aes(x='x',y='y',color='Legend'),data=plotData)
        else:
            p = p + linestyle(aes(x='x', y='y', color='Legend'), data=plotData,linetype=linetype)

    p = p+ggtitle(title)+xlab(xLabel)+ylab(yLabel)

    if visibilityLevel <= debugLevel:
        print(p)

    if fileName != "":
        saveFigToResults(kicID, fileName, p)



"""
def plotCustom(kicID, dataList, title="", showLegend=False, fileName=""):
    '''
    Custom plotter. Convinience function. Plots the data from dataList.Due to the inconsistency and different
    plotting devices, show() needs to be called.
    :param kicID: KicID of the plot
    :type kicID: str
    :param dataList: The actual datalist that will be plotted. The structure of the dataList has to be in the form:
    {label,(marker,x,y)}
    - label is the label of the line
    - marker is the way the plot is shown, i.e.'x','o', '-' and so on
    - x,y is the actual data that needs to be shown
    :type dataList: dict[str,(str,ndarray,ndarray)]
    :param title: Title of the whole plot
    :type title: str
    :param showLegend: Flag if the legend should be shown
    :type showLegend: bool
    :param fileName:The filename with which you want to save the plot. If it is empty, the plot will not be saved
    :type fileName:str
    '''
    fig = pl.figure()
    for label, (marker, x, y) in dataList.items():
        pl.plot(x, y, marker, label=label)

    if title != "":
        pl.title(title)

    if showLegend:
        pl.legend()

    if fileName != "":
        saveFigToResults(kicID, fileName, fig)
    return fig
"""

def show(visibilityLevel=0):
    """
    Convinience show function. For functions where you need to call pl.show(), you should use this function, as it
    will check the visibility level of the last plots opened. Closes the plots if they don't need to be shown.
    :param visibilityLevel:This parameter defines if the plot is shown or not. If visibilityLevel<SettingsLevel it will
    be shown
    :type visibilityLevel:int
    """
    debugLevel = int(Settings.Instance().getSetting(strMiscSettings, strSectDevMode).value)
    if visibilityLevel <= debugLevel:
        pl.show()
    else:
        pl.close()


def saveFigToResults(kicID, filename, figure):
    """
    This function will add the Figure object of the plots to the ResultWriter, which in turn will save them accordingly.
    Is basically only called from within the other function, but you can use it for your custom plotter as well
    :param kicID:KicID of the star you are currently working on
    :type kicID: str
    :param filename: Name of the file
    :type filename: str
    :param figure: Figure object, provided by the different plotter mechanisms
    :type figure: Figure
    """
    ResultsWriter.Instance(kicID).addImage(filename, figure)
