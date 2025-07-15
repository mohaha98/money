import akshare as ak
import pandas as pd

# ------------------------------
# 股票池过滤器：排除 ST、低价、小市值股票
# ------------------------------
def get_filtered_stock_list():
    """
    获取A股股票列表，并排除：
    - ST股
    - 当前股价低于5元
    - 流通市值小于60亿
    """
    stock_df = ak.stock_info_a_code_name()
    stock_list = []

    for idx, row in stock_df.iterrows():
        code = row['code']
        name = row['name']

        # ① 排除ST股
        if 'ST' in name.upper():
            continue

        try:
            # ② 获取市值和股价信息
            info = ak.stock_individual_info_em(symbol=code)
            info_df = pd.DataFrame(info)
            info_df.columns = ['item', 'value']
            price = float(info_df[info_df['item'] == '最新价']['value'].values[0])
            mkt_cap = float(info_df[info_df['item'] == '流通市值']['value'].values[0].replace('亿', ''))

            # ③ 过滤条件
            if 88>price >= 5 and mkt_cap >= 60:
                stock_list.append(code)
        except:
            continue

    return stock_list

def get_stock_data(stock_code):
    """获取个股历史K线（后复权）"""
    try:
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="hfq")
        df = df[['日期', '开盘', '收盘', '最高', '最低', '成交量']]
        df.rename(columns={'日期': 'date', '开盘': 'open', '收盘': 'close',
                           '最高': 'high', '最低': 'low', '成交量': 'volume'}, inplace=True)
        df['volume'] = df['volume'].astype(float)
        df = df.sort_values('date').reset_index(drop=True)
        return df
    except:
        return None

def is_breakout_volume(df):
    """判断是否符合突破放量选股模型"""
    if len(df) < 25:
        return False
    last_close = df.iloc[-1]['close']
    last_volume = df.iloc[-1]['volume']
    high_20 = df['high'][-21:-1].max()  # 不包含今天
    avg_volume_5 = df['volume'][-6:-1].mean()  # 不含今天

    if last_close > high_20 and last_volume > avg_volume_5 * 1.5:
        return True
    return False

def select_stocks():
    """主函数：筛选符合条件的股票"""
    stock_list = get_filtered_stock_list()
    result = []
    for code in stock_list:
        df = get_stock_data(code)
        if df is not None and is_breakout_volume(df):
            result.append(code)
    return result

# 执行选股
# selected = select_stocks()
# print("符合突破放量模型的股票：", selected)
print(get_stock_list())
print(len(get_stock_list()))
