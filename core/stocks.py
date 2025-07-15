import akshare as ak
from tqdm import tqdm
from datetime import datetime, timedelta
from tools.pandas_tools import parse_kline_to_dataframe
from tools.send_request import send_request


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
def filter_stocks(SZ_min = 60, SZ_max=200, HSL_min=1, HSL_max=15, LB_min=0, LB_max=100, close_min=5,close_max=88):

    # 获取股票实时行情数据（包含市值、换手率、量比等）
    df = ak.stock_zh_a_spot_em()

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



def get_kline(code):
    """
    股票详情 价格 开盘价 收盘价 量比等信息
    [名字，今天收盘价，今天开盘价，昨天开盘价，昨天收盘价，量比]
    """
    kline_temp = ['日期', '开盘价', '收盘价', '最高价', '最低价', '成交量', '成交额', '振幅', '涨跌', '涨幅', '换手率']
    today = datetime.today().strftime('%Y%m%d')
    date_400_days_ago = (datetime.today() - timedelta(days=100)).strftime('%Y%m%d')
    try:
        url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        payload = {'fields1':"f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13",
                   "fields2":"f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
                   "beg": date_400_days_ago,
                   "end": today,
                   "secid": f"{1 if code.startswith('6') else 0}.{code}",
                   "klt": "101",
                   "fqt": 1}
        response = send_request("GET", url, data=payload)
        k_data=response.get('data').get('klines')
        kline=parse_kline_to_dataframe(k_data)
        # print(kline)
        return kline
    except:
        return None

if __name__ == '__main__':
    print(get_kline('002466'))