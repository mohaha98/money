import time
from datetime import datetime
from tools.logger import log
from core.etf import get_all_etf,etf_kline
from tqdm import tqdm
from tools.send_email import send_email
def is_breakout_volume(df):
    """判断是否符合突破放量选股模型"""
    if len(df) < 30:
        return False


    df['ma5'] = df['收盘价'].rolling(5).mean()
    df['ma10'] = df['收盘价'].rolling(10).mean()
    df['ma20'] = df['收盘价'].rolling(20).mean()
    today = df.iloc[-1]

    last_close = df.iloc[-1]['收盘价']
    last_vol = df.iloc[-1]['成交量']
    high_20 = df['收盘价'][-15:-1].max()  # 不包含今天
    # print(high_20)
    avg_volume_5 = df['成交量'][-6:-1].mean()  # 不含今天

    # -------- 条件1：均线多头排列 --------
    if not (today['ma5'] > today['ma10'] > today['ma20'] and today['收盘价'] > today['ma20']):
        # print('不满足多头')
        return False

    if last_close > high_20 and last_vol > avg_volume_5 * 1.5:
        return True
    return False

def select_stocks():
    """主函数：筛选符合条件的股票"""
    stock_list = get_all_etf()
    # stock_list=['159792.SZ']
    result = []
    for code in tqdm(stock_list, desc="选股进度", bar_format="{l_bar}{bar:30}{r_bar}", colour="green"):
        try:
            df = etf_kline(code)
        except Exception as e:
            continue
        if df is not None and is_breakout_volume(df):
            result.append(code[:-3])
    return result

if __name__  ==  '__main__':
    # 执行选股
    # selected = select_stocks()
    # print("符合突破放量模型的股票：", selected)
    code=select_stocks()
    now = datetime.today().strftime('%Y%m%d%H%M')
    log.info(f'长度是{len(code)}')
    log.info(f'{code}')
    send_email(f'{now}etf_突破放量_筛选： \n\n\n\n'+str(code))