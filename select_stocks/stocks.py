import akshare as ak
import pandas as pd
from tqdm import tqdm
from datetime import datetime, timedelta

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


def get_filtered_stock_codes() -> list:
    """
    获取符合以下固定条件的A股股票代码列表：
        - 排除 ST 和退市股票
        - 收盘价 < 88元
        - 总市值 > 60亿（单位：元）
        - 换手率 3%~15%
        - 量比 > 1.5
        - 涨幅 > 0%

    返回:
        List[str]: 符合条件的股票代码列表
    """

    # 获取A股所有股票当日行情数据，包含价格、换手率、量比、市值等
    df = ak.stock_zh_a_spot_em()

    print(f"获取原始股票数量: {len(df)}")

    # 过滤ST、退市股票（名称中包含 ST、*ST、退）
    df = df[~df['名称'].str.contains('ST|退')]

    # 先把列转成字符串，方便替换符号，再转回数字
    df['最新价'] = pd.to_numeric(df['最新价'], errors='coerce')

    df['换手率'] = df['换手率'].astype(str).str.replace('%', '', regex=False)
    df['换手率'] = pd.to_numeric(df['换手率'], errors='coerce')

    df['量比'] = pd.to_numeric(df['量比'], errors='coerce')

    df['涨跌幅'] = df['涨跌幅'].astype(str).str.replace('%', '', regex=False)
    df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')

    df['总市值'] = df['总市值'].astype(str).str.replace('亿', '', regex=False)
    df['总市值'] = pd.to_numeric(df['总市值'], errors='coerce') * 1e8  # 亿转元

    # 筛选条件
    condition = (
        (df['最新价'] < 88) &
        (df['总市值'] > 60e8) &
        (df['换手率'] > 3.0) & (df['换手率'] < 15.0) &
        (df['量比'] > 1.5) &
        (df['涨跌幅'] > 0)
    )

    filtered_df = df[condition]

    print(f"筛选后剩余股票数量: {len(filtered_df)}")

    # 返回代码列表
    return filtered_df['代码'].tolist()



def get_stock_data(code):
    end_date = datetime.today().strftime('%Y%m%d')
    one_year_ago = datetime.today() - timedelta(days=500)
    start_date = one_year_ago.strftime('%Y%m%d')
    print(start_date)
    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="hfq",start_date=start_date,
            end_date=end_date)
        df = df[['日期', '开盘', '收盘', '最高', '最低', '成交量', '涨跌幅','换手率']]
        df.columns = ['date', 'open', 'close', 'high', 'low', 'volume','zdf','hsl']
        df['volume'] = df['volume'].astype(float)
        df = df.sort_values('date').reset_index(drop=True)
        return df
    except:
        return None

print(get_stock_data('002466'))