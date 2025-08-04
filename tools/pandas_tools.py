"""=================不积跬步无以至千里==================
作    者： LEGION
创建时间： 2025/7/15 21:58
文件名： pandas_tools.py
功能作用： 
=================不积小流无以成江海=================="""
import pandas as pd
from typing import List

def parse_kline_to_dataframe(data: List[str]) -> pd.DataFrame:
    """
    将K线字符串列表转换为 pandas.DataFrame

    参数：
        data: List[str]，每个字符串是一行K线数据，逗号分隔

    返回：
        pandas.DataFrame，结构化的K线数据
    """
    # 定义列名（注意：顺序要和数据一致）
    columns = ['日期', '开盘价', '收盘价', '最高价', '最低价', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']

    # 拆分数据并转为结构化列表
    parsed_data = []
    for row in data:
        items = row.split(",")
        # 保证格式正确再处理
        if len(items) == len(columns):
            parsed_data.append([items[0]] + [float(i) for i in items[1:]])
        else:
            print(f"格式错误跳过：{row}")

    # 转换为 DataFrame
    df = pd.DataFrame(parsed_data, columns=columns)
    # 选择并返回指定字段
    return df[['日期', '开盘价', '收盘价', '最高价', '最低价', '成交量', '涨跌额', '涨跌幅','换手率']]


if __name__ == '__main__':
    raw_data = [
        '2025-07-14,34.43,34.23,35.75,34.11,608521,2117810815.03,4.93,2.92,0.97,4.12',
        '2025-07-15,34.03,33.88,34.23,33.21,480851,1621202191.45,2.98,-1.02,-0.35,3.26'
    ]

    # 调用函数
    df = parse_kline_to_dataframe(raw_data)

    # 查看结果
    # for _, row in df.iterrows():
    #     print(f"{row['开盘价']} 收盘价: {row['开盘价']} 涨跌幅: {row['成交额']}%")

    # second_row = df.iloc[1]
    # print(second_row)
    close_price = df.iloc[-1]
    print(close_price)

