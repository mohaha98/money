import time
from datetime import datetime

from core.stocks import get_kline
from core.stocks import filter_stocks,is_up_yj
from tqdm import tqdm
from tools.send_email import send_email
from tools.logger import log

def is_strong_pullback(df):
    """
    强势股调整期模型：
    1）最后一个交易日均线多头：MA5 > MA10 > MA20 且 收盘价 > MA20
    2）前 7 个交易日内有放巨量：存在成交量 > 当日 5 日均量 * 1.8
    3）当前为调整期：收盘价不破 10 日均线，且成交量在 5 日均量 ±20% 区间
    """
    if len(df) < 30:
        return False

    df = df.copy()

    # ===== 均线 & 均量 =====
    df["ma5"] = df["收盘价"].rolling(5).mean()
    df["ma10"] = df["收盘价"].rolling(10).mean()
    df["ma20"] = df["收盘价"].rolling(20).mean()
    df["vol_ma5"] = df["成交量"].rolling(5).mean()

    today = df.iloc[-1]

    # ① 多头：均线多头 + 收盘价在趋势线上方
    if not (today["ma5"] > today["ma10"] > today["ma20"] and today["收盘价"] > today["ma20"]):
        return False

    # ② 前 7 个交易日内有放巨量（不含今天）
    last_7 = df.iloc[-8:-1].copy()
    last_7["is_spike"] = last_7["成交量"] > last_7["vol_ma5"] * 1.8
    if not last_7["is_spike"].any():
        return False

    # ③ 当前为调整期
    #    - 收盘价不破 10 日均线
    #    - 成交量在 5 日均量附近 ±20%
    if today["收盘价"] < today["ma10"]:
        return False

    if not (0.8 * today["vol_ma5"] <= today["成交量"] <= 1.2 * today["vol_ma5"]):
        return False

    return True

def select_stocks():

    """主函数：筛选符合条件的股票"""
    stock_list = filter_stocks(close_min=12,close_max=98)
    # stock_list=['600580']
    result = []
    for code in tqdm(stock_list, desc="选股进度", bar_format="{l_bar}{bar:30}{r_bar}", colour="green"):
        try:
            df = get_kline(code,'ef')
        except:
            time.sleep(1.5)
            df=get_kline(code,'bs')
        if df is not None and is_strong_pullback(df):
            ##业绩涨的

            if is_up_yj(code):
                result.append(code)
    return result

if __name__  ==  '__main__':
    #
    # 执行选股
    code=select_stocks()
    now = datetime.today().strftime('%Y%m%d%H%M')
    log.info(f'长度是{len(code)}')
    log.info(f'{code}')
    send_email(f'{now}强势股调整---： \n\n\n\n'+str(code))