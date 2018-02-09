import logging

import pandas as pd
import pylab as pl
from plotnine import *

import numpy as np
from readerWriter.resultsWriter import ResultsWriter
from res.strings import *
from settings.settings import Settings
from sys import platform

#apparently this is necessary for Linux, i don't know why.
if platform == "linux" or platform == "linux2":
    pl.switch_backend('Agg')

pl.style.use('ggplot')
logger = logging.getLogger(__name__)

yAxisAnnotation = {'color': 'grey', 'linetype': 'solid'}
smoothingAnnotation = {'color': 'green', 'linetype': 'solid'}
harveyAnnotation = {'color': 'blue', 'linetype': 'dashed'}
backgroundAnnotation = {'color': 'yellow', 'linetype': 'dotted'}
powerExcessAnnotation = {'color': 'blue', 'linetype': 'dotted'}
withoutGaussAnnotation = {'color': 'red', 'linetype': 'solid'}
fullBackgroundAnnotation = {'color': 'cyan', 'linetype': 'dashed'}


def plotPSD(data, psdOnly, markerList=None, smooth=True, visibilityLevel=0, fileName="",forceGauss = False):
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

    if not psdOnly or forceGauss:
        backgroundModel = data.createBackgroundModel()
        if len(backgroundModel) == 5:
            runGauss = True
            title = "Full fit model"
        else:
            runGauss = False
            title = "Noise only model"
    else:
        backgroundModel = None
        runGauss = False
        title = "PSD"

    title += ' KIC' + data.kicID
    dataList = {}
    annotationList = {}

    dataDescriptor = {r'Frequency [$\mu$Hz]': (None, psd[0]),
                      r'PSD [ppm$^2$/$\mu$Hz]': (yAxisAnnotation, psd[1])
                      }
    dataDescriptor = annotateDataDescriptor(dataDescriptor,backgroundModel,psdOnly)

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
            for name,(value,color) in markerList.items():
                idx = (np.abs(psd[0] - value)).argmin()
                p = p + geom_vline(xintercept=psd[0][idx], color=color,linetype="dashed")
        except:
            logger.error("MarkerList needs to be a dict with name,(tuple)")

    p = p + ggtitle(title) + ylab(r'PSD [ppm$^2$/$\mu$Hz]') + \
        scale_x_log10(limits=(min(psd[0]), max(psd[0]))) + scale_y_log10(limits=(min(psd[1] * 0.95), max(psd[1]) * 1.2))

    if visibilityLevel <= debugLevel:
        print(p)

    if fileName != "":
        saveFigToResults(data.kicID, fileName, p)


def plotParameterTrend(data,fileName):
    """
    Plots the parametertrend of the data. Size is automatically determined. Due to the inconsistency and different
    plotting devices, show() needs to be called.
    :param data: Dataset which is to be plotted. It has to have a getBackgroundParameters()  method and a KicID property
    assigned to it.
    """
    backgroundParameters = data.getBackgroundParameters()
    fig = pl.figure(figsize=(20,20))
    for iii in range(0, len(backgroundParameters)):
        par = backgroundParameters[iii].getData()
        pl.subplot(2, 5, iii + 1)
        pl.plot(par, linewidth=2, c='k')
        pl.xlabel(backgroundParameters[iii].name + ' (' + backgroundParameters[iii].unit + ')', fontsize=16)



    if fileName != "":
        saveFigToResults(data.kicID, fileName, fig)
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
        logger.debug("Plotting "+name)
        linetype = 'solid' if linetype is None else linetype
        try:
            plotData = pd.DataFrame({'x':data[0],'y':data[1],'Legend':[name]*len(data[0])})
        except IndexError:
            plotData = pd.DataFrame({'x': data, 'Legend': [name]})
        if linestyle == geom_point:
            p = p+linestyle(aes(x='x',y='y',color='Legend'),data=plotData)
        elif linestyle == geom_vline:
            p = p+linestyle(aes(xintercept='x',color='Legend'),data=plotData)
        else:
            p = p + linestyle(aes(x='x', y='y', color='Legend'), data=plotData,linetype=linetype)

    p = p+ggtitle(title)+xlab(xLabel)+ylab(yLabel)

    if visibilityLevel <= debugLevel:
        print(p)

    if fileName != "":
        saveFigToResults(kicID, fileName, p)

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

def annotateDataDescriptor(dataDescriptor,backgroundModel,psdOnly):
    if not psdOnly:
        dataDescriptor['First Harvey'] = (harveyAnnotation, backgroundModel[0])
        dataDescriptor['Second Harvey'] = (harveyAnnotation, backgroundModel[1])
        dataDescriptor['Third Harvey'] = (harveyAnnotation, backgroundModel[2])
        dataDescriptor['Background'] = (backgroundAnnotation, backgroundModel[3])
        dataDescriptor['Without Gaussian'] = (withoutGaussAnnotation, np.sum(backgroundModel[0:4], axis=0))
        dataDescriptor['Full Background'] = (fullBackgroundAnnotation, np.sum(backgroundModel, axis=0))

    return dataDescriptor
