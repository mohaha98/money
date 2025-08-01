"""=================不积跬步无以至千里==================
作    者： LEGION
创建时间： 2025/8/1 22:13
文件名： 洗盘.py
功能作用： 
=================不积小流无以成江海=================="""

import pandas as pd
from datetime import datetime
from tools.logger import log
from core.stocks import get_kline
from core.stocks import filter_stocks
from tqdm import tqdm
from tools.send_email import send_email

def is_possible_washout_with_turnover(df: pd.DataFrame) -> bool:
    """
    判断是否存在洗盘嫌疑，加入换手率指标判断。

    入参:
        df: pd.DataFrame，包含以下列：
            ['日期', '开盘价', '收盘价', '最高价', '最低价', '成交量', '涨跌额', '涨跌幅', '换手率']

    返回:
        True 表示有洗盘嫌疑，False 表示没有
    """

    if df.shape[0] < 30:
        return False  # 数据不足

    df = df.copy()
    df['ma5'] = df['收盘价'].rolling(5).mean()
    df['ma10'] = df['收盘价'].rolling(10).mean()
    df['ma20'] = df['收盘价'].rolling(20).mean()
    df['avg_vol_5'] = df['成交量'].rolling(5).mean()
    df['avg_vol_10'] = df['成交量'].rolling(10).mean()
    df['avg_turnover_5'] = df['换手率'].rolling(5).mean()
    df['avg_turnover_10'] = df['换手率'].rolling(10).mean()

    today = df.iloc[-1]

    # 条件1：趋势未坏（轻微回调或多头排列）
    trend_ok = (
            (today['收盘价'] > today['ma20'] * 0.97) or
            (today['ma5'] > today['ma10'] > today['ma20'])
    )
    if not trend_ok:
        return False

    # 条件2：缩量+十字星 or 下影线 or 换手不高
    entity = abs(today['收盘价'] - today['开盘价'])
    total_range = today['最高价'] - today['最低价']
    lower_shadow = min(today['开盘价'], today['收盘价']) - today['最低价']
    upper_shadow = today['最高价'] - max(today['开盘价'], today['收盘价'])

    is_doji_like = (entity / today['收盘价'] < 0.006) and (total_range / today['收盘价'] < 0.05)
    is_long_lower_shadow = lower_shadow > upper_shadow * 1.5 and lower_shadow > 0.01 * today['收盘价']
    is_volume_low = today['成交量'] < today['avg_vol_5']
    is_turnover_normal = today['换手率'] < today['avg_turnover_5'] * 1.2  # 无异常高换手

    if not ((is_doji_like or is_long_lower_shadow) and is_volume_low and is_turnover_normal):
        return False

    # 条件3：前15日是否出现放量且换手率高（主力进出行为）
    last_15 = df.iloc[-16:-1]
    has_spike = (
            (last_15['成交量'] > last_15['avg_vol_10'] * 1.8) &
            (last_15['换手率'] > last_15['avg_turnover_5'] * 1.3)
    ).any()

    if not has_spike:
        return False


    # 条件4（新增）：后市可能大涨的信号：
    # 1）缩量回调不破MA20
    # 2）换手率持续收缩（筹码集中）
    recent_5 = df.iloc[-5:]
    stable_above_ma20 = (recent_5['收盘价'] > recent_5['ma20']).all()
    shrinking_turnover = (recent_5['换手率'].iloc[-1] < recent_5['换手率'].mean()) and (recent_5['换手率'].iloc[-1] < recent_5['avg_turnover_10'].iloc[-1])
    if not (stable_above_ma20 and shrinking_turnover):
        return False

    return True

def select_stocks():

    """主函数：筛选符合条件的股票"""
    stock_list = filter_stocks(close_min=15,SZ_min=110,HSL_min=0.5,close_max=50)
    # stock_list=['601311']
    result = []
    for code in tqdm(stock_list, desc="选股进度", bar_format="{l_bar}{bar:30}{r_bar}", colour="green"):
        df = get_kline(code)
        if df is not None and is_possible_washout_with_turnover(df):
            result.append(code)
    return result


if __name__ == '__main__':
    # 执行选股
    # selected = select_stocks()
    # print("符合突破放量模型的股票：", selected)
    code=select_stocks()
    now = datetime.today().strftime('%Y%m%d%H%M')
    log.info(f'长度是{len(code)}')
    log.info(f'{code}')
    send_email(f'{now}存在洗盘嫌疑： \n\n\n\n'+str(code))
