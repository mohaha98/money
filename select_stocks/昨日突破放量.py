
from datetime import datetime
from tools.logger import log
from core.stocks import get_kline
from core.stocks import filter_stocks
from tqdm import tqdm
from tools.send_email import send_email
from select_stocks.突破放量 import is_breakout_volume

def is_breakout_volume_01(df):
    """判断是否符合突破放量选股模型"""
    if len(df) < 25:
        return False
    # 获取最后一行的数据
    today_row = df.iloc[-1]
    # 去掉当天日期的k线数据
    df = df.iloc[:-1].copy()
    if not is_breakout_volume(df):
        return False
    if abs(today_row['开盘价']-df.iloc[-1]['收盘价'])/df.iloc[-1]['收盘价']>0.01:
        return False
    if today_row['涨跌幅']>1:
        return False


    return True

def select_stocks():
    """主函数：筛选符合条件的股票"""

    stock_list = filter_stocks(LB_min=1.5, HSL_min=2, close_min=12)
    # stock_list=['600557']
    result = []
    for code in tqdm(stock_list, desc="选股进度", bar_format="{l_bar}{bar:30}{r_bar}", colour="green"):
        df = get_kline(code,'ak')
        if df is not None and is_breakout_volume_01(df):
            result.append(code)
    return result

if __name__  ==  '__main__':
    #适用于当天大盘绿色的情况 第二天出现回升
    # 执行选股
    code=select_stocks()
    now = datetime.today().strftime('%Y%m%d%H%M')
    log.info(f'长度是{len(code)}')
    log.info(f'{code}')
    # send_email(f'{now}昨日突破放量---： \n\n\n\n'+str(code))

