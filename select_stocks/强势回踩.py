from datetime import datetime

from core.stocks import get_kline
from core.stocks import filter_stocks
from tqdm import tqdm
from tools.send_email import send_email
from tools.logger import log

def is_strong_pullback(df):


    if len(df) < 30:
        return False
    """
    判断是否符合“强势回踩 + 缩量止跌”选股模型
    
    """
    # 价格、均线、涨幅
    close = df['收盘价']
    open = df['开盘价']
    high = df['最高价']
    low = df['最低价']
    vol = df['成交量']
    # -------- 1. 前期上涨 10日涨幅 > 20%--------

    up_5 = close.iloc[-1] / close.iloc[-6] - 1
    up_10 = close.iloc[-1] / close.iloc[-11] - 1

    if up_5 < 0.06 and up_10 < 0.10:
        return False

    # -------- 2. 均线回踩 --------
    ma5 = close.rolling(window=5).mean()
    ma10 = close.rolling(window=10).mean()
    if not (
        abs(close.iloc[-1] - ma5.iloc[-1]) / ma5.iloc[-1] < 0.03 or
        abs(close.iloc[-1] - ma10.iloc[-1]) / ma10.iloc[-1] < 0.03
    ):
        return False

    # -------- 3. 缩量判断 --------
    if vol.iloc[-1] >= vol.iloc[-2] or vol.iloc[-1] >= vol.iloc[-6:-1].mean():
        return False

    # -------- 4. 止跌形态判断 --------
    body = abs(close.iloc[-1] - open.iloc[-1])
    candle_range = high.iloc[-1] - low.iloc[-1]
    lower_shadow = min(open.iloc[-1], close.iloc[-1]) - low.iloc[-1]

    # 十字星/T线/下影线长 or 阳包阴
    is_doji = body < 0.005 * close.iloc[-1]
    is_t_line = lower_shadow > 0.5 * candle_range
    is_engulf = close.iloc[-1] > open.iloc[-1] and close.iloc[-2] < open.iloc[-2] and close.iloc[-1] > open.iloc[-2] and open.iloc[-1] < close.iloc[-2]

    if not (is_doji or is_t_line or is_engulf):
        return False

    return True




def select_stocks():

    """主函数：筛选符合条件的股票"""
    stock_list = filter_stocks(close_min=12)
    # stock_list=['601311']
    result = []
    for code in tqdm(stock_list, desc="选股进度", bar_format="{l_bar}{bar:30}{r_bar}", colour="green"):
        df = get_kline(code)
        if df is not None and is_strong_pullback(df):
            result.append(code)
    return result

if __name__ == '__main__':
    pass
    print("""""""""""""""已经禁用""""")
    # 执行选股
    # selected = select_stocks()
    # print("符合突破放量模型的股票：", selected)
    # code=select_stocks()
    # now = datetime.today().strftime('%Y%m%d%H%M')
    # log.info(f'长度是{len(code)}')
    # log.info(f'{code}')
    # send_email(f'{now}强势回踩---： \n\n\n\n'+str(code))