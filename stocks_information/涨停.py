import tushare as ts
import pandas as pd
from datetime import datetime

pro = ts.pro_api()
def get_limit_up_stocks(date=None):
    """
    获取指定日期的涨停股票列表（默认为今天）
    :param date: 日期，格式 'YYYYMMDD'
    :return: 涨停股票 DataFrame
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")

    # 获取行情数据
    df = pro.limit_list_d(trade_date=date, limit_type='U',fields='ts_code,trade_date,industry,name,close,pct_chg,open_times,up_stat,limit_times,total_mv')
    df["total_mv"] = df["total_mv"]/100000000
    df.rename(columns={
        'total_mv' : '总市值(亿)',
        "ts_code": "代码",
        "trade_date": "日期",
        "industry": "行业",
        "name": "名字",
        "close": "收盘价",
        "pct_chg": "涨跌幅",
        "open_times": "炸板次数",
        "up_stat": "涨停统计",
        "limit_times": "连板数"
    }, inplace=True)
    df = df[
        (df["连板数"] ==1 ) &
        (df["总市值(亿)"] > 130) &
        (df["涨跌幅"] < 11) &
        (df["收盘价"] > 12) &
        (df["收盘价"] < 120) &
        (df["炸板次数"] < 4)
    ]
    if df.empty:
        print(f"{date} 没有交易数据")
        return df


    return df[['总市值(亿)','代码', '名字', '行业','炸板次数','涨停统计','连板数']]

if __name__ == '__main__':
    pd.set_option('display.float_format', '{:.2f}'.format)
    # 示例：获取今天涨停股票
    limit_up_list = get_limit_up_stocks('20250822')
    print(limit_up_list.to_string(index=False))


#
