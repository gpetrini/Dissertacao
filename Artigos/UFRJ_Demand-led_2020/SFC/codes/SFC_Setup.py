###################### Packages ############

from pysolve3.model import Model
from pysolve3.utils import SolveSFC, ShockModel, SummaryShock, SFCTable

from datetime import datetime
t1 = datetime.now()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import seaborn as sns
import networkx as nx
import sympy as sp
from sympy import pprint, cse

import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed, interact_manual

from scipy.stats import yeojohnson

plt.style.use('seaborn-white')

import pandas_datareader.data as web
start = datetime(1987, 1, 1)
end = datetime(2018, 12, 31)

################## Model Class ################

def model(
    alpha = 0.5,
    gamma_F = 0.08,
    gamma_u = 0.09,
    g_Z = 0.025,
    omega = 0.5,
    rm = 0.01,
    spread_l = 0,
    spread_mo = 0,
    un = 0.8,
    v = 1.2,
    phi_0 = 0.025,
    phi_1 = 0.1,
    infla = 0.0,
    phparam=1.0,
    R = 0.7,
    real = -1,
    gC = 0.025
):
  """
  phparam: 1.0 means no inflation
  """
  model = Model()
  model.set_var_default(0) 
  model.var('C', desc='Consumption')
  model.var('Cw', desc='Workers Consumption', default=112)
  model.var('Ck', desc='Capitalist Consumption', default=68)
  model.var('FD', desc='Distributed profits')
  model.var('Fn', desc='Net profits')
  model.var('FT', desc='Total Profits')
  model.var('FU', desc='Retained profits')
  model.var('gk', desc='Capital growth rate')
  model.var('g_Z', desc='Autonomous grouth rate')
  model.var('h', desc='Marginal propensity to invest (non-residential)', default=0.03)
  model.var('I_t', desc='Investment', default = 100) # 200
  model.var('I_f', desc='Non-residential investment') # 100
  model.var('I_h', desc='Residential investment', default = 100) # 100
  model.var('Is', desc='Residential investment (Supply)', default = 100) # 100
  model.var('K_HS', desc='Houses supply', default=500) # 500
  model.var('K_HD', desc='Houses demand', default=500) # 500
  model.var('K_f', desc='Non-residential capital', default = 1000) # 10000
  model.var('Knom', desc='Nominal Capital', default=1500)
  model.var('K', desc='Real Capital', default=1500)
  model.var('K_k', desc="% of Kf in total")
  model.var('K_kr', desc="nominal % of Kf in total")
  model.var('L', desc='Total Loans') # 100
  model.var('Lf', desc='Firms Loans') # 100
  model.var('Lk', desc='Capitalist Loans') # 100
  model.var('M', desc='Money deposits') # 300
  model.var('M_h', desc='Households deposits')
  model.var('MO', desc='Mortgages') # 200
  model.var('NFW_h', desc='Households Capitalist Net Financial Wealth')
  model.var('NFW_hw', desc='Workers Net Financial Wealth', default=0)
  model.var('NFW_f', desc='Firms Net Financial Wealth')
  model.var('NFW_b', desc='Banks Net Financial Wealth')
  model.var('own', desc='Own interest rate')
  model.var('ph', desc='House price', default = 1)
  model.var('rl', desc='Interests rates on loans')
  model.var('rmo', desc='Interests rates on mortgages')
  model.var('S_hw', desc='Workers savings')
  model.var('S_hk', desc='Capitalist savings')
  model.var('u', desc='Capacity utilization ratio', default=0.7)
  model.var('V_h', desc='Household net nominal wealth')
  model.var('V_hr', desc='Household net real wealth')
  model.var('V_f', desc='Firms net wealth')
  model.var('V_b', desc='Banks net wealth')
  model.var('W', desc='Wages')
  model.var('Y', desc='GDP', default=280)
  model.var('Yk', desc='Capacity', default=1100)
  model.var('YDw', desc='Workers disposable income')
  model.var('YDk', desc='Capitalists disposable income')
  model.var('Z', desc='Autonomous expenditures')
  
  model.param('alpha', desc='Propensity to consume out of wages', default=alpha)
  model.param('gamma_F', desc='% of undistributed profits', default=gamma_F)
  model.param('gamma_u', desc='Adjustment parameter for the marginal propensity to invest', default=gamma_u) # 0.01
  model.param('omega', desc='Wage-share', default = omega)
  model.param('rm', desc='Interest rates on money deposits', default=rm) # 0.02
  model.param('spread_l', desc='Spread for loans', default=spread_l)
  model.param('spread_mo', desc='Spread for mortgages', default=spread_mo)
  model.param('un', desc='Normal capacity utilization ratio', default=un)
  model.param('v', desc='Capitl-Output ratio', default=v)
  model.param('phi_0', desc='Autonomous housing investment component',default = phi_0)
  model.param('phi_1', desc='Housing investment sensitivity to own interest rate', default = phi_1)
  model.param('R', desc='Autonomous ratio', default=R)
  model.param('infla', desc='infla value', default = infla)
  model.param('gC', desc='Autonomous consumption growth rate', default = gC)
  model.param('real', desc='Real data flag. True > 0. False < 0', default = real)  
  
  # General equations
  model.add('C = Cw + Ck')
  model.add('I_t = I_f + I_h') # Eq2
  model.add('Yk = K_f(-1)/v') # Eq 4
  model.add('u = Y/Yk') # Eq 5
  model.add('W = omega*Y') # Eq 6
  model.add('gk = h*u/v') # Eq 7
  model.add('Knom = K_HD*ph + K_f') # Eq 8 
  model.add('K = K_HD + K_f') # Eq 8 
  model.add('Z = I_h + Ck') # Eq 9
  model.add('Y = C + I_t') # Eq1
  
  # Workers equations
  model.add('Cw = alpha*W') # Eq 14
  model.add('YDw = W') # Eq 10
  model.add('S_hw = YDw - Cw') # Eq 11
  model.add('NFW_hw = S_hw')
    
  # Capitalist equations
  model.add('YDk = FD + rm*M_h(-1) - rmo*MO(-1) - rl*Lk(-1)')
  
  model.add('Ck = if_true(real>0)*(1+gC)*Ck(-1) + if_true(real<0)*R*Z')
  model.add('S_hk = YDk - Ck') # Eq 11
  model.add('d(MO) = I_h') # Eq 12
  model.add('d(Lk) = Ck')
  model.add('d(M_h) = S_hk + d(Lk)')
  model.add('V_h =  M_h  + K_HD*ph - MO - Lk') # Eq 15 
  model.add('V_hr =  M_h  + K_HD - MO - Lk') # Eq 15 
  model.add('NFW_h = S_hk - I_h') # Eq 16
  
  # Firms
  model.add('d(Lf) = I_f - FU') # Eq 15
  model.add('FT = (1-omega)*Y') # Eq 16
  model.add('Fn = FT -rl*Lf(-1)')
  model.add('FU = gamma_F*(Fn)') # Eq 17
  model.add('FD = (1 - gamma_F)*(Fn)') # Eq 18
  model.add('I_f = h*Y') # Eq 19
  model.add('d(K_f) = I_f') # 20
  model.add('h = h(-1)*gamma_u*(u-un) + h(-1)') # Eq 21 # Version without corridor
  model.add('V_f = K_f - Lf') # Eq 22
  model.add('NFW_f = FU - I_f') # Eq 23
  
  # Banks
  model.add('rmo = (1+spread_mo)*rm') # Eq 25
  model.add('rl = (1+spread_l)*rm') # Eq 26
  model.add('NFW_b = rl*L(-1) + rmo*MO(-1) - rm*M(-1)') # Eq 28
  model.add('V_b = L + MO - M') # Eq 27
  model.add('d(L) = d(Lf) + d(Lk)')
  model.add('d(M) = d(M_h)')
  
  
  # Residential investment
  model.add('K_HS = K_HD') # Eq 29
  model.add('Is = I_h')
  model.add('d(K_HD) = I_h') # Eq 30
  model.add('I_h = (1+g_Z)*I_h(-1)') # Eq 31
  model.add('K_k = K_HD/K') 
  model.add('K_kr = K_k*ph') 
  model.add('ph =(1+infla)*ph(-1)')
  model.add('own = ((1+rmo)/(1+infla)) -1')  
  model.add('g_Z = phi_0 - phi_1*own') 
  
  #model.var('Residual', desc='Unecessarily equation. Should be zero')
  #model.add('Residual = d(L) + d(MO) - d(M)') # Change!
  
  return model


