"""=================不积跬步无以至千里==================
作    者： LEGION
创建时间： 2025/8/23 12:22
文件名： etf.py
功能作用：
=================不积小流无以成江海=================="""
import tushare as ts
pro = ts.pro_api()
from datetime import datetime, timedelta
from tools.send_email import send_email
def get_all_etf():
    df = pro.etf_basic(list_status='L', fields='ts_code,csname,index_code,extname')
    df= df[
           (df["extname"].str.contains("军工", na=False))&
           (~df["extname"].str.contains("0|中|央|债|港|恒|基|创业|科创|国|沙|指|龙", na=False))&
           (~df["extname"].str.match(r'^[A-Za-z0-9]+$', na=False))
           ]
    # 去重：一个指数只保留一只ETF（默认保留第一只）
    df = df.drop_duplicates(subset='index_code', keep='first')
    print(df['extname'].tolist())
    df["ts_code"] = df["ts_code"].str[:-3]

    result=df['ts_code'].tolist()
    print(f"长度：{len(result)}")
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
    result=get_all_etf()
    # send_email(f'etf筛选： \n\n\n\n'+str(result))
    # print(etf_kline('563550.SH'))
