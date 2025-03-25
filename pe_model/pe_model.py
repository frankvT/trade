#%% simple_trade_2.py
'''
A simple trade model.

Follows textbook Feenstra and Taylor, 2008, International economics, chapter 8
It implements a 'large country' patrtial equilibrium model to illustrate
terms of trade effects and optimal tariffs.

Allows for log-linear equations
Allows for specific and ad-valorem tariffs 

FvT February 2025
'''
 
# imports 
import numpy as np
from pathlib import Path
import json

# import scipy modules for root finding and integration
from scipy import optimize
from scipy.integrate import quad

# local imports
from basefuncs import * # linfunc, linlogfunc, f_inv, funcs
import tariffs as tars 
from kitchen import pretty_print, set_unit
import init

PARPATH = init.PARPATH
PARFILE = init.PARFILE   
TEXTPATH = init.TEXTPATH
FIGPATH = init.FIGPATH

#############################################################
# INITIALIZE
#############################################################

# SYSTEM sets the type of functions used in demand and supply
# 'lin': all linear
# 'linlog': linear in logs, i.e. constant elasticities 
# DEFAULT parameters of the Marshalian demand and supply functions
# i.e. x = f(p)
DEFAULTS = {
            "SYSTEM": 'lin',
            "MONEY": 'Euros',
            "VOLUME": 'Tons',
            "TAR_type": 'Ave',
            "TAR_val": 0.2,
            "homedem_pars": {"const": 20,
                             "slope": -15 },
            "homesup_pars": {"const":-1,
                            "slope": 10},
            "forsup_pars": {"const": -2,
                            "slope": 15}
        }
SYSTEM = DEFAULTS["SYSTEM"]
MONEY, VOLUME = DEFAULTS["MONEY"], DEFAULTS["VOLUME"]
TAR_type, TAR_val = DEFAULTS["TAR_type"], DEFAULTS["TAR_val"]
homedem_pars, homesup_pars = DEFAULTS["homedem_pars"], DEFAULTS["homesup_pars"]
forsup_pars = DEFAULTS["forsup_pars"]


# read parameter file         
def read_parfile(fname):
    ''' reads params from json file'''
    try: 
        with open(fname, 'r') as openfile:
        # Reading from json file
            params_dict = json.load(openfile)
            print(f"****** Sucessfully read {fname}\n")
          
    except FileNotFoundError:
        print(f"*** OOPS: {fname} not found.\nReverting to defaults.")
        params_dict = DEFAULTS
    return params_dict

params_dict= read_parfile(PARPATH/ PARFILE)
#unpacks parameters dict
validkeys = ["SYSTEM", "MONEY", "VOLUME",
                 "TAR_type","TAR_val", 
                 "homedem_pars", "homesup_pars", "forsup_pars" 
                ]
try:
    SYSTEM = params_dict["SYSTEM"]
    MONEY, VOLUME = params_dict["MONEY"], params_dict["VOLUME"]
    TAR_type, TAR_val = params_dict["TAR_type"], params_dict["TAR_val"]
    homedem_pars, homesup_pars = params_dict["homedem_pars"], params_dict["homesup_pars"]
    forsup_pars = params_dict["forsup_pars"]
    
except KeyError:
    print(f"*** OOPS: necessary variable not found in {PARFILE}.\n"
                   f"Reverting to DEFAULTS.")
    
    SYSTEM = DEFAULTS["SYSTEM"]
    MONEY, VOLUME = DEFAULTS["MONEY"], DEFAULTS["VOLUME"]
    TAR_type, TAR_val = DEFAULTS["TAR_type"], DEFAULTS["TAR_val"]
    homedem_pars, homesup_pars = DEFAULTS["homedem_pars"], DEFAULTS["homesup_pars"]
    forsup_pars = DEFAULTS["forsup_pars"]


f = funcs[SYSTEM]['f']

################################################################
# helper functions
################################################################

def create_tar_instance(type, val):
    if type == 'Ave':
        t = tars.Ave(val)
    elif type == 'Specific':
        t = tars.Specific(val)   
    else: 
        t = 0.0     
    return t

