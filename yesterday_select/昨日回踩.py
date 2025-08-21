from datetime import datetime
from tools.logger import log
from core.stocks import get_kline
from core.stocks import filter_stocks,is_up_yj
from tqdm import tqdm
from tools.send_email import send_email
from select_stocks.强势回踩 import is_strong_pullback

def is_strong_pullback_01(df):
    """判断是否符合突破放量选股模型"""
    if len(df) < 30:
        return False
    # 获取最后一行的数据
    today_row = df.iloc[-1]
    # 去掉当天日期的k线数据
    df = df.iloc[:-1].copy()
    if not is_strong_pullback(df):
        return False

    return True

def select_stocks():
    """主函数：筛选符合条件的股票"""

    stock_list = filter_stocks()
    # stock_list=['600557']
    result = []
    for code in tqdm(stock_list, desc="选股进度", bar_format="{l_bar}{bar:30}{r_bar}", colour="green"):
        df = get_kline(code,'ak')
        if df is not None and is_strong_pullback_01(df):
            ##业绩涨的
            if is_up_yj(code):
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