################# Plot Functions #############
def clock_plots(shock, filename, variable):
    shock["TIME"] = [i+1 for i in range(len(shock.index))]
    shock["Ih/Y"] = shock["I_h"]/shock["Y"]
    shock["I/Y"] = shock["I_t"]/shock["Y"]
    shock["Z/Y"] = shock["Z"]/shock["Y"]
    shock["gY"] = shock["Y"].pct_change()
    
    sns.set_context('talk')
    fig, ax = plt.subplots(1,3,figsize=(24,5)
                          )
    
    sns.scatterplot(y = 'Ih/Y', x='u', data=shock, size="TIME", sizes = (1,200), 
                    color = 'black', legend=False, ax=ax[0])
    sns.lineplot(y = 'Ih/Y', x='u', data=shock, sort=False, color = 'black', ax=ax[0])
    ax[0].set_title("(A) Residential investment share on GDP\n VS. Capacity utilization ratio")
    
    sns.scatterplot(y = 'Z/Y', x='u', data=shock, size="TIME", sizes = (1,200), color = 'black', legend=False, ax=ax[1])
    sns.lineplot(y = 'Z/Y', x='u', data=shock, sort=False, color = 'black', ax=ax[1])
    ax[1].set_title("(B) Autonomous Expenditure share\n VS Capacity utilization")
    
    sns.scatterplot(y = 'I/Y', x='gY', data=shock, size="TIME", sizes = (1,200), color = 'black', legend=False, ax=ax[2])
    sns.lineplot(y = 'I/Y', x='gY', data=shock, sort=False, color = 'black', ax=ax[2])
    ax[2].set_title("(C) Total investment share\n VS GDP growth rate")
    
    
    sns.despine()
    plt.show()
    
    fig.savefig("../figs/" + filename, dpi = 600)

