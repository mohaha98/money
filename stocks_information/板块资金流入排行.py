"""=================不积跬步无以至千里==================
作    者： LEGION
创建时间： 2025/8/5 20:27
文件名： 板块资金流入排行.py
功能作用： 
=================不积小流无以成江海=================="""
import pandas as pd

from tools.send_email import send_email
import tushare as ts
from tools.logger import log
from datetime import datetime
# # 替换成你自己的 token
# ts.set_token('2876ea85cb005fb5fa17c809a98174f2d5aae8b1f830110a5ead6211')
#
# # 初始化接口

#东方财富板块净流入
def dc(trade_date):
    print('---------------------东方财富板块资金流入--------------------')
    pro = ts.pro_api()
    df = pro.moneyflow_ind_dc(trade_date=trade_date, fields='trade_date,name,pct_change, net_amount,buy_sm_amount_stock')
    # 重命名表头
    df = df.rename(columns={
        'name': '板块',
        'net_amount': '净流入',
        'pct_change': '涨跌幅',
        'trade_date': '日期',
        # 'net_amount_rate':'净流入净占比',
        'buy_sm_amount_stock':'净流入最大股'
    })
    df['净流入(亿)'] = df['净流入']/1e8
    df = df.sort_values(by='净流入', ascending=False)
    # print(df.head(15))
    df = df[['日期', '板块', '涨跌幅', '净流入(亿)', '净流入最大股']].head(12)
    print(df)
    name_list = df['板块'].tolist()
    # log.info(f'{trade_date}东方财富资金流入排名： \n{name_list}')
    # send_email(f'{trade_date} 东方财富资金流入排名： \n\n\n\n' + str(name_list))
    # return name_list

# 板块流入
def ths1(trade_date):
    print('---------------------同花顺板块资金流入--------------------')
    pro = ts.pro_api()
    df = pro.moneyflow_ind_ths(trade_date=trade_date)
    df = df.rename(columns={
        'industry': '板块',
        'net_amount': '净流入',
        'pct_change': '涨跌幅',
        'trade_date': '日期',
        # 'net_amount_rate':'净流入净占比',
        'lead_stock':'领涨股'
    })
    df = df.sort_values(by='净流入', ascending=False)
    df = df[['日期','板块', '涨跌幅', '净流入','领涨股']].head(10)
    print(df)
    # name_list = df['板块'].tolist()
    # log.info(f'{trade_date}同花顺资金流入排名：\n{name_list}')
    # send_email(f'{trade_date} 同花顺资金流入排名： \n\n\n\n' + str(name_list))
    # return name_list

#概念行业资金流入
def ths(trade_date):
    print('---------------------同花顺概念资金流入--------------------')
    pro = ts.pro_api()
    df = pro.moneyflow_cnt_ths(trade_date=trade_date)
    df = df.rename(columns={
        'name': '板块',
        'net_amount': '净流入',
        'pct_change': '涨跌幅',
        'trade_date': '日期',
        # 'net_amount_rate':'净流入净占比',
        'lead_stock':'领涨股'
    })
    df = df.sort_values(by='净流入', ascending=False)
    df = df[['日期','板块', '涨跌幅', '净流入','领涨股']].head(10)
    print(df)
    # name_list = df['板块'].tolist()
    # log.info(f'{trade_date}同花顺资金流入排名：\n{name_list}')
    # send_email(f'{trade_date} 同花顺资金流入排名： \n\n\n\n' + str(name_list))
    # return name_list

def gg_moneyflow_ths(date):
    print('---------------------同花顺个股资金流入--------------------')
    pro = ts.pro_api()
    df = pro.moneyflow_ths(trade_date=date)
    df = df.rename(columns={
        'name': '股票名称',
        'net_amount': '净流入',
        'pct_change': '涨跌幅',
        'trade_date': '日期',
        # 'net_amount_rate':'净流入净占比',
        'latest': '最新价'
    })
    df = df.sort_values(by='净流入', ascending=False)
    df = df[['日期', '股票名称', '涨跌幅', '净流入', '最新价']]
    print(df.head(10))

def gg_moneyflow_dc(date):
    print('---------------------东方财富个股资金流入--------------------')
    pro = ts.pro_api()
    df = pro.moneyflow_dc(trade_date=date)
    df = df.rename(columns={
        'name': '股票名称',
        'net_amount': '净流入',
        'pct_change': '涨跌幅',
        'trade_date': '日期',
        # 'net_amount_rate':'净流入净占比',
        'close': '最新价'
    })
    df = df.sort_values(by='净流入', ascending=False)
    df = df[['日期', '股票名称', '涨跌幅', '净流入', '最新价']]
    print(df.head(10))

if __name__  ==  '__main__':
    pass
    pd.set_option('display.max_colwidth', 20)
    pd.set_option('display.float_format', '{:.2f}'.format)
    # ts.set_token('2876ea85cb005fb5fa17c809a98174f2d5aae8b1f830110a5ead6211')
    now = datetime.today().strftime('%Y%m%d')
    date='20250820'
    dc(date)
    ths1(date)
    ths(date)
    gg_moneyflow_dc(date)




