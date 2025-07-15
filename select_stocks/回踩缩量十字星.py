import akshare as ak
import pandas as pd
from tqdm import tqdm
def get_filtered_stock_list():
    """
    获取A股股票列表，并过滤掉：
    - ST股票
    - 当前价格低于5元的股票
    - 流通市值小于60亿元的股票
    """
    stock_df = ak.stock_info_a_code_name()
    stock_list = []

    for idx, row in stock_df.iterrows():
        code = row['code']
        name = row['name']

        # ① 过滤ST股
        if 'ST' in name.upper():
            continue

        # ② 获取实时价格和市值数据
        try:
            info = ak.stock_individual_info_em(symbol=code)
            info_df = pd.DataFrame(info)
            info_df.columns = ['item', 'value']
            price = float(info_df[info_df['item'] == '最新价']['value'].values[0])
            mkt_cap = float(info_df[info_df['item'] == '流通市值']['value'].values[0].replace('亿', ''))

            # ③ 过滤低价股和小市值股
            if price >= 5 and mkt_cap >= 60:
                stock_list.append(code)
        except:
            continue

    return stock_list


def get_stock_data(stock_code):
    """获取个股历史K线（后复权）"""
    try:
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="hfq")
        df = df[['日期', '开盘', '收盘', '最高', '最低', '成交量']]
        df.columns = ['date', 'open', 'close', 'high', 'low', 'volume']
        df['volume'] = df['volume'].astype(float)
        df = df.sort_values('date').reset_index(drop=True)
        return df
    except:
        return None


def is_trend_pullback_star(df):
    """
    判断是否满足趋势回踩 + 缩量十字星模型：
    1. 多头排列 MA5 > MA10 > MA20 且收盘价 > MA20
    2. 今日缩量
    3. K线形态接近十字星（实体小、波动不大）
    """
    if len(df) < 30:
        return False

    df['ma5'] = df['close'].rolling(5).mean()
    df['ma10'] = df['close'].rolling(10).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    df['avg_volume_5'] = df['volume'].rolling(5).mean()

    row = df.iloc[-1]

    # 条件1：均线多头排列 + 收盘价在MA20上方
    if not (row['ma5'] > row['ma10'] > row['ma20'] and row['close'] > row['ma20']):
        return False

    # 条件2：缩量
    if row['volume'] >= row['avg_volume_5']:
        return False

    # 条件3：十字星（实体极小，总波动不大）
    entity = abs(row['close'] - row['open'])
    total_range = row['high'] - row['low']
    if entity / row['close'] > 0.005:  # 实体小于0.5%
        return False
    if total_range / row['close'] > 0.04:  # 整体波动不大于4%
        return False

    return True


def select_stocks():
    """主函数：获取符合趋势回踩 + 缩量十字星 + 三重过滤的股票"""
    stock_list = get_filtered_stock_list()
    selected = []
    for code in tqdm(stock_list, desc="选股进度", bar_format="{l_bar}{bar:30}{r_bar}", colour="green"):
        df = get_stock_data(code)
        if df is not None and is_trend_pullback_star(df):
            selected.append(code)
    return selected


# 执行选股
result = select_stocks()
print("✅ 符合‘趋势回踩+缩量十字星’并通过过滤的股票：")
print(result)
