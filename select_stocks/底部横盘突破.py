import akshare as ak
import pandas as pd
from tqdm import tqdm

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
            if price >= 5 and mkt_cap >= 60:
                stock_list.append(code)
        except:
            continue

    return stock_list

# ------------------------------
# 获取K线数据
# ------------------------------
def get_stock_data(code):
    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="hfq")
        df = df[['日期', '开盘', '收盘', '最高', '最低', '成交量']]
        df.columns = ['date', 'open', 'close', 'high', 'low', 'volume']
        df['volume'] = df['volume'].astype(float)
        df = df.sort_values('date').reset_index(drop=True)
        return df
    except:
        return None

# ------------------------------
# 判断是否符合底部横盘突破模式
# ------------------------------
def is_platform_breakout(df, days=20):
    """
    策略逻辑：
    - 过去N日横盘（波动小）
    - 今日突破平台上沿
    - 今日放量明显
    """
    if len(df) < days + 1:
        return False

    recent = df[-(days + 1):]
    today = recent.iloc[-1]
    before = recent.iloc[:-1]

    high_max = before['high'].max()
    low_min = before['low'].min()
    max_fluct = (high_max - low_min) / low_min

    # 横盘震荡（高低差 < 8%）
    if max_fluct > 0.08:
        return False

    # 今日收盘 > 平台最高（突破）
    if today['close'] <= high_max:
        return False

    # 放量突破：今日成交量 > 前5日均量 * 1.5
    avg_vol_5 = before['volume'][-5:].mean()
    if today['volume'] <= 1.5 * avg_vol_5:
        return False

    return True

# ------------------------------
# 主函数：遍历所有符合过滤器的股票
# ------------------------------
def select_stocks():
    stock_list = get_filtered_stock_list()
    selected = []

    for code in tqdm(stock_list, desc="选股进度"):
        df = get_stock_data(code)
        if df is not None and is_platform_breakout(df):
            selected.append(code)

    return selected

# ------------------------------
# 执行选股
# ------------------------------
if __name__ == "__main__":
    result = select_stocks()
    print("✅ 符合底部横盘突破模型的股票：")
    print(result)
