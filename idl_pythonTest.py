import numpy as np
from filehandler.fitsReading import FitsReader
from calculations.powerspectraCalculations import PowerspectraCalculator
from sympy.ntheory import factorint
import pylab as pl
from plotter.plotFunctions import *
from scipy import optimize

def sin(x,amp,tau):
   return amp*np.sin(2*np.pi*4*x/tau)

def sinc(x, a, tau_acf):
    return a * np.sinc((4* np.pi*x / tau_acf)**2)


def fullFunc(x,a1,a2,tau):
    return sinc(x,a1,tau)+sin(x,a2,tau)

def trismooth(x,window_width,gauss=False):
    #print(window_width)
    if window_width%2 != 0:
        window_width = window_width+1

    lend = len(x)-1
    if (lend+1) < window_width:
        print("Vector too short!")
        raise

    halfWeights = np.arange(window_width/2)
    weights = np.append(halfWeights,[window_width/2])
    weights = np.append(weights,halfWeights[::-1])
    weights +=1
    tot = np.sum(weights)

    smoothed = np.zeros(lend+1)
    offset = int(window_width/2)
    local = np.zeros(window_width)

    print("Len smoothed "+str(len(smoothed)))
    print("Offset is "+str(offset))
    print("len local "+str(len(local)))

    for i in range(offset,lend-offset):
        smoothed[i]=np.sum(x[i-offset:i+offset+1]*weights)

    smoothed /=tot

    for i in range(0,offset):
        smoothed[i] = np.sum(x[0:i+offset+1]*weights[offset-i:]) / np.sum(weights[offset-i:])

    for i in range(lend-offset+2,lend-1,-1):
        smoothed[i] = np.sum(x[i-offset:]*weights[0:offset+(lend-i)]) / np.sum(weights[0:offset+(lend-i)])

    return smoothed

