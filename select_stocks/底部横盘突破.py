from datetime import datetime

from core.stocks import get_kline
from core.stocks import filter_stocks,is_up_yj
from tqdm import tqdm
from tools.send_email import send_email
from tools.logger import log
# ------------------------------
# 判断是否符合底部横盘突破模式
# ------------------------------
def is_platform_breakout(df):
    """
    策略逻辑：
    - 过去20日横盘（波动小）
    - 今日突破平台上沿
    - 今日放量明显
    """
    if len(df) < 21:
        return False

    recent = df[-10:]
    today = recent.iloc[-1]
    before = recent.iloc[:-1]

    high_max = before['最高价'].max()
    low_min = before['最低价'].min()
    max_fluct = (high_max - low_min) / low_min

    # 横盘震荡（高低差 < 8%）
    if max_fluct > 0.12:
        return False

    # 今日收盘 > 平台最高（突破）
    if today['收盘价'] <= high_max:
        return False

    # 放量突破：今日成交量 > 前5日均量 * 1.5
    avg_vol_5 = before['成交量'][-5:].mean()
    if today['成交量'] <= 1.5 * avg_vol_5:
        return False

    return True

# ------------------------------
# 主函数：遍历所有符合过滤器的股票
# ------------------------------
def select_stocks():

    """主函数：筛选符合条件的股票"""
    stock_list = filter_stocks(LB_min=2,HSL_min=3,close_min=13)
    # stock_list=['601311']
    result = []
    for code in tqdm(stock_list, desc="选股进度", bar_format="{l_bar}{bar:30}{r_bar}", colour="green"):
        df = get_kline(code)
        if df is not None and is_platform_breakout(df):
            ##业绩涨的
            if is_up_yj(code):
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
    send_email(f'{now}横盘突破---： \n\n\n\n'+str(code))