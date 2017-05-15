from filehandler.fitsReading import FitsReader
from calculations.powerspectraCalculations import PowerspectraCalculator
from calculations.nuMaxCalculations import NuMaxCalculator
from calculations.priorCalculations import PriorCalculator
from plotter.plotFunctions import *
from filehandler.Diamonds.diamondsFileCreating import FileCreater
from diamonds.diamondsProcesses import DiamondsProcess

def createBackgroundModel(runGauss,median,psd,nyq):
    freq, psd = psd
    par_median = median  # median values

    zeta = 2. * np.sqrt(2.) / np.pi  # !DPI is the pigreca value in double precision
    r = (np.sin(np.pi / 2. * freq / nyq) / (
        np.pi / 2. * freq / nyq)) ** 2  # ; responsivity (apodization) as a sinc^2
    w = par_median[0]  # White noise component
    g = 0
    if runGauss:
        g = median[7] * np.exp(-(median[8] - freq) ** 2 / (2. * median[9] ** 2))  ## Gaussian envelope

    ## Long-trend variations
    sigma_long = par_median[1]
    freq_long = par_median[2]
    h_long = (sigma_long ** 2 / freq_long) / (1. + (freq / freq_long) ** 4)

    ## First granulation component
    sigma_gran1 = par_median[3]
    freq_gran1 = par_median[4]
    h_gran1 = (sigma_gran1 ** 2 / freq_gran1) / (1. + (freq / freq_gran1) ** 4)

    ## Second granulation component
    sigma_gran2 = par_median[5]
    freq_gran2 = par_median[6]
    h_gran2 = (sigma_gran2 ** 2 / freq_gran2) / (1. + (freq / freq_gran2) ** 4)

    ## Global background model
    print(w)
    w = np.zeros_like(freq) + w
    b1 = zeta * (h_long + h_gran1 + h_gran2) * r + w
    print("Whitenoise is '" + str(w) + "'")
    if runGauss:
        b2 = (zeta * (h_long + h_gran1 + h_gran2) + g) * r + w
        return zeta * h_long * r, zeta * h_gran1 * r, zeta * h_gran2 * r, w, g * r
    else:
        return zeta * h_long * r, zeta * h_gran1 * r, zeta * h_gran2 * r, w

def plotPSDTemp(runGauss,psd,backgroundModel):
    smoothedData = None

    pl.figure(figsize=(16, 7))
    pl.loglog(psd[0], psd[1], 'k', alpha=0.5)
    if smoothedData is not None:
        pl.plot(psd[0], smoothedData)
    else:
        print("Smoothingdata is None!")

    pl.plot(psd[0], backgroundModel[0], 'b', linestyle='dashed', linewidth=2)
    pl.plot(psd[0], backgroundModel[1], 'b', linestyle='dashed', linewidth=2)
    pl.plot(psd[0], backgroundModel[2], 'b', linestyle='dashed', linewidth=2)
    pl.plot(psd[0], backgroundModel[3], 'b', linestyle='dashed', linewidth=2)
    pl.plot(psd[0], backgroundModel[4], 'b', linestyle='dashed', linewidth=2)
    withoutGaussianBackground = np.sum(backgroundModel[0:4], axis=0)
    fullBackground = np.sum(backgroundModel, axis=0)
    pl.plot(psd[0], fullBackground, 'c', linestyle='dashed', linewidth=2)
    pl.plot(psd[0], withoutGaussianBackground, 'r', linestyle='solid', linewidth=3)

    pl.xlim(0.1, max(psd[0]))
    pl.ylim(np.mean(psd[1]) / 10 ** 6, max(psd[1]) * 1.2)
    pl.xticks(fontsize=16);
    pl.yticks(fontsize=16)
    pl.xlabel(r'Frequency [$\mu$Hz]', fontsize=18)
    pl.ylabel(r'PSD [ppm$^2$/$\mu$Hz]', fontsize=18)
    title = "Standardmodel" if runGauss else "Noise Backgroundmodel"
    title += ' KIC'
    pl.title(title)
    fig = pl.gcf()
    fig.canvas.set_window_title('Powerspectrum')


