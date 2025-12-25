
from datetime import datetime
from tools.logger import log
from core.stocks import get_kline
from core.stocks import filter_stocks,is_up_yj
from tqdm import tqdm
from tools.send_email import send_email
import time
def is_breakout_volume(df):
    """判断是否符合突破放量选股模型"""
    if len(df) < 30:
        return False
    last_close = df.iloc[-1]['收盘价']
    last_vol = df.iloc[-1]['成交量']
    high_20 = df['收盘价'][-15:-1].max()  # 不包含今天
    # print(high_20)
    avg_volume_5 = df['成交量'][-6:-1].mean()  # 不含今天
    if last_close > high_20 and last_vol > avg_volume_5 * 1.8:
        return True
    return False


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
    if not (today['ma10'] > today['ma20'] and today['收盘价'] > today['ma20']):
        # print('不满足多头')
        return False
    # else:
    #     print('满足多头')
    #     print(today['收盘价'],today['ma20'])

    # -------- 条件2：过去12天中存在放量（放量日 > 当日12日均量 * 1.8） --------
    last_15 = df.iloc[-10:-1].copy()
    last_15['vol_spike'] = last_15['成交量'] > last_15['avg_volume_10'] * 1.8
    if not last_15['vol_spike'].any():
        # print('不满足前期放量')
        return False
    # else:
    #     print('满足前期放量')

    # -------- 条件3：价格在 五日线或者十日线2个点距离内 --------
    if not (
            abs(today['收盘价'] - today['ma5']) / today['ma5'] < 0.03 or
            abs(today['收盘价'] - today['ma10']) / today['ma10'] < 0.03
    ):
        # print('不满足价格在均线附近',abs(today['收盘价'] - today['ma10']) / today['ma10'])
        return False
    # else:
    #     print('满足价格在均线附近')

    # -------- 条件4：缩量（当天成交量小于5日平均成交量） --------
    if today['成交量'] >= today['avg_volume_5'] * 0.9 or today['成交量'] > df.iloc[-2]['成交量'] * 1.2:
        # print(today['成交量'],today['avg_volume_5'])
        # print('不满足缩量')
        return False
    # else:
    #     print('满足缩量')

    # -------- 条件5：当天k线实体小于价格的1.8% --------
    body = abs(today['收盘价'] - today['开盘价'])
    if body / today['收盘价'] > 0.02:
        # print('不满足小实体')
        return False
    # else:
    #     print('满足小实体')

    # -------- 条件6：当天价格整体波动不大于4% --------
    if (today['最高价'] - today['最低价']) / today['收盘价'] >= 0.04:
        return False
    # else:
    #     print("满足小波动")

    # -------- 条件7：当天换手率小于五日平均换手率 --------

    # if today['换手率'] >= today['hs_5']:
    #     # print('不满足换手率下降',today['hs_5'])
    #     return False
    # else:
    #     print('满足换手率下降',today['hs_5'])

    if abs(today['涨跌幅']) >= 5:
        return False
    # else:
    #     print('满足涨跌幅小于5%')

    return True
def select_stocks():
    """主函数：筛选符合条件的股票"""
    stock_list = filter_stocks(close_min=12,close_max=98)
    # stock_list=['300468']
    result1 = [] #突破
    result2 = [] #回踩
    for code in tqdm(stock_list, desc="选股进度", bar_format="{l_bar}{bar:30}{r_bar}", colour="green"):
        try:
            df = get_kline(code, 'ak')
        except:
            time.sleep(1.5)
            df = get_kline(code, 'tu')
        if df is not None and is_breakout_volume(df):
            ##业绩涨的
            if is_up_yj(code):
                result1.append(code)

        if df is not None and is_strong_pullback(df):
            ##业绩涨的
            if is_up_yj(code):
                result2.append(code)
    return [result1, result2]

if __name__  ==  '__main__':
    # 执行选股
    # selected = select_stocks()
    # print("符合突破放量模型的股票：", selected)
    code=select_stocks()
    now = datetime.today().strftime('%Y%m%d%H%M')
    log.info(f'突破长度是{len(code[0])}')
    log.info(f'{code[0]}')
    send_email(f'{now}突破放量---： \n\n\n\n'+str(code[0]))
    send_email(f'{now}缩量回踩---： \n\n\n\n' + str(code[1]))

