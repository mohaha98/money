"""=================不积跬步无以至千里==================
作    者： LEGION
创建时间： 2025/8/31 12:17
文件名： 游资去向.py
功能作用： 
=================不积小流无以成江海=================="""
import os

import tushare as ts
import pandas as pd
from datetime import datetime
from tools import config
from tools.config import DATA_DIR
pro = ts.pro_api()
now = datetime.today().strftime('%Y%m%d')

def main(date):

    # 获取单日全部明细
    df = pro.hm_detail(trade_date=date,fields='trade_date,hm_name,ts_code,ts_name,buy_amount,sell_amount,net_amount')
    df.rename(columns={
        "trade_date": "日期",
        "hm_name": "游资名称",
        "ts_code": "股票代码",
        "ts_name": "股票名称",
        "buy_amount": "买入金额（元）",
        "sell_amount": "卖出金额（元）",
        "net_amount": "净买卖（元）"
    }, inplace=True)
    # print(df)
    filepath = os.path.join(config.DATA_DIR, f'游资去向{date}.xlsx')
    df.to_excel(filepath, index=False)


if __name__ == '__main__':
    date='20251225'
    main(date)
    # print(DATA_DIR)