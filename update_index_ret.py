import numpy as np
import pandas as pd

import akshare as ak
import plotly
import plotly.express as px
from datetime import datetime, timezone, timedelta

def get_df(look_back=63):
    temp = ak.sw_index_spot()
    a = list(temp['指数代码'])
    b = list(temp['指数名称'])
    temp = zip(a, b)
    symbol_name = {}
    for symbol, name in temp:
        symbol_name[symbol] = [name]

    for symbol in symbol_name.keys():
        df = ak.index_level_one_hist_sw(symbol)[['指数代码', '发布日期', '收盘指数', '平均流通市值']]
        df.columns = ['code', 'date', 'close', 'value']
        df = df.iloc[-(look_back+1):]    
        date = df['date'].iloc[-1]
        ret = round(df['close'].pct_change(look_back).iloc[-1], 4)
        value = round(df['value'].mean(), 2)
        symbol_name[symbol] += [date, ret, value]
        
    df = pd.DataFrame({'code':symbol_name.keys()})
    df[['name', 'date', 'return', 'value']] = np.nan
    for i in range(len(df)):
        df.loc[i, ['name', 'date', 'return', 'value']] = symbol_name[df.loc[i]['code']]

    df['return_display'] = df['return'].apply(lambda x: format(x, '.2%')) 
    assert len(df['date'].unique()) == 1
    
    return df

LOOK_BACK = 63
df = get_df(LOOK_BACK)

fig = px.treemap(data_frame=df, 
                 path=[px.Constant('申万一级行业指数近{}个交易日涨幅'.format(LOOK_BACK)), 'name'], 
                 values='value',
                 color='return', 
                 # hover_data=['return', 'return_display'],
                 custom_data=['return_display'],
#                  title='{}, 近{}日涨跌幅'.format(df['date'][0], LOOK_BACK),
                 color_continuous_scale=['#00FF00', '#000000', '#FF0000'],
                 color_continuous_midpoint=0)

fig.data[0].texttemplate = '%{label}<br>%{customdata[0]}'


fig.update_traces(textposition="middle center")



# Get current date, time and timezone to print to the html page
beijing = timezone(timedelta(hours=8))
time_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
time_beijing = time_utc.astimezone(beijing).strftime("%Y-%m-%d %H:%M:%S")

# Rewrite index_ret.html
with open('_includes/index_ret.html', 'a') as f:
    f.truncate(0) # clear file if something is already written on it
    title = "<h1 align=\"center\">Financial Data in China</h1>"
    description = "<h3 align=\"center\">Last update: " + time_beijing + " (UTC+8).</a></h3>"
    f.write(title + description)
    #f.write(fig.to_html())
    f.write(fig.to_html(full_html=False, include_plotlyjs='cdn')) # write the fig created above into the html file
