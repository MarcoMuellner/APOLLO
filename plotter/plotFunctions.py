import logging

import pandas as pd
from matplotlib import pyplot as pl
from matplotlib.figure import Figure
from matplotlib.axes import Axes

import numpy as np
from readerWriter.resultsWriter import ResultsWriter
from res.strings import *
from settings.settings import Settings

import warnings
warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

pl.rc('font', family='serif')
pl.rc('xtick', labelsize='x-small')
pl.rc('ytick', labelsize='x-small')

yAxisAnnotation = {'color': 'k', 'linetype': ':'}
smoothingAnnotation = {'color': 'g', 'linetype': '-'}
harveyAnnotation = {'color': 'b', 'linetype': '--'}
backgroundAnnotation = {'color': 'y', 'linetype': ':'}
powerExcessAnnotation = {'color': 'c', 'linetype': ':'}
withoutGaussAnnotation = {'color': 'r', 'linetype': '-'}
fullBackgroundAnnotation = {'color': 'm', 'linetype': '--'}

def add_subplot_axes(ax,rect,axisbg='w'):
    fig = pl.gcf()
    box = ax.get_position()
    width = box.width
    height = box.height
    inax_position  = ax.transAxes.transform(rect[0:2])
    transFigure = fig.transFigure.inverted()
    infig_position = transFigure.transform(inax_position)
    x = infig_position[0]
    y = infig_position[1]
    width *= rect[2]
    height *= rect[3]  # <= Typo was here
    subax = fig.add_axes([x,y,width,height])#axisbg=axisbg)
    subax.set_facecolor('white')
    x_labelsize = subax.get_xticklabels()[0].get_size()
    y_labelsize = subax.get_yticklabels()[0].get_size()
    x_labelsize *= rect[2]**0.5
    y_labelsize *= rect[3]**0.5
    subax.xaxis.set_tick_params(labelsize=x_labelsize)
    subax.yaxis.set_tick_params(labelsize=y_labelsize)
    return subax


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
    debugLevel = int(Settings.ins().getSetting(strMiscSettings, strSectDevMode).value)
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

    if runGauss:
        dataDescriptor['Poweraccess'] = (powerExcessAnnotation, backgroundModel[4])

    for name, (annotation, dataSet) in dataDescriptor.items():
        dataList[name] = dataSet
        if annotation is not None:
            annotationList[name] = annotation

    fig : Figure = pl.figure()
    ax : Axes= fig.add_subplot(111)
    ax.loglog(psd[0],psd[1],color='k')
    ax.set_title(title)
    ax.set_ylabel(r'PSD [ppm$^2$/$\mu$Hz]')
    ax.set_xlabel(r'Frequency [$\mu$Hz]')

    if smooth:
        try:
            ax.loglog(psd[0],data.smoothedData,color=smoothingAnnotation['color'],linestyle=smoothingAnnotation['linetype'])
            dataDescriptor['Smoothed'] = (smoothingAnnotation, data.smoothedData)
        except AttributeError:
            logger.warning("No smoothing available for object type " + str(type(data)))

    for i in dataList.keys():
        if i != r'Frequency [$\mu$Hz]' and i != r'PSD [ppm$^2$/$\mu$Hz]':
            if i in annotationList.keys():
                logger.debug(i)
                logger.debug(annotationList[i])
                ax.loglog(psd[0],dataList[i],color=annotationList[i]['color'],linestyle=annotationList[i]['linetype'])
            else:
                ax.loglog(psd[0], i)
    if markerList is not None:
        try:
            for name,(value,color) in markerList.items():
                idx = (np.abs(psd[0] - value)).argmin()
                ax.axvline(x=psd[0][idx],color=color,linestyle='--')
        except:
            logger.error("MarkerList needs to be a dict with name,(tuple)")

    ax.set_xlim(min(psd[0]), max(psd[0]))
    ax.set_ylim(min(psd[1] * 0.95), max(psd[1]) * 1.2)

    if visibilityLevel <= debugLevel:
        fig.show()

    if fileName != "":
        saveFigToResults(data.kicID, fileName, fig)


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
    debugLevel = int(Settings.ins().getSetting(strMiscSettings, strSectDevMode).value)
    lightCurve = data.lightCurve
    title = "Lightcurve " + data.kicID

    fig : Figure = pl.figure()
    ax : Axes = fig.add_subplot(111)

    ax.plot(lightCurve[0],lightCurve[1],'o',color='k')
    ax.set_title(title)
    ax.set_xlabel(r'Observation Time [d]')
    ax.set_ylabel(r'Flux')
    ax.set_xlim(min(lightCurve[0]), max(lightCurve[0]))
    ax.set_ylim(1.1 * min(lightCurve[1]), 1.1 * max(lightCurve[1]))

    if visibilityLevel <= debugLevel:
        fig.show()

    if fileName != "":
        saveFigToResults(data.kicID, fileName, fig)

