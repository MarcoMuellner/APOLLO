import numpy as np
from scipy import optimize
import logging

logger = logging.getLogger(__name__)

def scipyFit(x, y, method,p0 = None,boundaries = ([-np.inf],[np.inf])):
    if boundaries is not None and len(boundaries) != 2:
        raise ValueError("Boundaries need to be a two 2D tuple")

    if p0 is not None and boundaries is not None and len(p0) != len(boundaries[0]) and boundaries != ([-np.inf],[np.inf]):
        raise ValueError("P0 and Fixed Array have to have the same length")
    popt, pcov = optimize.curve_fit(method, x, y,p0=p0,bounds = boundaries)
    perr = np.sqrt(np.diag(pcov))
    return popt, perr


def gaussian(x, y0, cen, wid):
    '''
    Fitting function used. Fits a Gaussian using the following function:
    .. math::
        y(x)=y_0+\frac{amp}{\sqrt{2\pi wid}}\text{exp}(-\frac{(x-cen)^2}{2*wid^2})
    :param x:x-Axis against which we will approximate the function
    :type x:1-D numpy array
    :param y0:y-Offset of the function
    :type y0:float
    :param amp:Amplitude of the gaussian
    :type amp:float
    :param cen:x-Value of center of distribution
    :type cen:float
    :param wid:Standard deviation of the distribution
    :type wid:float
    :return:y-Array of a gaussian distribution
    :rtype:1-D numpy array
    '''
    return y0 + (1 / (np.sqrt(2 * np.pi) * wid)) * np.exp(-(x - cen) ** 2 / (2 * wid ** 2))

def sinOffset(x,amp,tau,offset,phi):
    return offset+amp*np.sin(2*np.pi*x/tau+phi)


def linearPolynomial(x, a, b):
    return a + b * x

def exponentialDistribution(x,A,B,u):
    return A+B*np.exp(-x*u)*u


def quadraticPolynomial(x, a, b, c):
    return a + b * x + c * x ** 2

def sin(x,amp,tau):
    '''
    Represents the used sin within our Fit
    :type x: 1-D numpy array
    :param amp: Amplitude of sin
    :type amp: float
    :type tau: float
    :return: the functional values for the array x
    :rtype: 1-D numpy array
    '''
    return amp*np.sin(2*np.pi*4*x/tau)

def sinc(x, a, tau_acf):
    '''
    Represents the used sinc within our Fit
    :param x: 1-D numpy array
    :param a: float, amplitude of the sinc
    :param tau_acf: float
    :return: the functional value for the array x
    :rtype: 1-D numpy array
    '''
    return a * np.sinc(4 * x / tau_acf)**2

def trismooth(x,window_width):
    '''
    This function is implemented to create a similar function to the Trismooth function of idl
    :rtype: 1-D numpy array
    :type window_width: int
    :param x: The array containg the data which should be filtered. In our case this represents the Flux within the
              lightCurve
    :type x: 1-D numpy array
    :param window_width: The bin size which the function will look at
    :return: The smoothed variant of x
    '''
    if window_width%2 != 0:
        window_width = window_width+1

    lend = len(x)-1
    if (lend+1) < window_width:
        raise ValueError

    halfWeights = np.arange(window_width/2)
    weights = np.append(halfWeights,[window_width/2])
    weights = np.append(weights,halfWeights[::-1])
    weights +=1
    tot = np.sum(weights)

    smoothed = np.zeros(lend+1)
    offset = int(window_width/2)
    local = np.zeros(window_width)

    for i in range(offset,lend-offset):
        smoothed[i]=np.sum(x[i-offset:i+offset+1]*weights)

    smoothed /=tot

    for i in range(0,offset):
        smoothed[i] = np.sum(x[0:i+offset+1]*weights[offset-i:]) / np.sum(weights[offset-i:])

    for i in range(lend-offset,lend-1,-1):
        smoothed[i] = np.sum(x[i-offset:]*weights[0:offset+(lend-i)]) / np.sum(weights[0:offset+(lend-i)])

    return smoothed