def plot_shock(filename, shock, df):
    """
    This function plots some selected variables
    
    filename: name to save the plot (str)
    shock: df returned by ShockModel function
    """
    sns.set_context('talk')
    fig, ax = plt.subplots(2,2, figsize=(16,10))

    shock[["Y"]].pct_change().plot(
        title = "Growth rates", ax = ax[0,0], 
        ls = ('--'), lw=3,
    )
    shock[["K"]].pct_change().plot(
        title = "Growth rates", ax = ax[0,0], 
        ls = (':'), lw=3
    )
    shock[["I_h"]].pct_change().plot(
        title = "Growth rates", ax = ax[0,0], 
        ls = ('-'), lw=3,
    )
    shock[["I_f"]].pct_change().plot(
        title = "Growth rates", ax = ax[0,0], 
        ls = ('-.'), lw=3,
    )
    ax[0,0].axhline(y=shock["g_Z"].iloc[-1], color = "black", ls = "--", lw=2.5)
    #ax[0,0].set_yticklabels(['{:,.1%}'.format(x) for x in ax[0,0].get_yticks()])
    ax[0,0].legend(loc='upper center', bbox_to_anchor=(0.5, -0.06),
                   labels = ["$Y$", "$K$", "$I_h$", "$I_f$"],
              fancybox=True, shadow=True, ncol=2)
    ax[0,0].ticklabel_format(useOffset=False)

    ((shock["Z"]/shock['Y'])).plot(
        title = "Autonomous expenditures share on GDP", ax = ax[0,1], ls = ('-'), lw=3, color='darkred')
    
    ax[0,1].set_ylim(auto=True)
    ax[0,1].legend(loc='upper center', bbox_to_anchor=(0.5, -0.08),
                   labels=['$Z/Y$'],
              fancybox=True, shadow=True, ncol=2)

    shock['u'].plot(title = 'Capacity utilization ratio', ax=ax[1,0], legend = False, color = "darkred", lw = 3, )
    ax[1,0].axhline(y = shock['un'].iloc[-1], ls ='--', color = "gray")
    #ax[1,0].set_yticklabels(['{:,.2%}'.format(x) for x in ax[1,0].get_yticks()])
    ax[1,0].ticklabel_format(useOffset=False)

    shock['h'].plot(title = 'Marginal propensity to invest', ax=ax[1,1], legend = False, color = "darkred", lw = 3, )
    ax[1,1].axhline(y = df['h'].iloc[-1], ls ='--', color = "gray")
    ax[1,1].ticklabel_format(useOffset=False)
    
    sns.despine()
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

    fig.savefig("../figs/" + filename, dpi = 600)

