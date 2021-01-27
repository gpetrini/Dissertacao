def fredData(request_dict, start_date, end_date, api_key, freq = 'Q'):
    """ download some data from fred """
    import pandas as pd
    import numpy as np
    import requests
    base = 'https://api.stlouisfed.org/fred/series/observations?series_id='
    dates = '&observation_start={}&observation_end={}'.format(start_date, end_date)
    api_key = '&api_key={}'.format(api_key)
    ftype = '&file_type=json'
    
    dataFrame = pd.DataFrame()
    for code, name in request_dict.items():
        url = '{}{}{}{}{}'.format(base, code, dates, api_key, ftype)
        r = requests.get(url).json()['observations']
        dataFrame[name[0]] = [i['value'] for i in r]

    dataFrame = dataFrame.replace('.', np.nan)    
    dataFrame = dataFrame.astype(float)

    sectors = pd.MultiIndex.from_tuples(list(zip([i[1] for i in request_dict.values()],[i[0] for i in request_dict.values()])))
    dataFrame.columns = sectors

    dates = pd.date_range(start_date, periods=dataFrame.shape[0], freq=freq)
    dataFrame.index = dates
    return dataFrame

"""
# usage 
df = fredData(request_dict=q_dict, start_date=start_date, end_date=end_date, api_key=fred_key)
df
"""
