#!/usr/bin/env python
# coding: utf-8

# # TODO
# 
# - [ ] Checar importância da significância estatística dos coeficientes da regressão
# - [ ] Checar quebra estrutural em 1991

# # Setup

# In[1]:


get_ipython().system('rm *.csv # Removendo dados anteriores')
get_ipython().system('rm -R figs # Removendo pasta de figuras')
get_ipython().system('rm -R tabs # Removendo pasta de tabelas')
get_ipython().system('mkdir figs # Criando pasta para salvar figuras')
get_ipython().system('mkdir tabs # Criando pasta para salvar tabelas')
get_ipython().system('ls')


# # Introdução
# 
# Esta rotina ajusta um modelo de séries temporais. 
# Será testado se o investimento residencial ($I_h$) depende da <u>taxa própria de juros</u> dos imóveis, ou seja,
# 
# $$
# I_h = f(r_{mo}, p_h)
# $$
# em que
# 
# - $I_h$ Investimento residencial
# 
#   + **Série:** PRFI
#   + Com ajuste sazonal
#   + Trimestral
#   
# - $r_{mo}$ taxa de juros das hipotecas
#   + **Série:** MORTGAGE30US
#   - Sem ajuste sazonal
#   - Semanal (encerrado às quintas feiras)
# 
# - $p_h$ Inflação de imóveis: Índice Case-Shiller
# 
#   + **Série:** CSUSHPISA
#   + Com ajuste sazonal, Jan 2000 = 100
#   + Mensal
#   
# **Nota:** Uma vez que pretende-se utilizar os resultados obtidos deste modelo em um trabalho futuro, os resultados serão checados tanto em python quanto em gretl, ambos softwares livres.

# # Carregando pacotes

# In[2]:


get_ipython().run_line_magic('config', "InlineBackend.figure_format = 'retina'")
get_ipython().run_line_magic('load_ext', 'rpy2.ipython')

# Pacotes gerais

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import warnings
warnings.filterwarnings('ignore')
# Pacotes estatísticos

from statsmodels.tsa.vector_ar.var_model import VAR
from statsmodels.tsa.api import SVAR
from statsmodels.tsa.vector_ar.vecm import coint_johansen, CointRankResults, VECM, select_coint_rank

from statsmodels.stats.diagnostic import acorr_breusch_godfrey, acorr_ljungbox, het_arch, het_breuschpagan, het_white
from statsmodels.tsa.stattools import adfuller, kpss, grangercausalitytests, q_stat, coint
from arch.unitroot import PhillipsPerron, ZivotAndrews, DFGLS, KPSS, ADF

from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# Pacotes para importação de dados

import pandas_datareader.data as web
from scipy.stats import yeojohnson

# Configurações do notebook

plt.style.use('seaborn-white')
start = datetime.datetime(1987, 1, 1)
#start = datetime.datetime(1992, 1, 1)
end = datetime.datetime(2019, 7, 1)


# # Importando dados

# In[3]:


df = web.DataReader(
    [
        "PRFI",
        "CSUSHPISA",
        "MORTGAGE30US",
    ], 
    'fred', 
    start, 
    end
)

df.columns = [
    "Investimento residencial", 
    "Preço dos imóveis", 
    "Taxa de juros",
]
df.index.name = ""

df['Taxa de juros'] = df['Taxa de juros'].divide(100)
df['Preço dos imóveis'] = df['Preço dos imóveis']/df['Preço dos imóveis'][0]
df["Inflação"] = df["Preço dos imóveis"].pct_change(12)
df = df.resample('Q').mean()

df["Taxa Própria"] = ((1+df["Taxa de juros"])/(1+df["Inflação"])) -1
df['Taxa Própria'], *_ = yeojohnson(df['Taxa Própria'])

df['gZ'], *_ = yeojohnson(df["Investimento residencial"].pct_change(4))