def plot_norms(filename, shock, df):
    """
    This function plots some selected variables
    
    filename: name to save the plot (str)
    shock: df returned by ShockModel function
    """
    sns.set_context('talk')
    fig, ax = plt.subplots(2,2, figsize=(16,10))

    ((shock["YDk"]/shock['V_h'])**(1)).plot(title = "Flow/Stock", ax = ax[0,0], ls = (':'), lw=3)
    ((shock["YDk"]/shock['V_hr'])**(1)).plot(ax = ax[0,0], ls = ('-'), lw=3)
    ((shock["FU"]/shock['V_f'])**(1)).plot(ax = ax[0,0], ls = ('-'), lw=3)
    
    ax[0,0].set_yticklabels(['{:,.1%}'.format(x) for x in ax[0,0].get_yticks()])
    ax[0,0].legend(loc='upper center', bbox_to_anchor=(0.5, -0.08),
                   labels = [
                       "$YDk/V_{hk}$",
                       "$YDk/V_{hkr}$",
                       "$FU$/V_f",
                            ],
              fancybox=True, shadow=True, ncol=2)
    #ax[0,0].ticklabel_format(useOffset=False)
    
    shock['K_k'].plot(color = "darkred", 
                      title = "Housing share on\nTotal Capital Stock", 
                      label = "$\k$", legend = False, ax = ax[0,1], lw = 3, )
    ax[0,1].axhline(y = df['K_k'].iloc[-1], ls ='--', color = "gray")
    ax[0,1].ticklabel_format(useOffset=False)
    
    (shock["MO"]*shock["rmo"][1:]/shock['YDk'][1:]).plot(
        title="Debt service on\nDisposable income", ax = ax[1,0], ls = ('-'), lw=3)
    ((shock["Lk"]*shock["rl"][1:])/shock['YDk'][1:]).plot(ax = ax[1,0], ls = ('-'), lw=3)
    ((shock["MO"]*shock["rmo"][1:] + shock["Lk"]*shock["rl"][1:])/shock['YDk'][1:]).plot( ax = ax[1,0], ls = ('-'), lw=3)
    ax[1,0].set_yticklabels(['{:,.1%}'.format(x) for x in ax[1,0].get_yticks()])
    ax[1,0].legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
                   labels = [
                       'Mortgage',
                       'Loans',
                       'Total'
                            ],
              fancybox=True, shadow=True, ncol=2)
    
    (shock['FT']/shock['K_f']).plot(ax=ax[1,1], label='Gross profit rate')
    (shock['Fn']/shock['K_f']).plot(ax=ax[1,1], label='Net profit rate')
    ax[1,1].set_yticklabels(['{:,.1%}'.format(x) for x in ax[1,0].get_yticks()])
    ax[1,1].legend()

    
    sns.despine()
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()
    
    fig.savefig("../figs/" + filename, dpi = 300)

def other_plots(shock, df):

    (shock['MO']/(shock['M'])).plot(title="Mortgage as % of deposits")
    sns.despine()
    plt.show()
    
    fig, ax = plt.subplots()
    (shock['FT']/shock['K_f']).plot(ax=ax, label='Gross profit rate')
    (shock['Fn']/shock['K_f']).plot(ax=ax, label='Net profit rate')
    ax.legend()
    sns.despine()
    plt.show()
    
    fig, ax = plt.subplots()
    (shock['YDk']/shock['K_HD']).plot(ax=ax, label='Real', title="Disposible income as % of Housing")
    (shock['YDk']/(shock['K_HD']*shock['ph'])).plot(ax=ax, label='Nominal')
    ax.legend()
    sns.despine()
    plt.show()
    
    fig, ax = plt.subplots()
    (shock['NFW_h']/(shock['Lk'] + shock['MO']) - (shock['rm'] - shock['g_Z'])).plot(title = 'Household debt stability',ax=ax)
    ax.axhline(y = ((df['NFW_h']/(df['Lk'] + df['MO'])) - (df['rm'] - df['g_Z'])).iloc[-1], ls ='--', color = "gray")
    
    sns.despine()
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()
    
    fig, ax = plt.subplots(1,1, figsize=(8,5))

    shock[["MO", "L"]].apply(lambda x: x/(shock["MO"] + shock['L'])).plot(kind = "area",stacked = True ,title = "Credit (as % Passives)", ax=ax)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.axhline(y = 1, color = "black", ls = "--")
    ax.axhline(y = 0, color = "black", ls = "--")
    
    sns.despine()
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

##################################### SOBOL ##################
def sobol(
    parameters,
    bound = np.linspace(0,1,101),
    time = 10,
    skip = 10,
    filename="Sobol.eps",
    var = "u"
):
    t2 = datetime.now()
    bound = bound
    df = pd.DataFrame()
    empty_list = [i for i in range(len(bound))]  
    
    for param in parameters:
        for i in range(len(bound)):
            base = model()
            base.set_values({param:bound[i]})
            try:
                empty_list[i] = np.log(SolveSFC(base,time=time+skip)[var][skip:].std())
            except Exception as e:
                empty_list[i] = np.infty
                pass
        df[param] = empty_list ################### Replace here
############################### End #####################################################
    df.index = bound
    
    sns.set_context('talk')
    fig, ax = plt.subplots()

    df.plot(
        ax = ax,
        lw = 2.5
    )
    ax.ticklabel_format(useOffset=False)
    ax.set_ylabel(f"$\log(std({var}))$")
    ax.set_xlabel("Parameters")
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    fig.suptitle("Sensibility analysis", fontsize = 14, weight="bold")
    ax.set_title("Simulation duration is {} periods (desconsidering firsts {}lags)".format(time+skip,skip), fontsize = 12, y = .98)

    ylim = ax.get_ylim()
    fig.savefig("../figs/" + filename, dpi = 300)
    plt.show()
    print("Total running time: ", datetime.now()-t2)
    return df

