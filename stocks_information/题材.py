import tushare as ts
import pandas as pd
from datetime import datetime
pro = ts.pro_api()
now = datetime.today().strftime('%Y%m%d')
def tc(date = now):
    df = (
        pro.kpl_concept(trade_date=date)
        .sort_values(by='up_num', ascending=False)
        .rename(columns={
            'trade_date': '交易日期',
            "ts_code": "题材代码",
            "name": "题材名称",
            "z_t_num": "涨停数量",
            "up_num": "排名上升位数",
        })
        [['交易日期', '题材名称', '涨停数量', '排名上升位数']]
        .head(20)   # 取前20行
    )
    print(df.to_string(index=False))

if __name__ == '__main__':
    tc('20250820')