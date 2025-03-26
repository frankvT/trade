# runmodel.py
#%% imports
import pe_model as mod
from kitchen import pretty_print
from plots import *       #plot_equil, plot_markets, opt_tar_plot
from basefuncs import elas

import sys
from pathlib import Path



#%% run model 
# NOTE: parameters are read from file in pe_model.py
# the parameter file to read is configured in init.json

t = mod.create_tar_instance(mod.TAR_type, mod.TAR_val)
res = mod.generate_markets()
eq, labels = mod.trademodel(t, Description=f"Large country model 1.({mod.SYSTEM})")

results_with_labels_dict = {k:(round(eq[k],3),labels[k]) for k in eq}

pw = res['pw'] # free trade price on home and world markets
pstar_t = eq['pstar_t']
pstar = eq['pstar'] 
w_home = mod.home_welf(pw, pstar_t, pstar)
w_fore = mod.foreign_welf(pw, pstar)
w_world = mod.world_welf(w_home, w_fore)


# elasticities
f1 =  lambda x: mod.expsup(x, t = 0)
elas_dict = {
            "Home demand" : elas(mod.homedem, pstar_t),
            "Home supply" : elas(mod.homesup, pstar_t),
            "Import demand" : elas(mod.impdem, pstar),
            "Export supply": elas(f1, pstar),
            }           


fig1 = plot_markets(res)
plot_equil(fig1, res, eq, 
           x_t = [mod.expsup(p, t=t) for p in res['p']],  # tariff-ridden export supply
           show= False)


#%% optimal tariff calculatiions and plots
# dict to hold various results for plotting
opt_tar_toplot = {'tar':[],
                  'rev':[],
                  'welf':[],
                  'dCS':[],
                  'dPS':[],
                  'ToT':[],
                  'tartype':'',
                  'AVE':[],
                  'unit':''}


valbase=0.0
tar = mod.create_tar_instance(mod.TAR_type, valbase)

opt_tar_toplot["tartype"] = tar.get_tartype()
opt_tar_toplot['unit'] = mod.home_welf.unit

base = mod.generate_markets()
m = base['m1'] # free trade imports
pw = base['pw'] # free trade price on home and world markets

eps = 1e-5
while m >= eps: # stop when imports become too small. In linlog model 0 is a problem
    eq, _ = mod.trademodel(tar, Description='Large country model 1')
    pstar_t = eq['pstar_t']
    m = eq['mstar']
    pstar = eq['pstar'] 

    if m < eps: break # to avoid furher calculations when imports are negative
       
    welf_res = mod.home_welf(pw, pstar_t, pstar)
    opt_tar_toplot['welf'].append(welf_res["total"])
    opt_tar_toplot['dCS'].append(welf_res["dCS"])
    opt_tar_toplot['dPS'].append(welf_res["dPS"])
    opt_tar_toplot['rev'].append(welf_res["dRev"])
    opt_tar_toplot['ToT'].append(welf_res["ToT"])
    opt_tar_toplot['tar'].append(tar.value)
    opt_tar_toplot["AVE"].append(tar.ave(pstar_t))
           
    tar.value +=0.01    

# plot results 
# tariff pedagogy
opt_tar_plot(opt_tar_toplot, key = 'welf', ylabel = 'Importer welfare')
opt_tar_plot(opt_tar_toplot, key='rev', ylabel = 'Tariff revenue')
opt_tar_plot(opt_tar_toplot, key='dCS', ylabel = 'Consumer welfare')
opt_tar_plot(opt_tar_toplot, key='dPS', ylabel = 'Producer surplus')
opt_tar_plot(opt_tar_toplot, key='ToT', ylabel = 'Terms of Trade')

# find optimal tariff (note: the plotting function does the same)
idx = opt_tar_toplot["welf"].index(max(opt_tar_toplot["welf"]))
opt_tar = opt_tar_toplot["tar"][idx]
opt_tar_ave = opt_tar_toplot["AVE"][idx]
opt_tar_welf = opt_tar_toplot["welf"][idx]

# If the weighst for the 3 welfare components are not equal, we get something different. 
# E.g put more weight on consumers and producers than on revenue: 
weights = np.array([4, 3, 2])
weights = weights/weights.sum() # to make sure they sum to unity

# weighted sum as product of matrix and vector of weights
welf_weighted =  np.array([opt_tar_toplot['dCS'],
                 opt_tar_toplot['dPS'],
                 opt_tar_toplot['rev']]).T@weights
                  
idx = np.where(welf_weighted == max(welf_weighted))[0][0]
opt_tar_ave_weighted = opt_tar_toplot["AVE"][idx]

def create_rep(txtfile=False, **kwargs):
      tmp_stdout = sys.stdout
      if txtfile == True:
            
            fname = kwargs["fname"]
            fullfname = Path(Path(__file__).parent) / f"{mod.TEXTPATH}/{fname}"
            try:
                  fullfname.unlink()
    
            except FileNotFoundError:
                  pass

      else:
            fullfname = ".My Screen"
            

      with open(fullfname, 'w') as file:
            if txtfile == True: 
                  sys.stdout = file
            
            print(f"\nEquilibrium results for {labels['Description']} with tariff {t.value} {t.get_tartype()}\n"
                  f"{pretty_print(results_with_labels_dict, fw=8, indent = 1)}")

            print(f"Equilibrium elasticities:\n {pretty_print(elas_dict)}")

            print(F"Welfare results for tariff: {t.value} {t.get_tartype()}:"\
                  f"\nAll in {mod.home_welf.unit}")
            
            print(f"Home\n{pretty_print(w_home)}")
            print(f"Foreign\n{pretty_print(w_fore )}")
            print(f"World\n{pretty_print(w_world)}")

            print(f"Optimal tariff: {opt_tar_toplot['tartype'].title()} {opt_tar:.2f}, "
            f"with an AVE of {opt_tar_ave:.0%}"
            f"\nWelfare outcome: {opt_tar_toplot['unit']} {opt_tar_welf:.2f}")
            print(f"\nNOTE: {opt_tar_toplot['tartype'].title()} means {tar.unit}\n")

            print(f"Optimal tariff for unequal weights (dCS, dPS, dRev): "
                  f"{[round(w,2) for w in weights]} "
                  f"AVE: {opt_tar_ave_weighted:.0%}"
                  f"\nWeighted welfare outcome: {max(welf_weighted):.2f}")

            print(f"\nModel parameters read from: {Path(mod.PARPATH/mod.PARFILE)}\n")
            print(f"A bunch of figures saved in: {FIGPATH}")
            print(f"And this report has made it to: {fullfname}")
            print('\n','*'*10, 'END','*'*10,'\n')

            sys.stdout = tmp_stdout

create_rep()   
create_rep(txtfile=True, fname = f"{mod.PARFILE.stem}_out.txt")   


# %%