def calculateAutocorrelation(oscillatingData):
    #this here is the actual correlation -> rest is just to crop down to
    #significant areas
    corrs2 = np.correlate(oscillatingData, oscillatingData, mode='same')
    #
    N = len(corrs2)
    corrs2 = corrs2[N // 2:]
    lengths = range(N, N // 2, -1)
    corrs2 /= lengths
    corrs2 /= corrs2[0]
    maxcorr = np.argmax(corrs2)
    corrs2 = corrs2 / corrs2[maxcorr]
    return corrs2

def scipyFit(data,tauGuess):
    y = data[1] 
    x = data[0]

    #self.__nearestIndex = (np.abs(y-0.0)).argmin()
    #self.__nearestIndex = self.find_first_index(y,0)
    #initA = np.amax(y)
    #initTau_acf = x[self.__nearestIndex]
    #initB = initA/20
    #arr = [initA,initB, initTau_acf]

    #bounds = ([initA - 0.1,initB/2, initTau_acf - 0.2], [initA + 0.1,initB*2, initTau_acf + 0.2])

    print("Initial Guess is "+str(tauGuess))

    arr = [1.0,tauGuess]



    popt, pcov = optimize.curve_fit(sinc, x, y,p0=arr)
    perr = np.sqrt(np.diag(pcov))
    print("a = '" + str(popt[0]) + " (" + str(perr[0]) + ")'")
    print("tau_acf = '" + str(popt[1]) + " (" + str(perr[1]) + ")'")

    return popt



input = "006144777_350"
input = "003744681_983"
powerSpectrum = False
filename = "../Sterndaten/RG_ENRICO/kplr" + input + "_COR_" + (
    "PSD_" if powerSpectrum else "") + "filt_inp.fits"
filterTime = 5

file = FitsReader(filename)

powerCalc = PowerspectraCalculator(file.getLightCurve())
powerCalc.setKicID(input)

#plotPSD(powerCalc,True,True)
#plotLightCurve(powerCalc)

lightCurve = file.getLightCurve()
lightCurve[0] -=lightCurve[0][0]

#set to seconds
lightCurve[0] *=3600*24
#find the new number of bins after the filter
elements = len(lightCurve[0])
duty_cycle = np.mean(lightCurve[0][1:elements -1] - lightCurve[0][0:elements
                                                                  -2])
normalized_bin = np.round(filterTime*24*3600/int(duty_cycle))
bins = int(elements/normalized_bin)

# Find out how many points are left
n_points_left = elements - normalized_bin*bins
index_shift = 0
n_cols = 1

if n_points_left > 1:
    factors=factorint(n_points_left,multiple=True)
    index_shift = factors[0]**factors[1]
    n_cols = int(n_points_left/index_shift + 1)
elif n_points_left == 1:
    n_cols = 2
    index_shift = 1

print("Index shift is "+str(index_shift))
print("n_cols is "+str(n_cols))


amp_mean_array = np.zeros(n_cols)

for k in range(0,n_cols):
    amp_rebin_array = np.zeros(int(elements-n_points_left))
    n_points_per_bin_array = np.zeros(int(elements-n_points_left))
    amp_substract_array = np.zeros(int(elements-n_points_left))

    i = k*index_shift

    for j in range(0,bins):
        bin_mean = 0.0
        ref_time = i
        count = 1

        while i < (elements-1) and (lightCurve[0][i] - lightCurve[0][ref_time])/(3600*24) <filterTime:
            bin_mean +=lightCurve[1][i]
            if lightCurve[1][i] != 0:
                count +=1
            i+=1

        bin_mean += lightCurve[1][i]
        if lightCurve[1][i] != 0:
            count +=1
        count_float = float(count)

        if count > 1:
            bin_mean /= (count_float-1)

        amp_rebin_array[ref_time - k*index_shift:(i-1)-k*index_shift] = bin_mean
        n_points_per_bin_array[ref_time - k*index_shift:(i-1) - k*index_shift] = count

    amp_substract_array = lightCurve[1][k*index_shift:k*index_shift+len(amp_rebin_array)] -amp_rebin_array
    amp_substract_array = amp_substract_array[n_points_per_bin_array>=normalized_bin/2]
    amp_mean_array[k] = np.mean(amp_substract_array)

amp_mean = np.mean(amp_mean_array)

print(amp_mean)

#Calculate Flicker Amplitude
amp_substract_array = np.unique(amp_substract_array)
amp_flic = 0
for i in range(0,len(amp_substract_array)):
    amp_flic +=(amp_substract_array[i] - amp_mean)**2
denominator = float(len(amp_substract_array))
amp_flic = np.sqrt(amp_flic/denominator)

print("Flicker amplitude is '"+str(amp_flic))

nu_filter = 10**(5.187)/(amp_flic**(1.560))
print("Nu filter is '"+str(nu_filter))
marker = {}
marker["InitialFilter"] = (nu_filter,"r")


tau_filter = 1/(nu_filter*10**-6)

print("Tau filter is "+str(tau_filter))

new_normalized_bin_size = int(np.round(tau_filter/duty_cycle))
print("New normalized bin size is "+str(new_normalized_bin_size))
amp_smoothed_array = trismooth(lightCurve[1],new_normalized_bin_size)
amp_filtered_array = lightCurve[1]-amp_smoothed_array

powerCalc2 = PowerspectraCalculator((lightCurve[0],amp_filtered_array))
powerCalc2.setKicID("test2")

#plotPSD(powerCalc,True,True,smooth = False)
#plotPSD(powerCalc2,True,True,smooth = False)

#Autocorrelation
length = 1.5*tau_filter*4/duty_cycle
if length > elements:
    length = 1.5*4/(10**-7*duty_cycle)-1
if length > elements:
    length = elements - 1

autocor = calculateAutocorrelation(amp_filtered_array)
autocor = autocor[0:int(length)]
autocor = autocor**2

#pl.plot(lightCurve[0][0:int(length)]/4,autocor)
#pl.show()

popt = scipyFit((lightCurve[0][0:int(length)]/4,autocor),tau_filter/55)

tau_first_fit = popt[1]/60

nu_filter = 10**(3.098)*1/(tau_first_fit**0.932)*1/(tau_first_fit**0.05)

print("New filter is '"+str(nu_filter))
marker["First filter"] = (nu_filter,"g")

nu_filter = nu_filter*10**-6
tau_filter = 1/nu_filter
print("Tau filter is "+str(tau_filter))

new_normalized_bin_size = int(np.round(tau_filter/duty_cycle))
print("New normalized bin size is "+str(new_normalized_bin_size))
amp_smoothed_array = trismooth(lightCurve[1],new_normalized_bin_size)
amp_filtered_array = lightCurve[1] - amp_smoothed_array

powerCalc3 = PowerspectraCalculator((lightCurve[0],amp_filtered_array))
powerCalc3.setKicID("Test3")

#plotPSD(powerCalc2,True,True,smooth = False)
#plotPSD(powerCalc3,True,True,smooth = False)

length = 1.5*tau_filter*4/duty_cycle
if length > elements:
    length = 1.5*4/(10**-7*duty_cycle)-1
if length > elements:
    length = elements - 1

autocor = calculateAutocorrelation(amp_filtered_array)
autocor = autocor[0:int(length)]
autocor = autocor**2


popt = scipyFit((lightCurve[0][0:int(length)]/4,autocor),tau_first_fit*30)

tau_filter = popt[1]/60

nu_filter = 10**(3.098)*1/(tau_filter**0.932)*1/(tau_filter**0.05)

marker["Second filter"] = (nu_filter,"b")


plotPSD(powerCalc,True,True,marker)

print("New filter is '"+str(nu_filter))


