"""=================不积跬步无以至千里==================
作    者： LEGION
创建时间： 2026/3/10 18:33
文件名： 超跌.py
功能作用： 
=================不积小流无以成江海=================="""

import pandas as pd
import numpy as np
from core.stocks import get_kline

def calculate_rsi(series, period=6):
    """计算RSI指标（6日）"""
    delta = series.diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # 移动平均（平滑处理）
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()

    # 避免除以0
    avg_loss = avg_loss.replace(0, 0.0001)
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def stock_backtest(
        df,  # 过去5年K线数据，需包含：datetime, close（收盘价）
        hold_days=3,  # 持仓天数
        lookback_days=60,  # 计算“过去最低前二”的回溯天数
        profit_stop=None,  # 可选：止盈比例（比如0.05=5%）
        loss_stop=None  # 可选：止损比例（比如0.03=3%）
):
    """
    股票回测函数：基于RSI_6<25+股价新低前二的买点，计算胜率
    """
    # 复制数据避免修改原数据
    df = df.copy()
    # 确保数据按时间排序
    df = df.sort_values('日期').reset_index(drop=True)

    # ========== 1. 计算核心指标 ==========
    # 计算6日RSI
    df['rsi_6'] = calculate_rsi(df['收盘价'], period=6)
    # 计算过去lookback_days天的最低价前二（第2小值）
    df['lowest_2'] = df['收盘价'].rolling(window=lookback_days, min_periods=1).apply(
        lambda x: np.partition(x, 1)[1] if len(x) >= 2 else x.min()
    )
    # 标记买入信号：RSI_6<25 且 收盘价≤过去最低前二
    df['buy_signal'] = (df['rsi_6'] < 20) & (df['收盘价'] <= df['lowest_2'])

    # ========== 2. 模拟买卖交易 ==========
    trades = []  # 存储所有交易记录
    in_position = False  # 是否持仓
    buy_price = 0  # 买入价格
    buy_date = None  # 买入日期
    hold_count = 0  # 持仓天数计数

    for idx, row in df.iterrows():
        # 未持仓，且触发买入信号 → 买入
        if not in_position and row['buy_signal']:
            buy_price = row['收盘价']
            buy_date = row['日期']
            in_position = True
            hold_count = 0
            continue

        # 已持仓 → 计算持仓天数，判断是否卖出
        if in_position:
            hold_count += 1
            current_price = row['收盘价']
            # 计算浮盈浮亏
            profit_rate = (current_price - buy_price) / buy_price

            # 卖出条件：1.持仓天数达标 2.触发止盈/止损（可选）
            sell_condition = False
            # 条件1：持仓天数达到设定值
            if hold_count >= hold_days:
                sell_condition = True
            # 条件2：触发止盈
            if profit_stop and profit_rate >= profit_stop:
                sell_condition = True
            # 条件3：触发止损
            if loss_stop and profit_rate <= -loss_stop:
                sell_condition = True

            # 执行卖出
            if sell_condition:
                trades.append({
                    'buy_date': buy_date,
                    'sell_date': row['日期'],
                    'buy_price': buy_price,
                    'sell_price': current_price,
                    'profit_rate': profit_rate,
                    'hold_days': hold_count,
                    'is_profit': profit_rate > 0
                })
                # 清空持仓状态
                in_position = False
                buy_price = 0
                buy_date = None
                hold_count = 0

    # ========== 3. 计算回测结果 ==========
    if len(trades) == 0:
        return {
            '总交易次数': 0,
            '盈利次数': 0,
            '亏损次数': 0,
            '胜率(%)': 0.0,
            '平均盈利比例(%)': 0.0,
            '平均亏损比例(%)': 0.0,
            '总收益比例(%)': 0.0,
            '交易明细': []
        }

    # 转换为DataFrame方便计算
    trades_df = pd.DataFrame(trades)
    total_trades = len(trades_df)
    profit_trades = trades_df[trades_df['is_profit']]
    loss_trades = trades_df[~trades_df['is_profit']]

    # 核心指标计算
    win_rate = len(profit_trades) / total_trades * 100
    avg_profit_rate = profit_trades['profit_rate'].mean() * 100 if len(profit_trades) > 0 else 0
    avg_loss_rate = loss_trades['profit_rate'].mean() * 100 if len(loss_trades) > 0 else 0
    total_profit_rate = (trades_df['profit_rate'] + 1).prod() - 1  # 复利总收益
    total_profit_rate = total_profit_rate * 100

    return {
        '总交易次数': total_trades,
        '盈利次数': len(profit_trades),
        '亏损次数': len(loss_trades),
        '胜率(%)': round(win_rate, 2),
        '平均盈利比例(%)': round(avg_profit_rate, 2),
        '平均亏损比例(%)': round(avg_loss_rate, 2),
        '总收益比例(%)': round(total_profit_rate, 2),
        '交易明细': trades_df.to_dict('records')
    }


# ========== 测试示例 ==========
if __name__ == "__main__":
    # 构造模拟5年K线数据（你替换为真实接口数据即可）

    df = get_kline('300661','ef')

    # 执行回测
    backtest_result = stock_backtest(
        df=df,
        hold_days=3,  # 持仓5天
        lookback_days=40,  # 过去60天最低价前二
        # profit_stop=0.05,  # 可选：盈利5%止盈
        # loss_stop=0.03  # 可选：亏损3%止损
    )

    # 打印回测结果
    print("===== 回测结果汇总 =====")
    for key, value in backtest_result.items():
        if key != '交易明细':
            print(f"{key}: {value}")

    # 打印前5笔交易明细（可选）
    print("\n===== 前5笔交易明细 =====")
    for trade in backtest_result['交易明细'][:10]:
        print(f"买入日期：{trade['buy_date']}, 卖出日期：{trade['sell_date']}, "
              f"买入价：{trade['buy_price']:.2f}, 卖出价：{trade['sell_price']:.2f}, "
              f"盈利比例：{trade['profit_rate']:.2%}, 是否盈利：{trade['is_profit']}")


