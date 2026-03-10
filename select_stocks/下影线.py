
from datetime import datetime
from tools.logger import log
from core.stocks import get_kline
from core.stocks import filter_stocks,is_up_yj
from tqdm import tqdm
from tools.send_email import send_email

def is_long_donw_line(df):
    """
    强势股 · 中途调整 · 二次上攻模型（实战版）
    适合：短线 / 波段 / 打板后的低吸
    """

    if len(df) < 40:
        return False

    df = df.copy()

    # ================= 均线 & 量能 =================
    df['ma5'] = df['收盘价'].rolling(5).mean()
    df['ma10'] = df['收盘价'].rolling(10).mean()
    df['ma20'] = df['收盘价'].rolling(20).mean()

    df['vol_ma5'] = df['成交量'].rolling(5).mean()
    df['vol_ma10'] = df['成交量'].rolling(10).mean()

    # ================= 最近数据 =================
    today = df.iloc[-1]
    prev = df.iloc[-2]

    # =================================================
    # 一、前期必须是“强势启动过”
    # =================================================

    # 1️⃣ 近 5 日内出现涨停（强资金记忆）
    last_5 = df.iloc[-8:-1]
    if not (last_5['涨跌幅'] >= 9.8).any():
        return False

    # 2️⃣ 近 20 日涨幅必须明显
    close_20_ago = df['收盘价'].iloc[-21]
    if today['收盘价'] / close_20_ago - 1 < 0.15:
        return False

    if today['涨跌幅']<-5:
        return False
    # =================================================
    # 二、趋势必须保持（这是“中途”，不是“结束”）
    # =================================================

    # 多头结构
    if not (today['ma5'] > today['ma10'] > today['ma20']):
        return False

    # 不破趋势线（核心）
    if today['收盘价'] < today['ma20']:
        return False

    # =================================================
    # 三、回踩必须是“缩量洗盘”
    # =================================================

    # 条件2：缩量
    if today['成交量'] >= today['vol_ma5']*1.3:
        return False

    # # 回调幅度不能过大（防止转弱）
    # recent_high = df['最高价'].iloc[-10:].max()
    # if (recent_high - today['收盘价']) / recent_high > 0.12:
    #     return False

    # =================================================
    # 四、止跌信号（这是“可买”的关键）
    # =================================================

    # K线实体小（十字 / 小阳）
    lower_shadow = min(today['开盘价'], today['收盘价']) - today['最低价']
    upper_shadow = today['最高价'] - max(today['开盘价'], today['收盘价'])
    entity = abs(today['收盘价'] - today['开盘价'])
    total_range = today['最高价'] - today['最低价']
    if entity / today['收盘价'] > 0.02:
        return False

    # 下影线 ≥ 实体（经典）
    if lower_shadow < entity *1.3:
        return False

    return True


def select_stocks():
    """主函数：筛选符合条件的股票"""
    stock_list = filter_stocks(close_min=12,close_max=90)
    result = []
    for code in tqdm(stock_list, desc="选股进度", bar_format="{l_bar}{bar:30}{r_bar}", colour="green"):
        df = get_kline(code,'ak')
        if df is not None and is_long_donw_line(df):
            ##业绩涨的
            if is_up_yj(code):
                result.append(code)
    return result

if __name__  ==  '__main__':
    # 执行选股
    # selected = select_stocks()
    # print("符合突破放量模型的股票：", selected)
    code=select_stocks()
    now = datetime.today().strftime('%Y%m%d%H%M')
    log.info(f'长度是{len(code)}')
    log.info(f'{code}')
    send_email(f'{now}突破放量---： \n\n\n\n'+str(code))

