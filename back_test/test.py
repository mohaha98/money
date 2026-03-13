"""=================不积跬步无以至千里==================
作    者： LEGION
创建时间： 2026/3/10 19:39
文件名： test.py
功能作用： 
=================不积小流无以成江海=================="""

import pandas as pd
import numpy as np
from core.stocks import get_kline

import pandas as pd
import numpy as np


def calculate_rsi_6_standard(kline_data, target_date, period=6):
    """
    计算指定日期的6日RSI值（韦尔德式/EMA版，和行情软件一致）

    参数：
        kline_data (pd.DataFrame): 股票K线数据，含'date'（日期字符串）、'close'（收盘价）
        target_date (str): 目标日期，格式'YYYY-MM-DD'
        period (int): RSI周期，默认6

    返回：
        float: 目标日期的6日RSI（保留2位小数）；数据不足/日期不存在返回None
    """
    # 1. 数据预处理
    df = kline_data.copy()
    df['日期'] = df['日期'].astype(str)
    df = df.sort_values('日期').reset_index(drop=True)

    # 检查目标日期是否存在
    if target_date not in df['日期'].values:
        print(f"错误：日期{target_date}不在数据中")
        return None

    # 2. 计算每日涨跌、涨幅、跌幅
    df['change'] = df['收盘价'].diff()
    df['gain'] = np.where(df['change'] > 0, df['change'], 0)
    df['loss'] = np.where(df['change'] < 0, -df['change'], 0)

    # 3. 计算EMA版的平均涨幅/跌幅（韦尔德式）
    # 第一步：计算初始平均值（前period天的简单平均）
    df['avg_gain'] = np.nan
    df['avg_loss'] = np.nan
    # 找到第一个能计算初始平均值的位置
    first_valid_idx = period - 1  # period=6时，第一个位置是5（索引从0开始）
    if len(df) <= first_valid_idx:
        print(f"错误：数据不足，至少需要{period}天K线")
        return None

    # 初始值
    df.loc[first_valid_idx, 'avg_gain'] = df.loc[:first_valid_idx, 'gain'].mean()
    df.loc[first_valid_idx, 'avg_loss'] = df.loc[:first_valid_idx, 'loss'].mean()

    # 第二步：迭代计算后续的EMA平均值
    for i in range(first_valid_idx + 1, len(df)):
        df.loc[i, 'avg_gain'] = (df.loc[i - 1, 'avg_gain'] * (period - 1) + df.loc[i, 'gain']) / period
        df.loc[i, 'avg_loss'] = (df.loc[i - 1, 'avg_loss'] * (period - 1) + df.loc[i, 'loss']) / period

    # 4. 计算RS和RSI
    df['rs'] = df['avg_gain'] / df['avg_loss']
    # 处理avg_loss=0的情况（无下跌，RSI=100）
    df['rsi_6'] = np.where(df['avg_loss'] == 0, 100, 100 - (100 / (1 + df['rs'])))

    # 5. 提取目标日期的RSI
    target_idx = df[df['日期'] == target_date].index[0]
    if np.isnan(df.loc[target_idx, 'rsi_6']):
        print(f"错误：日期{target_date}的RSI数据不足")
        return None

    return round(df.loc[target_idx, 'rsi_6'], 2)


# ------------------- 测试用例 -------------------
if __name__ == "__main__":
    # 模拟K线数据（日期+收盘价）
    test_kline = get_kline('300661','ef')

    # 计算2026-03-10的6日RSI
    target_date = '2026-03-04'
    rsi_result = calculate_rsi_6_standard(test_kline, target_date)
    print(f"{target_date}的6日RSI值：{rsi_result}")