def plotCustom(kicID, title, data, xLabel="", yLabel="", fileName ="", visibilityLevel = 0):
    """
    Custom Plotter, designed to be a convinient function to plot a certain dataset.
    :param kicID: The KICID for the plot. Needed for saving the plot
    :type kicID: str
    :param data: Dataset containing the plotData and other parameters. Should look like this:
                    {name:(data,linestyle,linetype)}
                    name:Name of the dataset
                    data:Dataset to plot. First axis is x-Axis, Second is y-Axis
                    linestyle: The linestyle used, i.e '-','x', whatever
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

    debugLevel = int(Settings.ins().getSetting(strMiscSettings, strSectDevMode).value)

    fig :Figure = pl.figure()
    ax : Axes = fig.add_subplot(111)

    dotList = ['x','o']
    lineStyleList = ['-','--','-.',':']

    for name,(data,linestyle) in data.items():
        logger.debug("Plotting "+name)

        if linestyle in dotList:
            ax.plot(data[0], data[1],linestyle,label=name)
        elif linestyle in lineStyleList:
            ax.plot(data[0], data[1], linestyle = linestyle, label=name)
        elif linestyle == '|':
            ax.axvline(x=data,linestyle='--',label=name)
        elif linestyle == '/':
            ax.axhline(y=data,linestyle='--',label=name)
        else:
            ax.plot(data[0],data[1],label=name)

    ax.set_title(title)
    ax.set_xlabel(xLabel)
    ax.set_ylabel(yLabel)

    if visibilityLevel <= debugLevel:
        fig.show()

    if fileName != "":
        saveFigToResults(kicID, fileName, fig)

def show(visibilityLevel=0):
    """
    Convinience show function. For functions where you need to call pl.show(), you should use this function, as it
    will check the visibility level of the last plots opened. Closes the plots if they don't need to be shown.
    :param visibilityLevel:This parameter defines if the plot is shown or not. If visibilityLevel<SettingsLevel it will
    be shown
    :type visibilityLevel:int
    """
    debugLevel = int(Settings.ins().getSetting(strMiscSettings, strSectDevMode).value)
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
    ResultsWriter.addImage(kicID,filename,figure)

def annotateDataDescriptor(dataDescriptor,backgroundModel,psdOnly):
    if not psdOnly:
        dataDescriptor['First Harvey'] = (harveyAnnotation, backgroundModel[0])
        dataDescriptor['Second Harvey'] = (harveyAnnotation, backgroundModel[1])
        dataDescriptor['Third Harvey'] = (harveyAnnotation, backgroundModel[2])
        dataDescriptor['Background'] = (backgroundAnnotation, backgroundModel[3])
        dataDescriptor['Without Gaussian'] = (withoutGaussAnnotation, np.sum(backgroundModel[0:4], axis=0))
        dataDescriptor['Full Background'] = (fullBackgroundAnnotation, np.sum(backgroundModel, axis=0))

    return dataDescriptor
