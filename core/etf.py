"""=================不积跬步无以至千里==================
作    者： LEGION
创建时间： 2025/8/23 12:22
文件名： etf.py
功能作用： 
=================不积小流无以成江海=================="""
import tushare as ts
pro = ts.pro_api()
import pandas as pd
from datetime import datetime, timedelta
def get_all_etf():
    df = pro.etf_basic(list_status='L', fields='ts_code,csname,index_code,index_name,extname')
    df= df[
           (df["index_code"].str.contains("SZ|SH|CSI", na=False))
           ]
    # 去重：一个指数只保留一只ETF（默认保留第一只）
    # df = df.drop_duplicates(subset='index_code', keep='first')
    # print(df)
    result=df['ts_code'].tolist()
    # print(result)
    return result

def etf_kline(etf_code):
    pass
    today = datetime.today().strftime('%Y%m%d')
    date_100_days_ago = (datetime.today() - timedelta(days=120)).strftime('%Y%m%d')
    df = pro.fund_daily(ts_code=etf_code, start_date=date_100_days_ago, end_date=today,
                        fields='ts_code,trade_date,open,high,low,close,vol,amount,change,pct_chg')
    ##倒序
    df = df[::-1]
    df = df.rename(columns={
        'ts_code': 'etf代码',
        'trade_date': '日期',
        'high': '最高价',
        'low': '最低价',
        'close': '收盘价',
        'open': '开盘价',
        'vol': '成交量',
        'amount': '成交额',
        'change': '涨跌额',
        'pct_chg': '涨跌幅'
    })
    return df[['日期', '开盘价', '收盘价', '最高价', '最低价', '成交量', '涨跌额', '涨跌幅']]

if __name__ == '__main__':
    get_all_etf()
    # print(etf_kline('563550.SH'))
