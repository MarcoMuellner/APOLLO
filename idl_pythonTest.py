import numpy as np

def sin(x,amp,tau):
   return amp*np.sin(2*np.pi*4*x/tau)

def sinc(x,amp,tau):
    return amp*np.sin(4*np.pi*x/tau)
