#plots.py
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from pathlib import Path
import numpy as np

import init
FIGPATH = init.FIGPATH

font = {'size': 12, 'family' : 'sans-serif'}
plt.rc('font', **font)



def get_offset(ax, dx, dy):
        dp_to_dd = ax.transData.inverted().transform([dx,dy]) \
                   - ax.transData.inverted().transform([0,0])  
        return dp_to_dd

def plot_markets(res):
    fig, (homeax, worldax) = plt.subplots(1,2,layout='tight', sharey= True, sharex=False,
                                          num=1)
    plt.subplots_adjust(left = 0.15, right=0.99, bottom=0.2, wspace=0.)

    homeax.set_ylabel("Price", rotation = 0, 
                  loc = 'top')
    homeax.set_xlabel("Quantity", rotation = 0, loc = 'right')

    # set up the plot
    homeax.spines[['right', 'top']].set_visible(False)
    worldax.spines[['right', 'top']].set_visible(False)

        
    # plot the functions
    l1 = homeax.plot(res['d'], res['p'], label = 'D')
    l2 = homeax.plot(res['s'], res['p'], label = 'S')

    l1_XY = np.max(l1[0].get_xydata(), axis=0) # end of the line 
    l2_XY = np.max(l2[0].get_xydata(), axis = 0)

    homeax.set_xlim(0, max(l1_XY[0]*1.1, l2_XY[0])*1.1)
    homeax.set_ylim(0, l2_XY[1]*1.1)

    # reduce axis tick labels for clarity
    homeax.xaxis.set_major_locator(ticker.FixedLocator([0,int(homeax.get_xlim()[1])]))
    homeax.yaxis.set_major_locator(ticker.FixedLocator([0,int(max(res['p']))]))

    l3 = worldax.plot(res['m'], res['p'])
    l4 = worldax.plot(res['x'], res['p'])

    l3_XY = np.max(l3[0].get_xydata(), axis = 0)
    l4_XY = np.max(l4[0].get_xydata(), axis = 0)

    worldax.set_xlim(0,max(l3_XY[0]*1.1, l4_XY[0])*1.1)

    worldax.xaxis.set_major_locator(ticker.FixedLocator([0,int(worldax.get_xlim()[1])]))

    # plot dashed horizontal and vertical lines 
    worldax.hlines(res['pw'], 0, res['m1'], ls='--')
    worldax.vlines(res['m1'], worldax.get_ylim()[0], res['pw'], ls='--')

    homeax.hlines(res['pw'], 0, homeax.get_xlim()[1], ls='--')
    homeax.vlines(res['s1'], homeax.get_ylim()[0], res['pw'], ls='--')
    homeax.vlines(res['d1'], homeax.get_ylim()[0], res['pw'], ls='--')

    # put text labels 
    homeax.set_title('Home Market')
    worldax.set_title('World Market')

    homeax.text(max(res['d'])*1.01, min(res['p']), 'D', ha = 'left')
    homeax.text(max(res['s'])*1.01, max(res['p']), 'S', ha = 'left')
    worldax.text(max(res['m'])*1.01, min(res['p']), 'M', ha = 'left' )

    
    worldax.text(max(res['x']) *1.01, max(res['p']), 'X', ha = 'left' )

    # offset from axes to avoid label clutter
    fs = plt.rcParams['font.size']
    xoff, yoff = get_offset(homeax, dx=fs, dy=fs) 

    homeax.annotate(r'$P^w$',
                    xy = (0,res['pw']),
                    xytext = (-xoff*3, res['pw']), textcoords='data')
    
    homeax.text(res['d1'], -yoff, r'$D_1$', ha = 'center', va='top')
    homeax.text(res['s1'], -yoff, r'$S_1$', ha = 'center' ,va='top')

    worldax.text(res['m1'],-yoff, r'$M_1 = D_1 - S_1$', va='top')
    
    
    figpath = FIGPATH / str(init.PARFILE.stem +'_fig1a.svg')
    plt.savefig(figpath, dpi=100)
    print(f"Figure 'markets' saved as: {figpath} ")
    
    return fig


