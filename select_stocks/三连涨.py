from datetime import datetime
from tools.logger import log
from core.stocks import get_kline
from core.stocks import filter_stocks
from tqdm import tqdm
from tools.send_email import send_email

##三天上涨
def is_up3_mild_trend(df):
    """
    判断是否满足：
    1. 最近3天连续上涨（收盘价逐日上涨）
    2. 三天累计涨幅不超过6%
    3. MA5 > MA10 > MA20（多头排列）
    """
    if df is None or len(df) < 25:
        return False

    df['ma5'] = df['收盘价'].rolling(5).mean()
    df['ma10'] = df['收盘价'].rolling(10).mean()
    df['ma20'] = df['收盘价'].rolling(20).mean()

    # 连续3天上涨
    last3 = df.iloc[-3:]
    if not (last3['收盘价'].iloc[0] < last3['收盘价'].iloc[1] < last3['收盘价'].iloc[2]):
        return False

    # 条件2：三天都是红K线（阳线）
    if not all(last3['收盘价'] > last3['开盘价']):
        return False

    # 三天累计涨幅
    close_now = df['收盘价'].iloc[-1]
    close_3day_ago = df['收盘价'].iloc[-4]
    change = (close_now / close_3day_ago) - 1
    if change > 0.078 or change < 0.028:
        return False

    # 多头排列
    last_row = df.iloc[-1]
    if not (last_row['ma5'] > last_row['ma10'] > last_row['ma20']):
        return False

    return True

def select_stocks():

    """主函数：筛选符合条件的股票"""
    stock_list = filter_stocks(close_min=15,SZ_min=99)
    # stock_list=['601311']
    result = []
    for code in tqdm(stock_list, desc="选股进度", bar_format="{l_bar}{bar:30}{r_bar}", colour="green"):
        df = get_kline(code,x='tu')
        if df is not None and is_up3_mild_trend(df):
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
    send_email(f'{now}三连涨---： \n\n\n\n'+str(code))