df["Crise"] = [0 for i in range(len(df["gZ"]))]
for i in range(len(df["Crise"])):
    if df.index[i] > datetime.datetime(2007,12,1) and df.index[i] < datetime.datetime(2009,7,1):
        df["Crise"][i] = 1

df.to_csv("Dados_yeojohnson.csv")


df.to_csv(
    "Dados_yeojohnson_ascii.csv", 
    encoding='ascii', 
    header = [
        #'data',
        'invRes',
        'preco',
        'juros',
        'infla',
        'taxap',
        'gz',
        'crise',
          ], 
         )

df = df[["Taxa de juros", "Inflação", "gZ", "Crise", "Taxa Própria"]]
df.plot()
sns.despine()
plt.show()

df["d_Taxa Própria"] = df["Taxa Própria"].diff()
df["d_gZ"] = df["gZ"].diff()
df["d_Inflação"] = df["Inflação"].diff()
df["d_Taxa de juros"] = df['Taxa de juros'].diff()
df = df.dropna()
df.tail()


# # Funções

# ## Teste de raíz unitária

# In[4]:


def testes_raiz(df=df["gZ"], original_trend='c', diff_trend='c'):
    """
    serie: Nome da coluna do df
    orignal_trend: 'c', 'ct', 'ctt'
    diff_trend: 'c', 'ct', 'ctt'
    
    Plota série o original e em diferenta e retorna testes de raíz unitária
    """
    fig, ax = plt.subplots(1,2)

    df.plot(ax=ax[0], title='série original')
    df.diff().plot(ax=ax[1], title='série em diferença')

    plt.tight_layout()
    sns.despine()
    plt.show()
    
    fig, ax = plt.subplots(2,2)
    
    plot_acf(df, ax=ax[0,0], title='ACF: serie original') 
    plot_pacf(df, ax=ax[0,1], title='PACF: serie original')
    
    plot_acf(df.diff().dropna(), ax=ax[1,0], title='ACF: serie em diferença') 
    plot_pacf(df.diff().dropna(), ax=ax[1,1], title='PACF: serie em diferença')
    
    plt.tight_layout()
    sns.despine() 
    plt.show()

    
    # Zivot Andrews
    print('\nZIVOT ANDREWS série em nível')
    print(ZivotAndrews(df, trend = original_trend).summary(),"\n")
    print('\nZIVOT ANDREWS série em primeira difenrença')
    print(ZivotAndrews(df.diff().dropna(), trend = diff_trend).summary(),"\n")
    
    print('\nADF série em nível')
    print(ADF(df, trend=original_trend).summary(),"\n")
    print('\nADF série em primeira diferença')
    print(ADF(df.diff().dropna(), trend=diff_trend).summary(),"\n")
    
    print('\nDFGLS série em nível')
    print(DFGLS(df, trend=original_trend).summary(),"\n")
    print('\nDFGLS série em primeira diferença')
    print(DFGLS(df.diff().dropna(), trend=diff_trend).summary(),"\n")
    
    print('\nKPSS em nível')
    print(KPSS(df, trend = original_trend).summary(),"\n")
    print('\nKPSS em primeira diferença')
    print(KPSS(df.diff().dropna(), trend = diff_trend).summary(),"\n")
    
    print('\nPhillips Perron em nível')
    print(PhillipsPerron(df, trend=original_trend).summary(),"\n")
    print('\nPhillips Perron em primeira diferença')
    print(PhillipsPerron(df.diff().dropna(), trend=diff_trend).summary(),"\n")


# ## Teste de Cointegração Engel-Granger e de Johansen

# In[5]:


# Teste de cointegração