def plot_equil(figure, res, eq, x_t=[], show=False):
    x_t_toplot = x_t
    fs = plt.rcParams['font.size']
    
    axes = figure.get_axes()
    homeax, worldax = axes[0], axes[1]
  
    xoff, yoff = get_offset(homeax, dx=fs, dy=fs) 

    # tariff-ridden export supply
    worldax.plot(x_t_toplot, res['p'], color = 'red')

    worldax.hlines(eq['pstar'], 0, eq['xstar'], ls='--', color='red')
    worldax.hlines(eq['pstar_t'], 0, eq['xstar'], ls='--', color='red')
    worldax.vlines(eq['xstar'],0, eq['pstar_t'], ls ='--', color = 'red')
    worldax.text(max(x_t_toplot), max(res['p']), r'$X^*$', ha='left', va='bottom')

    homeax.hlines(eq['pstar'], 0, homeax.get_xlim()[1], ls='--', color='red')
    homeax.hlines(eq['pstar_t'], 0, homeax.get_xlim()[1], ls='--', color='red')


    homeax.text(-xoff*3,eq['pstar'],r'$P^*$')
    homeax.text(-xoff*3.5,eq['pstar_t'],r'$P^{*+t}$', va='bottom')

    homeax.vlines(eq['sstar'], 0, eq['pstar_t'], ls ='--', color = 'red')
    homeax.vlines(eq['dstar'], 0, eq['pstar_t'], ls ='--', color = 'red')
    homeax.text(eq['sstar'], -yoff, r"$S_2$", ha='center', va='center', color = 'red')

    homeax.text(eq['dstar'], -yoff, r"$D_2$", ha='center', va='center', color = 'red')

    worldax.text(eq['xstar'], -yoff, r"$X_2$", ha = 'center', va='center', color = 'red')
    
    
    figpath = FIGPATH / str(init.PARFILE.stem +'_fig1b.svg')
    plt.savefig(figpath, dpi=100)
    print(f"Figure 'markets equilibrium'saved as: {figpath} ")

    if show == True:
        plt.show()


# optimal tariff plot
def opt_tar_plot(opt_tar_toplot, key = 'welf', ylabel='Importer welfare',
                 show = False):
    '''Plots change in one welfare component against tariffs.
    E.g. total domestic welfareor traiff revenues
    
    Assumes opt_tar_toplot is a dict. 
     opt_tar_toplot = {'tar':[],
                  'rev':[],
                  'welf':[],
                  'tartype':'',
                  'AVE':[],
                  'unit':''}
    REQUIRED keys: tar, tartype, AVE, unit.
    At least one plotable series in the keys, e.g. 'welf'   

    '''

    # set up the figure 
    fig, ax = plt.subplots(layout='tight')
    plt.subplots_adjust(left=0.1, right=0.9)

    ax.spines[['right', 'top']].set_visible(False)
    ax.spines['bottom'].set_position(('data',0))
    ax.set_ylabel(f"\nChange\n{ylabel}\n({opt_tar_toplot['unit']})", rotation = 0, 
                  loc = 'top')
    ax.yaxis.set_major_formatter('{x:0.1f}')
    ax.set_xlabel(f"Tariff\n({opt_tar_toplot['tartype']})", loc = 'right')

    # get offsets to position annotations
    fs = plt.rcParams['font.size']
    xoff, yoff = get_offset(ax, dx=fs, dy=fs) 

    # plot the data 
    ax.plot(opt_tar_toplot['tar'], opt_tar_toplot[key])
    ylims = ax.get_ylim()
    
    # find optimal tariff, ployt anad annotate
    max_dat = max(opt_tar_toplot[key])
    min_dat = min(opt_tar_toplot[key])
    idx = opt_tar_toplot[key].index(max_dat)
    opt_tar = opt_tar_toplot["tar"][idx]

    ax.plot(opt_tar, max_dat, 'o')
    
    bbox = dict(boxstyle="round", fc="0.8") #0.8
    arrowprops = dict(
    arrowstyle="->",
        connectionstyle="angle,angleA=0,angleB=90,rad=10")

    
    ax.vlines(opt_tar, 0, max_dat, ls= '--')

    _ave = opt_tar_toplot['AVE'][opt_tar_toplot["tar"].index(opt_tar)]
    ax.annotate(f"Optimal\ntariff {opt_tar:.2f}\n(AVE={_ave:.0%}))",
                    xy = (opt_tar, max_dat),
                    xytext = (opt_tar+5*xoff, ylims[1]), textcoords='data',
                    bbox=bbox, arrowprops=arrowprops)

    # plot and annotate prohibitive tariff 
    ax.plot(max(opt_tar_toplot['tar']), min_dat, 'o', color = 'red')

    prohib = max(opt_tar_toplot['tar'])
    _ave = opt_tar_toplot['AVE'][opt_tar_toplot["tar"].index(prohib)]

    ax.annotate(f"Prohibitive\ntariff {prohib:.2f}\n(AVE={_ave:.0%})",
                    xy = (prohib, min_dat), xycoords = 'data',
                    xytext = (2.5+0.3 +fs, 2.5+fs ), textcoords='offset points',
                              bbox=bbox, 
                              arrowprops={"arrowstyle":"->"})
    
    # annotate free trade solution
    ax.annotate("Free trade",
                xy = (0,opt_tar_toplot[key][0]), xycoords='data',
                # points from xy to always position correctly relative to spines: the y coord is 
                # fontsize + padding of ticklabels(3.5) + padding of bbox(0.3) + fontsize + fontsize
                xytext = (1.5, -((fs+3.5)+ 0.3 +fs + fs)), textcoords='offset points', 
                                bbox=bbox, arrowprops={"arrowstyle":"->"} 
                )
    
    figpath = FIGPATH / str(init.PARFILE.stem +f'_{ylabel}.svg')
    plt.savefig(figpath, dpi=100)
    print(f"Figure optimal tariff {ylabel} saved as: {figpath} ")

    if show == True:
        plt.show()
   
    