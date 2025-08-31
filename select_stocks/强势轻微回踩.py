import time
from datetime import datetime

from core.stocks import get_kline
from core.stocks import filter_stocks,is_up_yj
from tqdm import tqdm
from tools.send_email import send_email
from tools.logger import log

def is_strong_pullback(df):

    # print(df)
    if len(df) < 30:
        return False
    """
    判断是否符合“强势回踩 + 缩量止跌”选股模型
    
    """
    # df = df.iloc[:-2].copy()
    # 价格、均线、涨幅
    df['ma5'] = df['收盘价'].rolling(5).mean()
    df['ma10'] = df['收盘价'].rolling(10).mean()
    df['ma20'] = df['收盘价'].rolling(20).mean()
    df['avg_volume_5'] = df['成交量'].rolling(5).mean()
    df['avg_volume_10'] = df['成交量'].rolling(10).mean()
    # df['hs_5'] = df['换手率'].rolling(5).mean()
    # df['hs_10'] = df['换手率'].rolling(10).mean()

    today = df.iloc[-1]

    # -------- 条件1：均线多头排列 --------
    if not (today['ma5'] > today['ma10'] > today['ma20'] and today['收盘价'] > today['ma5']*0.9):
        # print('不满足多头')
        return False
    # else:
    #     print('满足多头')
    #     print(today['收盘价'],today['ma20'])


    # -------- 条件2：过去12天中存在放量（放量日 > 当日12日均量 * 1.8） --------
    last_15 = df.iloc[-5:-1].copy()
    if (last_15['最高价'].max() - last_15['最低价'].min()) / last_15['收盘价'].min() < 0.12:  # 涨幅至少10%
        return False
    # last_15['vol_spike'] = last_15['成交量'] > last_15['avg_volume_10'] * 1.7
    # if not last_15['vol_spike'].any():
    #     # print('不满足前期放量')
    #     return False
    # else:
    #     print('满足前期放量')


    # # -------- 条件3：价格在 五日线或者十日线2个点距离内 --------
    # if not (
    #     abs(today['收盘价'] - today['ma5']) / today['ma5'] < 0.03 or
    #     abs(today['收盘价'] - today['ma10']) / today['ma10'] < 0.03
    # ):
    #     # print('不满足价格在均线附近',abs(today['收盘价'] - today['ma10']) / today['ma10'])
    #     return False
    # else:
    #     print('满足价格在均线附近')

    # -------- 条件4：缩量（当天成交量小于5日平均成交量） --------
    if today['成交量'] > df.iloc[-2]['成交量'] or today['成交量'] > today['avg_volume_5']:
        # print(today['成交量'],today['avg_volume_5'])
        # print('不满足缩量')
        return False
    # else:
    #     print('满足缩量')

    if df.iloc[-2]['涨跌幅'] < 2.3:
        # print(today['成交量'],today['avg_volume_5'])
        # print('不满足缩量')
        return False

    # -------- 条件5：当天k线实体小于价格的1.8% --------
    body = abs(today['收盘价'] - today['开盘价'])
    if body / today['收盘价'] > 0.02:
        # print('不满足小实体')
        return False
    # else:
    #     print('满足小实体')

    # # -------- 条件6：当天价格整体波动不大于4% --------
    # if (today['最高价'] - today['最低价']) / today['收盘价'] >= 0.06:
    #     return False
    # # else:
    #     print("满足小波动")


    # -------- 条件7：当天换手率小于五日平均换手率 --------

    # if today['换手率'] >= df.iloc[-2]['换手率']*0.8:
    #     # print('不满足换手率下降',today['hs_5'])
    #     return False
    # else:
    #     print('满足换手率下降',today['hs_5'])

    if abs(today['涨跌幅']) >= 2:
        return False
    # else:
    #     print('满足涨跌幅小于5%')


    return True




def select_stocks():

    """主函数：筛选符合条件的股票"""
    stock_list = filter_stocks(close_min=12,close_max=98)
    # stock_list=['603306']
    result = []
    for code in tqdm(stock_list, desc="选股进度", bar_format="{l_bar}{bar:30}{r_bar}", colour="green"):
        # time.sleep(1.3)
        df = get_kline(code,'tu')
        if df is not None and is_strong_pullback(df):
            ##业绩涨的
            if is_up_yj(code):
                result.append(code)
    return result

if __name__  ==  '__main__':
    #大盘涨幅不大跑来选股
    # 执行选股
    code=select_stocks()
    now = datetime.today().strftime('%Y%m%d%H%M')
    log.info(f'长度是{len(code)}')
    log.info(f'{code}')
    send_email(f'{now}强势轻微回踩---： \n\n\n\n'+str(code))