def cointegracao(ts0, ts1, signif = 0.05, lag=1):
  trends = ['nc', 'c', 'ct', 'ctt']
  for trend in trends:
    print(f"\nTestando para lag = {lag} e trend = {trend}")
    result = coint(ts0, ts1, trend = trend, maxlag=lag)
    print('Null Hypothesis: there is NO cointegration')
    print('Alternative Hypothesis: there IS cointegration')
    print('t Statistic: %f' % result[0])
    print('p-value: %f' % result[1])
    if result[1] < signif:
      print('CONCLUSION: REJECT null Hypothesis: there IS cointegration\n')
    else:
      print('CONCLUSION: FAIL to reject Null Hypothesis: there is NO cointegration\n')
    
def testes_coint(series, maxlag=8):
    for i in range(1, maxlag):
        print(50*'=')
        cointegracao(
            ts0=series.iloc[:, 0],
            ts1=series.iloc[:, 1:],
            signif=0.05,
            lag=i
        )
        print("\nTESTE DE JOHANSEN\n")
        rank_sel = select_coint_rank(endog=series, k_ar_diff=i, det_order=1).rank
        print(f'Para lag = {i}, Rank = {rank_sel}')
        print(10*'=')


# ## Análise de resíduos: Ljung-Box e Box-Pierce

# In[6]:


### Resíduos

def LjungBox_Pierce(resid, signif = 0.05, boxpierce = False, k = 4):
  """
  resid = residuals df
  signif = signif. level
  """
  var = len(resid.columns)
  print("H0: autocorrelations up to lag k equal zero")
  print('H1: autocorrelations up to lag k not zero')
  print("Box-Pierce: ", boxpierce)
  
  for i in range(var):
    print("Testing for ", resid.columns[i].upper(), ". Considering a significance level of",  signif*100,"%")
    result = acorr_ljungbox(x = resid.iloc[:,i-1], lags = k, boxpierce = boxpierce)[i-1] < signif
    for j in range(k):
      print("Reject H0 on lag " ,j+1,"? ", result[j])
    print("\n")
    
def ARCH_LM(resid, signif = 0.05, autolag = 'bic'):
  """
  df = residuals df
  signif = signif. level
  """
  var = len(resid.columns)
  print("H0: Residuals are homoscedastic")
  print('H1: Residuals are heteroskedastic')
  
  for i in range(var):
    print("Testing for ", resid.columns[i].upper())
    result = het_arch(resid = resid.iloc[:,i], autolag = autolag)
    print('LM p-value: ', result[1])
    print("Reject H0? ", result[1] < signif)
    print('F p-value: ', result[3])
    print("Reject H0? ", result[3] < signif)
    print('\n')
    

def analise_residuos(results, nmax=15):
    
    residuals = pd.DataFrame(results.resid, columns = results.names)
    
    residuals.plot()
    sns.despine()
    plt.show()
    
    for serie in residuals.columns:
        sns.set_context('paper')
        fig, ax = plt.subplots(1,2, figsize=(10,8))

        plot_acf(residuals[serie], ax=ax[0], title=f'ACF Resíduo de {serie}', zero=False) 
        plot_pacf(residuals[serie], ax=ax[1], title=f'PACF Resíduo de {serie}', zero=False)
        
        plt.tight_layout()
        sns.despine() 
        plt.show()

    print('AUTOCORRELAÇÃO RESIDUAL: PORTMANTEAU\n')
    print(results.test_whiteness(nlags=nmax).summary())
    print('\nAUTOCORRELAÇÃO RESIDUAL: PORTMANTEAU AJUSTADO\n')
    print(results.test_whiteness(nlags=nmax, adjusted=True).summary())
    print('\nLJUNGBOX\n')
    LjungBox_Pierce(residuals, k = 12, boxpierce=False)
    print('\nBOXPIERCE\n')
    LjungBox_Pierce(residuals, k = 12, boxpierce=True)
    print('\nNORMALIDADE\n')
    print(results.test_normality().summary())
    print('\nHOMOCEDASTICIDADE\n')
    ARCH_LM(residuals)
    
    return residuals
    


# In[7]:


results = []
def plot_lags(results = results, trimestres=[2, 5]):
    series = results.names
    fig, ax = plt.subplots(len(trimestres),2, figsize = (16,10))
    
    for i in range(len(trimestres)):
        sns.regplot(y = df[series[0]], x = df[series[1]].shift(-trimestres[i]), color = 'black', ax = ax[i,0], order = 2)
        ax[i,0].set_xlabel(f'{series[1]} defasada em {trimestres[i]} trimestres')

        sns.regplot(x = df[series[0]].shift(-trimestres[i]), y = df[series[1]], color = 'black', ax = ax[i,1], order = 2)
        ax[i,1].set_xlabel(f'{series[0]} defasada em {trimestres[i]} trimestres')


# # Teste de quebra estrutural

# In[8]:


get_ipython().run_cell_magic('R', '-i df', 'library(strucchange)\nlibrary(urca)\ndf <- df[,c(4:7)]\nnames(df) <- c("Juros", "Infla", "TaxaP", "gZ")\ndf <- ts(data = df, start = c(1987,01), frequency = 4)\nbp_ts <- breakpoints(Juros ~ 1, data=df)\nprint("Testando quebra estrutural para Taxa de juros das hipotecas")\nprint(summary(bp_ts))\n\nbp_ts <- breakpoints(gZ ~ 1, data=df)\nprint("=========================")\nprint("Testando quebra estrutural para Taxa de crescimento dos imóveis")\nprint(summary(bp_ts))\n\nbp_ts <- breakpoints(TaxaP ~ 1, data=df)\nprint("=========================")\nprint("Testando quebra estrutural para Taxa Própria")\nprint(summary(bp_ts))\n\nbp_ts <- breakpoints(Infla ~ 1, data=df)\nprint("=========================")\nprint("Testando quebra estrutural para Inflação")\nprint(summary(bp_ts))')


# Selecionando série para depois de 1991

# In[9]:


df = df["1992-01-01":]


# # Teste de raíz unitária

# ## Investimento residencial ($g_Z$)

# In[10]:


testes_raiz(df=df['gZ'])


# **Conclusão:** Série  não é fracamente estacionária.

# ## Taxa própria

# In[11]:


testes_raiz(df['Taxa Própria'])


# **Conclusão:** Será tomada em primeira diferença.

# ## Inflação

# In[12]:


testes_raiz(df['Inflação'])


# ## Taxa de juros das hipotecas

# In[13]:


testes_raiz(df['Taxa de juros'], original_trend='ct')


# # Cointegração

# ## $g_Z$ e Taxa Própria

# In[14]:


testes_coint(series=df[['gZ', 'Taxa Própria']], maxlag=9)


# ## $g_Z$, Inflação e taxa de juros

# In[15]:


testes_coint(series=df[['gZ', 'Inflação', 'Taxa de juros']])


# ## $g_Z$ e Inflação

# In[16]:


testes_coint(series=df[['gZ', 'Inflação']])


# # VECM

# VECM: $g_Z$, Inflação e Juros exógeno

# ## Ordem do modelo

# In[17]:


from statsmodels.tsa.vector_ar.vecm import select_order

det = 'cili'
order_vec = select_order(
    df[[
        #"Inflação", 
        "Taxa Própria", 
        "gZ"
    ]], 
    #exog=df[["Taxa de juros"]],
    maxlags=15, deterministic=det)

with open('./tabs/VECM_lag_order.tex','w') as fh:
    fh.write(order_vec.summary().as_latex_tabular(tile = "Selação ordem do VECM"))

order_vec.summary()


# ## Estimação

# In[18]:


model = VECM(
    endog = df[[
        #"Inflação", 
        "Taxa Própria", 
        "gZ"
    ]], 
    #exog=df[["Taxa de juros"]],
    k_ar_diff=8,
    deterministic=det, 
)
results = model.fit()

with open('./tabs/VECM_ajuste.tex','w') as fh:
    fh.write(results.summary().as_latex())

