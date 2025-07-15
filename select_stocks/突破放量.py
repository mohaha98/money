# ------------------------------
# 股票池过滤器：排除 ST、低价、小市值股票
# ------------------------------
from core.stocks import get_kline
from core.stocks import filter_stocks
from tqdm import tqdm
from tools.send_email import send_email

def is_breakout_volume(df):
    """判断是否符合突破放量选股模型"""
    if len(df) < 25:
        return False
    last_close = df.iloc[-1]['收盘价']
    last_vol = df.iloc[-1]['成交量']
    high_20 = df['收盘价'][-21:-1].max()  # 不包含今天
    # print(high_20)
    avg_volume_5 = df['成交量'][-6:-1].mean()  # 不含今天

    if last_close > high_20 and last_vol > avg_volume_5 * 2:
        return True
    return False

def select_stocks():

    """主函数：筛选符合条件的股票"""
    stock_list = filter_stocks(LB_min=2,HSL_min=3)
    # stock_list=['601311']
    result = []
    for code in tqdm(stock_list, desc="选股进度", bar_format="{l_bar}{bar:30}{r_bar}", colour="green"):
        df = get_kline(code)
        if df is not None and is_breakout_volume(df):
            result.append(code)
    return result

if __name__ == '__main__':
    # 执行选股
    # selected = select_stocks()
    # print("符合突破放量模型的股票：", selected)
    code=select_stocks()
    print(code)
    print(len(code))
    send_email('突破放量---：'+str(code))