def solve(func, init):
    # solves by searching root of function
    sol = optimize.root(func, x0=init)
    return sol

################################################################
# define equations
################################################################

@set_unit(VOLUME)
def homedem(p, pars=homedem_pars):
    ''' Returns domestic demand quantity as function of price p'''
    return f(p, **pars)


def homesup(p, pars=homesup_pars):
    ''' Returns domestic supply quantity as function of price p'''
    return f(p, **pars)

def impdem(p):
    '''returns demand for imports as function of price'''

    return homedem(p) - homesup(p)


def expsup(p, t:tars.Tariff, pars=forsup_pars):
    ''' Returns foreign supply quantity as function of 
    price p and tariff t'''
    if isinstance(t, tars.Tariff):
        p_tar = p*(1. - t.ave(p))
        
    else:
        p_tar  = p

    return f(p_tar , **pars)

def expprice(x):
    '''Inverse of expsup(p) returns foreign export price as function of 
    export volume x'''
    
    # Below lambda function is required to fix parameter t 
    # for the root finder in f_inv()

    # Alternatively use functools.partial() to hold constant the parameter t like so:
    # f_inv(partial(expsup, t=0), exo=x)
    
    f1 = lambda x: expsup(x, t = 0)
    return f_inv(f1, exo=x)



def home_notrade_equil():
    '''Returns no trade equilibrium in home market, i.e when 
        domestic demand equals domestic supply and hence impdem(p) = 0.
         Solves the intersection of D-S numerically'''
    
    equil = solve(impdem, init = homedem_pars["const"])
    p = equil.x
    q = homedem(p)
    return (p[0],q[0]) 


#%% generate results 

def generate_markets():
    '''generate some data to plot the demand and supply functions'''

    res = {'p':[], 'd':[], 's':[],'x':[], 'm':[], 'pw':0.0, 'm1':0.0}
           
    # find suitable range of prices to plot
    P0, Q0 = home_notrade_equil()
    
    # free trade equilibrium 
    def equil(p):                    
        return impdem(p) - expsup(p, t=0)
    eq = solve(equil, init=0.01)
    PW, m1 = eq.x[0], expsup(eq.x[0], t=0)
    
    alfa = 4 # ratio of largest and midpoint on home quantity axis
    beta = 3 # ratio of largest and midpoint on world quantity axis

    P1, P2 = f_inv(homedem, Q0*alfa), f_inv(homedem, Q0/alfa)
    P3, P4 = expprice(m1/beta), expprice(m1*beta)

    # finally, this is the price range that should work (mostly) 
    start, stop = max(min(P1,P3),1e-3), max(min(P2, P4),1e-3)
    
    numdat = 20    
    res['p'] = [p for p in np.linspace(start,stop, numdat)]
    res['d'] = [homedem(p) for p in res['p']]
    res['s'] = [homesup(p) for p in res['p']]
    res['m'] = [impdem(p) for p in res['p']]
    res['x'] = [expsup(p, t=0) for p in res['p']]
    
     
    res['pw'] = PW
    res['m1'] = expsup(res['pw'], t=0)
    res['s1'] = homesup(res['pw'])
    res['d1'] = homedem(res['pw'])
 
    return res

###########################################################################
# The PE model
###########################################################################