print(results.summary())


# ## Análise dos resíduos

# In[19]:


print(60*"=")
print("\nPÓS ESTIMAÇÂO\n")
residuals = analise_residuos(results=results)
print(60*"=")


# ## Função impulso resposta ortogonalizada

# In[20]:


p = results.irf(20).plot(orth=True)
p.suptitle("")
sns.despine()
plt.show()
p.savefig("./figs/Impulso_VECMOrth.png", dpi = 300, bbox_inches = 'tight',
    pad_inches = 0.2, transparent = True,)


# ## Função impulso resposta não-ortogonalizada

# In[21]:


p = results.irf(20).plot(orth=False)
p.suptitle("")
sns.despine()
plt.show()
p.savefig("./figs/Impulso_VECM.png", dpi = 300, bbox_inches = 'tight',
    pad_inches = 0.2, transparent = True,)


# ## Teste de causalidade de granger

# In[22]:


series = residuals.columns
print(results.test_granger_causality(causing=series[0], caused=series[1]).summary())
print(results.test_inst_causality(causing=series[0]).summary())


# ## Inspeção gráfica dos resíduos

# In[23]:


series = results.names
for serie in series:
    sns.scatterplot(x = residuals[serie], y = residuals[serie]**2)
    plt.ylabel(f"{serie}^2")
    sns.despine()
    plt.show()
    
    sns.scatterplot(
    y = residuals[serie], 
    x = residuals[serie].shift(-1), 
    color = 'darkred' 
    )
    sns.despine()
    plt.xlabel(f"{serie}(-1)")
    plt.show()


# In[24]:


sns.set_context('paper')
g = sns.PairGrid(residuals, diag_sharey=False)
g.map_lower(sns.kdeplot, color = 'darkred')
g.map_upper(sns.scatterplot, color = 'darkred')
g.map_diag(sns.kdeplot, lw=3, color = 'darkred')
plt.show()
g.savefig("./figs/Residuos_4VECM.png", dpi = 300, bbox_inches = 'tight',
    pad_inches = 0.2, transparent = True,)


# In[25]:


series = results.names
sns.set_context('talk')
ax = sns.jointplot(
    x = series[0], 
    y = series[1], 
    data = residuals, color = 'darkred', kind="reg", 
)
plt.show()


# ## FEVD

# In[26]:


get_ipython().run_cell_magic('R', '-o fevd_gz', 'library(tsDyn)\nlibrary(readr)\ndf <- read.csv("./Dados_yeojohnson.csv", encoding="UTF-8")\ndf <- df[,c(4:7)]\nnames(df) <- c("Juros", "Infla", "TaxaP", "gZ")\ndf <- na.omit(df[,c("Juros", "Infla","TaxaP", "gZ")])\ndf <- ts(data = df, start = c(1992,03), frequency = 4)\nmodel <- tsDyn::VECM(data = df[,c("TaxaP","gZ")], lag = 6, r = 1, estim = "ML", LRinclude="both", include="trend")\nfevd_gz = data.frame(tsDyn::fevd(model, 20)$gZ)')


# In[27]:


get_ipython().run_cell_magic('R', '-o fevd_tx', 'fevd_tx = data.frame(tsDyn::fevd(model, 20)$TaxaP)')


# In[28]:


sns.set_context('talk')
fig, ax = plt.subplots(2,1, figsize = (16,10))

fevd_gz.plot(
    ax=ax[0], 
    title = "Decomposição da variância para $g_Z$", 
    color = ("black", "lightgray"), 
    kind = 'bar', stacked = True
)
ax[0].set_xlabel('Trimestres')
ax[0].set_ylabel('Porcentagem')
ax[0].axhline(y=0.5, color = 'red', ls = '--')
ax[0].legend(loc='center left', bbox_to_anchor=(1, 0.5), labels = ("50%", "Inflação", "gZ"))
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=0)


