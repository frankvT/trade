# basefuncs.py 
"""Template definitions of functions"""

from scipy import optimize
import numpy as np

def linfunc(x, const, slope)-> float:
    '''Returns f(x_) = const + slope * x'''
    return const + slope * x
   
def linlogfunc(x, const, slope)-> float:
    '''Returns levels. f(x) = const^slope'''
    if x > 0: 
        return const * x**slope
    else:
        return 1e-6
        

    
def f_inv(f, exo):
    ''' returns inverted function by using numerical root finding
    y = f(x) => x = f^-1(y)
    e.g. if y = f(X) 
    f_inv(f, exo=10) finds the value of X for which y = 10 
    
    Parameters:
    f : a function 
    exo: the targeted exogenous value of f(x)  

    Returns: 
    x : float
    '''
    eps = 1e-6

    def func(*args, **kwargs):
        return exo - f(*args, **kwargs)
            
    inv = optimize.root(func, x0 = eps)
    
    return inv.x[0]


funcs = {'lin': {'f': linfunc},
          'linlog': {'f': linlogfunc}
        }    


def elas(func, x):
    '''calculates elasticity of func at point x'''
    dx_x = 0.001
    dz = np.gradient([func(x*(1-dx_x)), func(x), func(x*(1+dx_x))])
    el = dz[0]/func(x)*(1/dx_x)
    return el 