def trademodel(tariff:tars.Tariff, **kwargs):
    ''' The equations and solution of the model '''

    exog = {'tariff': tariff.value}

    endo = {'pstar_t': 0.0,
            'pstar': 0.0,
            'mstar': 0.0,
            'xstar': 0.0,
            'dstar': 0.0,
            'sstar': 0.0,
            'P0':0,
            'Q0':0}
    
    desc = {'pstar_t': 'tariff-inclusive price on home market',
            'pstar': 'price received by exporter',
            'mstar': 'import quantity',
            'xstar': 'export quantity',
            'dstar': 'domestic demand quantity',
            'sstar': 'domestic supply quantity',
            'tariff': str(tariff),
            'P0': f'Price at home no-trade equilibrium ({MONEY})',
            'Q0': f'Quantity at home no-trade equilibrium ({VOLUME})',
            }
    if kwargs: 
        for k, v in kwargs.items():
            desc[k] = v
    
    t = tariff
    
    '''Equilibrium condition 
    It clears domestic and foreign markets:
    M(p) = D(p) - S(p)  
    M(p) = X(p,t)
    so that (D - S - X) = 0 yields the tariff-ridden price. 
      Solves numerically'
    '''
    def equil(p):                           # eqilibrium condition
        return impdem(p) - expsup(p, t)
    
    eq = solve(equil, init=0.01)
    pstar_t = eq.x[0]                      # equilibrium tariff-inclusive price
    xstar = expsup(pstar_t, t=t)           # export quantity 

    endo['pstar_t'] = pstar_t              
    endo['xstar'] = xstar
    endo['pstar'] = expprice(xstar)        # price received by exporter
    endo['mstar'] = impdem(pstar_t)        # imports
    endo['dstar'] = homedem(pstar_t)       # doemstic demand
    endo['sstar'] = homesup(pstar_t)       # domestic supply

    endo['P0'], endo['Q0'] = home_notrade_equil() # autarky solution

    return endo, desc


################################################################
# welfare calculations
################################################################
   
@set_unit(MONEY)
def home_welf(p0, p_t, pstar):
    ''' Returns a dict with the components of changes in domestic welfare
    relative to a an initial situation characterized by p0 
    (typically a free trade solution)
     p0:   base price
     P_t:  tariff-ridden domestic price
     pstar: price received  by foreign exporter
    '''

    # change consumer surplus: negative of area under demand cuve
    d_cs = -quad(homedem, p0, p_t)[0] 

    # approx Hicksian EV and CV, see Deaton & Muellbauer
    ev = -(p_t - p0) * homedem(p_t)  
    cv = -(p_t - p0) * homedem(p0)

    # change producer surplus: area above inverse supply curve  = area below 
    # original curve
    #
    d_ps = (quad(homesup, p0, p_t)[0])
    
    # terms of trade effect
    tot = (p0 - pstar) * impdem(p_t)  
    # tariff revenues
    rev = (p_t - p0) * impdem(p_t)
    
    # collect results 
    welf = {}
    welf["dCS"] = d_cs
    welf["dPS"] = d_ps
    welf["dRev"] = rev
    # deadweight loss: net of consumer loss and producer gains and gov revenue
    welf["DW"] = welf["dCS"] +  welf["dPS"] + welf["dRev"]
    welf["ToT"] = tot
    welf["total"] = welf["dCS"] + welf["dPS"] + welf["dRev"] + welf["ToT"]
    welf["EV"] = ev
    welf["CV"] = cv
    return welf

def foreign_welf(p0, pstar):
    # ToT loss
    # producer surplus loss
    f1 = lambda x: expsup(x, t = 0)
    d_ps = (quad(f1, p0, pstar)[0])
    welf = {}
    welf['ToT'] = -(p0 - pstar) * expsup(pstar, 0) 
    welf['dPS'] = d_ps

    return welf

def world_welf(w_home, w_foreign):
    welf = {}
    welf['dCS_h'] = w_home['dCS']
    welf['dPS_h'] = w_home['dPS']
    welf['dRev_h'] = w_home['dRev']
    welf['ToT_h'] = w_home['ToT']
    welf['Net Home'] = welf['dCS_h'] + welf['dPS_h'] + welf['dRev_h']\
                    + welf['ToT_h']
    
    welf['dPS_f'] = w_foreign['dPS']
    welf['ToT_f'] = w_foreign['ToT']
    welf['Net Foreign'] = welf['dPS_f'] + welf['ToT_f']

    welf['Net WORLD'] = welf['Net Home'] + welf['Net Foreign']
 
    return welf


#%% Trial run the model 

t = create_tar_instance(TAR_type, TAR_val)
res = generate_markets()
eq, labels = trademodel(t, Description='Large country model trial run')

results_with_labels_dict = {k:(round(eq[k],3),labels[k]) for k in eq}

print('*'*20)
print(f"Trial run\n{labels['Description']} with tariff {t.value} {t.get_tartype()}\n"
      f"{pretty_print(results_with_labels_dict, fw=8, indent = 1)}")
print('*'*20)