#003656476_12
#004346201_18
#004351319_19
#input = '0603396438'
input = "003656476_12"
#input = "0223976028"
powerSpectrum = False
#KeplerData
filename = "../../Sterndaten/KeplerData/kplr" + input + "_COR_" + (
    "PSD_" if powerSpectrum else "") + "filt_inp.fits"
#Young Stars
#filename = "../../Sterndaten/CoRoT_lightcurves/G-type/" + input + "_LC_poly.txt"

#New data
#filename = "../../Sterndaten/LC_CORR/kplr" + input + "_COR.fits"

file = FitsReader(filename)
powerCalc = PowerspectraCalculator(file.getLightCurve())
powerCalc.setKicID(input)

plotPSD(powerCalc,True,True)

nuMaxCalc = NuMaxCalculator(powerCalc.getLightcurve(),powerCalc.getPSD())

print("First iterative Calculation")
corr,best_fit = nuMaxCalc.calculateIterativeFilterFrequency()
print("Second iterative Calculation")
corr_2,best_fit_2 = nuMaxCalc.calculateIterativeFilterFrequency()


initNuFilter = nuMaxCalc.getInitNuFilter()
nuMax = nuMaxCalc.getNuFilterFitted()
photonNoise = nuMaxCalc.getPhotonNoise()
nyquist = nuMaxCalc.getNyquistFrequency()

priorCalculator = PriorCalculator(initNuFilter, nuMax,photonNoise)

print("Priors")
print("PhotonNoise: '" + str(priorCalculator.getPhotonNoiseBoundary()) + "'")
print("First Harvey Frequency: '" + str(priorCalculator.getFirstHarveyFrequencyBoundary()) + "'")
print("First Harvey Amplitude: '" + str(priorCalculator.getHarveyAmplitudesBoundary()) + "'")
print("Second Harvey Frequency: '" + str(priorCalculator.getSecondHarveyFrequencyBoundary()) + "'")
print("Second Harvey Amplitude: '" + str(priorCalculator.getHarveyAmplitudesBoundary()) + "'")
print("Third Harvey Frequency: '" + str(priorCalculator.getThirdHarveyFrequencyBoundary()) + "'")
print("Third Harvey Amplitude: '" + str(priorCalculator.getHarveyAmplitudesBoundary()) + "'")
print("Amplitude: '" + str(priorCalculator.getAmplitudeBounday()) + "'")
print("nuMax: '" + str(priorCalculator.getNuMaxBoundary()) + "'")
print("Sigma: '" + str(priorCalculator.getSigmaBoundary()) + "'")

priors = []
priors.append(priorCalculator.getPhotonNoiseBoundary())
priors.append(priorCalculator.getHarveyAmplitudesBoundary())
priors.append(priorCalculator.getFirstHarveyFrequencyBoundary())
priors.append(priorCalculator.getHarveyAmplitudesBoundary())
priors.append(priorCalculator.getSecondHarveyFrequencyBoundary())
priors.append(priorCalculator.getHarveyAmplitudesBoundary())
priors.append(priorCalculator.getThirdHarveyFrequencyBoundary())
priors.append(priorCalculator.getAmplitudeBounday())
priors.append(priorCalculator.getNuMaxBoundary())
priors.append(priorCalculator.getSigmaBoundary())

lowerBounds = np.zeros(len(priors))
upperBounds = np.zeros(len(priors))

for i in range(0,len(priors) ):
    lowerBounds[i] = priors[i][0]
    upperBounds[i] = priors[i][1]

priors = np.array((lowerBounds,upperBounds)).transpose()

files = FileCreater(input,powerCalc.getPSD(),nyquist,priors)

median = []
median.append(priorCalculator.getPhotonNoise())
median.append(priorCalculator.getHarveyAmplitude())
median.append(priorCalculator.getHarveyFrequency1())
median.append(priorCalculator.getHarveyAmplitude())
median.append(priorCalculator.getHarveyFrequency2())
median.append(priorCalculator.getHarveyAmplitude())
median.append(priorCalculator.getHarveyFrequency3())
median.append(priorCalculator.getAmplitude())
median.append(nuMax)
median.append(priorCalculator.getSigma())

#proc = DiamondsProcess(strDiamondsGaussian,input,"0","1")
#proc.start()

backgroundModel = createBackgroundModel(True,median,powerCalc.getPSD(),nyquist)
plotPSDTemp(True,powerCalc.getPSD(),backgroundModel)
show()