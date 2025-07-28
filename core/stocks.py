import re

import akshare as ak
from tqdm import tqdm
from datetime import datetime, timedelta
from tools.pandas_tools import parse_kline_to_dataframe
from tools.send_request import send_request
import pandas as pd
import tushare as ts

def get_all_codes(remove_st=True, return_df=False):
    """
    获取沪深A股所有股票代码（可选择是否排除 ST 和退市股）

    参数：
        remove_st (bool): 是否移除 ST 和退市股
        return_df (bool): 是否返回完整 DataFrame，否则只返回代码列表

    返回：
        List[str] 或 pd.DataFrame
    """
    # 获取股票列表
    stock_df = ak.stock_info_a_code_name()

    # ------------------ 过滤创业板 ------------------
    stock_df = stock_df[~stock_df['code'].str.startswith('688')]
    # ------------------ 过滤 ST 和退市 ------------------
    if remove_st:
        # 过滤 ST、*ST、退市股票
        stock_df = stock_df[
            ~stock_df['name'].str.contains('ST') &
            ~stock_df['name'].str.contains('退')
        ]

    stock_df = stock_df.reset_index(drop=True)

    if return_df:
        return stock_df
    else:
        return stock_df['code'].tolist()


#用于初步筛选
def filter_stocks(SZ_min = 78, SZ_max=1800, HSL_min=1, HSL_max=15, LB_min=0, LB_max=100, close_min=10,close_max=78):

    # 获取股票实时行情数据（包含市值、换手率、量比等）
    df = ak.stock_zh_a_spot_em()
    # ------------------ 过滤创业板 ------------------
    df = df[~df['代码'].str.startswith('688')]
    # 去除ST股票（名称中含有ST或*ST）
    df = df[~df["名称"].str.contains("ST")]

    # 筛选：市值（单位：亿元），换手率（%），量比，股价
    df = df[
        (df["总市值"] > SZ_min*100000000) &
        (df["总市值"] < SZ_max*100000000) &  # 市值大于60亿元
        (df["换手率"] > HSL_min) &
        (df["换手率"] < HSL_max) &
        (df["量比"] > LB_min) &
        (df["量比"] < LB_max) &
        (df["最新价"] > close_min) &
        (df["最新价"] < close_max)
    ]

    # 只返回代码列表，也可以返回整张表
    return df["代码"].tolist()



def get_kline_east(code):
    """
    股票详情 价格 开盘价 收盘价 量比等信息
    [名字，今天收盘价，今天开盘价，昨天开盘价，昨天收盘价，量比]
    """
    today = datetime.today().strftime('%Y%m%d')
    date_100_days_ago = (datetime.today() - timedelta(days=120)).strftime('%Y%m%d')
    try:
        url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        payload = {'fields1':"f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13",
                   "fields2":"f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
                   "beg": date_100_days_ago,
                   "end": today,
                   "secid": f"{1 if code.startswith('6') else 0}.{code}",
                   "klt": "101",
                   "fqt": 1}
        haed={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
              'referer':f'https://quote.eastmoney.com/{"sh" if code.startswith("6") else "sz"}{code}.html'}
        response = send_request("GET", url, data=payload,headers=haed)
        k_data=response.get('data').get('klines')
        kline=parse_kline_to_dataframe(k_data)
        # print(kline)
        return kline
    except:
        return None


#get_kline_tushare
def get_kline_tushare(code):
    """
    获取tushare的k线数据，
    数据有延迟，下午五点后才会有当天的数据
    """
    today = datetime.today().strftime('%Y%m%d')
    date_100_days_ago = (datetime.today() - timedelta(days=120)).strftime('%Y%m%d')
    pro = ts.pro_api()
    df = pro.daily(ts_code=f"{code}.{'SH' if code.startswith('6') else 'SZ'}", start_date=date_100_days_ago, end_date=today)
    df = df[::-1]
    # print(df.iloc[-1])
    df = df.rename(columns={
        'ts_code': '股票代码',
        'trade_date': '日期',
        'high': '最高价',
        'low': '最低价',
        'close': '收盘价',
        'open': '开盘价',
        'vol': '成交量',
        'amount': '成交额',
        'pre_close': '昨收价',
        'change': '涨跌额',
        'pct_chg': '涨跌幅'
    })
    # 选择并返回指定字段
    return df[['日期', '开盘价', '收盘价', '最高价', '最低价', '成交量', '涨跌额', '涨跌幅']]


def get_kline_akshare(code: str) -> pd.DataFrame:
    """
    获取 A 股股票的完整日 K 线数据（含复权、换手率等字段）

    参数:
        code (str): 股票代码（如 '600519'）
        market (str): 市场类型，'sz' 或 'sh'
        start_date (str): 开始日期，格式 'YYYYMMDD'（默认 '20240101'）
        adjust (str): 复权方式，'qfq' 前复权，'hfq' 后复权，'None' 不复权

    返回:
        pandas.DataFrame: 包含完整K线字段
    """
    # 获取数据
    today = datetime.today().strftime('%Y%m%d')
    date_100_days_ago = (datetime.today() - timedelta(days=120)).strftime('%Y%m%d')
    df = ak.stock_zh_a_hist(
        symbol=code,
        period="daily",
        start_date=date_100_days_ago,
        end_date=today,
        adjust='qfq'
    )
    #['日期', '开盘价', '收盘价', '最高价', '最低价', '成交量', '成交额', '振幅', '涨跌额', '涨跌幅', '换手率']
    # 字段重命名为你需要的形式
    df.rename(columns={
        "日期": "日期",
        "开盘": "开盘价",
        "收盘": "收盘价",
        "最高": "最高价",
        "最低": "最低价",
        "成交量": "成交量",
        "成交额": "成交额",
        "振幅": "振幅",
        "涨跌幅": "涨跌幅",
        "涨跌额": "涨跌额",
        "换手率": "换手率",
        "股票代码": "股票代码"
    }, inplace=True)

    # 选择并返回指定字段
    return df[['日期', '开盘价', '收盘价', '最高价', '最低价', '成交量', '涨跌额', '涨跌幅']]



def get_kline(code, x='ak'):
    if x=='ea':
        return get_kline_east(code)
    if x=='tu':
        return get_kline_tushare(code)
    if x=='ak':
        return get_kline_akshare(code)
    else:
        return get_kline_akshare(code)


if __name__ == '__main__':
    pass
    print(get_kline('600580','ak'))
    # ts.set_token('2ab066e2a7f5502cbae653839b89eda20c7e538f1c01a6382e34a8b2')
    # print(get_kline_tushare('002466'))
    # codes=filter_stocks()
    # print(codes)
    # print(len(codes))
    # df = get_kline("002466",'tu')
    # print(df)
    # ts.set_token('2ab066e2a7f5502cbae653839b89eda20c7e538f1c01a6382e34a8b2')