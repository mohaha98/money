from datetime import datetime
from tools.logger import log
from core.stocks import get_kline
from core.stocks import filter_stocks
from tqdm import tqdm
from tools.send_email import send_email
from select_stocks.回踩缩量十字星 import is_trend_pullback_star

##回踩缩量十字星
def is_trend_pullback_star_01(df):
    """
    判断是否满足趋势回踩 + 缩量十字星模型：
    1. 多头排列 MA5 > MA10 > MA20 且收盘价 > MA20
    2. 今日缩量
    3. K线形态接近十字星（实体小、波动不大）
    """
    if len(df) < 30:
        return False
    #获取最后一行的数据
    today_row = df.iloc[-1]
    #去掉当天日期的k线数据
    df = df.iloc[:-1].copy()

    if not is_trend_pullback_star(df):
        return False

    if today_row['涨跌幅']<1:
        return False
    return True


def select_stocks():

    """主函数：筛选符合条件的股票"""
    stock_list = filter_stocks(close_min=12)
    # stock_list=['601311']
    result = []
    for code in tqdm(stock_list, desc="选股进度", bar_format="{l_bar}{bar:30}{r_bar}", colour="green"):
        df = get_kline(code)
        if df is not None and is_trend_pullback_star_01(df):
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
    send_email(f'{now}昨日回踩十字星： \n\n\n\n'+str(code))
