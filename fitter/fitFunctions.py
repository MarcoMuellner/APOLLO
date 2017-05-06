import numpy as np
from scipy import optimize

def scipyFit(x,y,method):
    print(type(x),type(y))
    popt, pcov = optimize.curve_fit(method, x, y)
    perr = np.sqrt(np.diag(pcov))
    return popt,perr


def gaussian(x, y0, amp, cen, wid):
    return y0 + (amp / (np.sqrt(2 * np.pi) * wid)) * np.exp(-(x - cen) ** 2 / (2 * wid ** 2))

def linearPolynomial(x,a,b):
    return a+b*x

def quadraticPolynomial(x,a,b,c):
    return a+b*x+c*x**2

