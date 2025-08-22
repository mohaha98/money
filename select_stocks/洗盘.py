"""=================不积跬步无以至千里==================
作    者： LEGION
创建时间： 2025/8/1 22:13
文件名： 洗盘.py
功能作用： 
=================不积小流无以成江海=================="""

import pandas as pd
from datetime import datetime
from tools.logger import log
from core.stocks import get_kline,is_up_yj
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


    # df = df.iloc[:-1].copy()
    # df = df.copy()
    df['ma5'] = df['收盘价'].rolling(5).mean()
    df['ma10'] = df['收盘价'].rolling(10).mean()
    df['ma20'] = df['收盘价'].rolling(20).mean()
    df['avg_vol_5'] = df['成交量'].rolling(5).mean()
    df['avg_vol_10'] = df['成交量'].rolling(10).mean()
    df['avg_turnover_5'] = df['换手率'].rolling(5).mean()
    df['avg_turnover_10'] = df['换手率'].rolling(10).mean()

    today = df.iloc[-1]

    # 1、前期横盘震荡（高低差 < 8%）
    before15 = df[-16:-1]
    high_max = before15['最高价'].max()
    low_min = before15['最低价'].min()
    max_fluct = (high_max - low_min) / low_min
    if max_fluct > 0.09:
        return False

    # 2、趋势未坏（轻微回调或多头排列）
    trend_ok = (
            (today['收盘价'] > today['ma20'] * 0.95) and
            (today['ma10'] > today['ma20'])
    )
    if not trend_ok:
        return False

    # 3、实体小，振幅小于5个点  缩量  无异常高换手
    entity = abs(today['收盘价'] - today['开盘价'])
    total_range = today['最高价'] - today['最低价']

    is_doji_like = (entity / today['收盘价'] < 0.018) and (total_range / today['收盘价'] < 0.05) #实体小，振幅小于5个点
    is_volume_low = (today['成交量'] < today['avg_vol_5']) and (today['成交量'] < before15['成交量'].iloc[-2])  ##缩量
    is_turnover_normal = (today['换手率'] < today['avg_turnover_5'] * 1.1) and (today['换手率'] < before15['换手率'].iloc[-2])  # 无异常高换手

    if not (is_doji_like and is_volume_low and is_turnover_normal):
        return False

    return True

def select_stocks():

    """主函数：筛选符合条件的股票"""
    stock_list = filter_stocks(close_min=12, SZ_min=130, close_max=89)
    # stock_list=['601311']
    result = []
    for code in tqdm(stock_list, desc="选股进度", bar_format="{l_bar}{bar:30}{r_bar}", colour="green"):
        df = get_kline(code)
        if df is not None and is_possible_washout_with_turnover(df):
            if is_up_yj(code):
                result.append(code)
    return result


if __name__ == '__main__':
    # 执行选股
    code=select_stocks()
    now = datetime.today().strftime('%Y%m%d%H%M')
    log.info(f'长度是{len(code)}')
    log.info(f'{code}')
    send_email(f'{now}存在洗盘嫌疑： \n\n\n\n'+str(code))