fevd_tx.plot(
    ax=ax[1], 
    title = "Decomposição da variância para Inflação", 
    color = ("black", "lightgray"), 
    kind = 'bar', stacked = True,
)
ax[1].axhline(y=0.5, color = 'red', ls = '--')
ax[1].legend(loc='center left', bbox_to_anchor=(1, 0.5), labels = ("50%", "Inflação", "gZ"))
ax[1].set_xlabel('Trimestres')
ax[1].set_ylabel('Porcentagem')
ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=0)

sns.despine()
plt.tight_layout()
plt.show()
fig.savefig("./figs/FEVD_VECM.png", dpi = 300, bbox_inches = 'tight',
    pad_inches = 0.2, transparent = True,)


# # VAR
# 
# **Dúvida:** Variável exógena do VAR deve ser estacionária também?

# ## Ordem do modelo

# In[29]:


model = VAR(
    df[["d_Taxa Própria", 'd_gZ']],
)
print(model.select_order(maxlags=15, trend='ct').summary())


# Adotando o BIC como critério de seleção dada a parciomônia, estima-se uma VAR de ordem 5.

# ## Estimação

# In[30]:


results = model.fit(maxlags=5)
print(results.summary())


# ## Pós-estimação

# ### Autocorrelação dos resíduos 
# 
# **OBS:** série consigo mesma na diagonal principal.

# In[31]:


results.plot_acorr(nlags = 20)
sns.despine()
plt.show()


# **Conclusão:** Pela inspeção gráfica, o modelo não apresenta autocorrelação serial dos resíduos.

# ### Estabilidade

# In[32]:


print("Estável:", results.is_stable(verbose=True))


# **OBS:** Apesar de estar escrito VAR(1), os resultados acima correspondem ao VAR(p)

# ## Inspeção dos resíduos

# In[33]:


residuals = analise_residuos(results=results)


# ## Inspeção gráfica dos resíduos

# In[34]:


series = results.names
sns.set_context('talk')
ax = sns.jointplot(
    x = series[0], 
    y = series[1], 
    data = residuals, color = 'darkred', kind="reg", 
)
plt.show()


# In[35]:


sns.set_context('paper')
g = sns.PairGrid(residuals, diag_sharey=False)
g.map_lower(sns.kdeplot, color = 'darkred')
g.map_upper(sns.scatterplot, color = 'darkred')
g.map_diag(sns.kdeplot, lw=3, color = 'darkred')
plt.show()
g.savefig("./figs/Residuos_4.png", dpi=300)


# In[36]:


series = results.names
for serie in series:
    sns.scatterplot(x = residuals[serie], y = residuals[serie]**2)
    sns.despine()
    plt.show()
    
    sns.scatterplot(
    y = residuals[serie], 
    x = residuals[serie].shift(-1), 
    color = 'darkred' 
    )
    sns.despine()
    plt.xlabel(f"{serie}(-1)")
    plt.show()


# In[37]:


plot_lags(results=results)


# ## Função resposta ao impulso ortogonalizada

# In[38]:


p = results.irf(20).plot(orth=True)
p.suptitle("")
sns.despine()
plt.show()
p.savefig("./figs/Impulso_Orth.png", dpi = 300)


# ## Função resposta ao impulso não-ortogonalizada

# In[39]:


p = results.irf(20).plot(orth=False)
p.suptitle("")
sns.despine()
plt.show()
p.savefig("./figs/Impulso.png", dpi = 300)


# ## Efeito cumulativo

# In[40]:


p = results.irf(20).plot_cum_effects(orth=True)
sns.despine()
plt.show()
p.savefig("./figs/Impulso_Cum.png", dpi = 300)


# ## Decomposição da variância

# In[41]:


p = results.fevd(20).plot()
sns.despine()
plt.show()
p.savefig("./figs/DecompVar.png", dpi = 300)

