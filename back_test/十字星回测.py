"""=================不积跬步无以至千里==================
作    者： LEGION
创建时间： 2026/3/10
文件名： 十字星回测.py
功能作用：十字星缩量+多头排列+放量回测，计算胜率
=================不积小流无以成江海=================="""

import pandas as pd
import numpy as np

from core.stocks import get_kline



def _add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    在K线数据上补充策略所需指标字段。

    期望原始字段包含：
    - 日期
    - 开盘价、收盘价、最高价、最低价
    - 成交量
    """
    df = df.copy()
    df = df.sort_values("日期").reset_index(drop=True)
    print(df)

    # 实体与振幅
    df["real_body"] = (df["收盘价"] - df["开盘价"]).abs()
    df["high_low_range"] = (df["最高价"] - df["最低价"]).abs()

    # 十字星：实体相对振幅很小（这里取 20% 为阈值，可调）
    df["is_doji"] = (df["high_low_range"] > 0) & (
        df["real_body"] <= df["high_low_range"] * 0.3
    )

    # 缩量：当日成交量小于前一日
    df["is_shrink_vol"] = df["成交量"] < df["成交量"].shift(1)

    # 多头排列：5日均线 > 10日均线 > 20日均线
    df["ma5"] = df["收盘价"].rolling(5, min_periods=5).mean()
    df["ma10"] = df["收盘价"].rolling(10, min_periods=10).mean()
    df["ma20"] = df["收盘价"].rolling(20, min_periods=20).mean()
    df["is_bull_trend"] = (df["ma5"] > df["ma10"]) & (df["ma10"] > df["ma20"])

    # RSI_6（简单实现：基于收盘价的 6 日 RSI）
    # 计算价格变动
    df["close_change"] = df["收盘价"].diff()
    df["gain"] = df["close_change"].clip(lower=0)
    df["loss"] = -df["close_change"].clip(upper=0)
    # 6 日平均涨跌
    df["avg_gain_6"] = df["gain"].rolling(6, min_periods=6).mean()
    df["avg_loss_6"] = df["loss"].rolling(6, min_periods=6).mean()
    # 避免除以 0
    rs = df["avg_gain_6"] / df["avg_loss_6"].replace(0, np.nan)
    df["RSI_6"] = 100 - (100 / (1 + rs))

    # 前 15 个交易日内是否出现过超跌（RSI_6 < 25）
    df["pre15_has_oversold"] = (
        (df["RSI_6"] < 25)
        .shift(1)
        .rolling(15, min_periods=1)
        .max()
        .fillna(0)
        .astype(bool)
    )

    # 10日均量（用于放量判断）
    df["vol_ma10"] = df["成交量"].rolling(10, min_periods=10).mean()

    # ---------------- 前期10日内有放量 ----------------
    # 定义“放量”：成交量 > 2 * 10日均量（阈值可按需调整）
    df["is_big_vol"] = df["成交量"] > 1.8 * df["vol_ma10"]
    # 对 is_big_vol 做滚动10日（不含当日），只要过去10日内出现过一次即满足
    df["pre10_has_big_vol"] = (
        df["is_big_vol"]
        .shift(1)
        .rolling(10, min_periods=1)
        .max()
        .fillna(0)
        .astype(bool)
    )



    # 汇总买入条件：十字星缩量 + 多头排列 + 前10日有放量 + 前15日存在超跌（RSI_6 < 25）
    df["buy_signal"] = (
        df["is_doji"]
        & df["is_shrink_vol"]
        & df["is_bull_trend"]
        & df["pre10_has_big_vol"]
        & df["pre15_has_oversold"]
    )

    return df


def doji_strategy_backtest(
    df: pd.DataFrame,
    hold_days: int = 3,
):
    """
    十字星缩量 + 多头排列 + 放量条件的回测函数。

    策略规则：
    - 当日K线为十字星（实体小于振幅20%）
    - 当日缩量（成交量 < 前一日）
    - 均线多头排列：MA5 > MA10 > MA20
    - 前10个交易日内出现过“放量日”（成交量 > 2 * 10日均量）
    - 当日成交量 > 前10日平均成交量的1.8倍
    - 收盘价买入，持仓 hold_days 天后收盘卖出
    - 盈利（卖出价 > 买入价）记为一次胜利
    """
    if df is None or df.empty:
        return {
            "总交易次数": 0,
            "盈利次数": 0,
            "亏损次数": 0,
            "胜率(%)": 0.0,
            "平均盈利比例(%)": 0.0,
            "平均亏损比例(%)": 0.0,
            "总收益比例(%)": 0.0,
            "交易明细": [],
        }

    df = _add_indicators(df)

    trades = []
    in_position = False
    buy_price = 0.0
    buy_date = None
    hold_count = 0

    for idx, row in df.iterrows():
        # 未持仓且出现买入信号：按收盘价买入
        if not in_position and row["buy_signal"]:
            buy_price = float(row["收盘价"])
            buy_date = row["日期"]
            in_position = True
            hold_count = 0
            continue

        # 已持仓：计数持仓天数，到期卖出
        if in_position:
            hold_count += 1
            current_price = float(row["收盘价"])
            profit_rate = (current_price - buy_price) / buy_price

            if hold_count >= hold_days:
                trades.append(
                    {
                        "buy_date": buy_date,
                        "sell_date": row["日期"],
                        "buy_price": buy_price,
                        "sell_price": current_price,
                        "profit_rate": profit_rate,
                        "hold_days": hold_count,
                        "is_profit": profit_rate > 0,
                    }
                )
                in_position = False
                buy_price = 0.0
                buy_date = None
                hold_count = 0

    # 汇总统计
    if len(trades) == 0:
        return {
            "总交易次数": 0,
            "盈利次数": 0,
            "亏损次数": 0,
            "胜率(%)": 0.0,
            "平均盈利比例(%)": 0.0,
            "平均亏损比例(%)": 0.0,
            "总收益比例(%)": 0.0,
            "交易明细": [],
        }

    trades_df = pd.DataFrame(trades)
    total_trades = len(trades_df)
    profit_trades = trades_df[trades_df["is_profit"]]
    loss_trades = trades_df[~trades_df["is_profit"]]

    win_rate = len(profit_trades) / total_trades * 100
    avg_profit_rate = (
        profit_trades["profit_rate"].mean() * 100 if len(profit_trades) > 0 else 0
    )
    avg_loss_rate = (
        loss_trades["profit_rate"].mean() * 100 if len(loss_trades) > 0 else 0
    )
    total_profit_rate = (trades_df["profit_rate"] + 1).prod() - 1
    total_profit_rate *= 100

    return {
        "总交易次数": int(total_trades),
        "盈利次数": int(len(profit_trades)),
        "亏损次数": int(len(loss_trades)),
        "胜率(%)": round(win_rate, 2),
        "平均盈利比例(%)": round(avg_profit_rate, 2),
        "平均亏损比例(%)": round(avg_loss_rate, 2),
        "总收益比例(%)": round(total_profit_rate, 2),
        "交易明细": trades_df.to_dict("records"),
    }


def backtest_single_stock(
    code: str,
    source: str = "ef",
    start_date: str | None = None,
    end_date: str | None = None,
    hold_days: int = 3,
):
    """
    方便直接对单只股票做十字星策略回测。

    使用示例：
        result = backtest_single_stock("300661", "ef")
        print(result["胜率(%)"])
    """
    df = get_kline(code, x=source, start_date=start_date, end_date=end_date)
    return doji_strategy_backtest(df, hold_days=hold_days)


if __name__ == "__main__":
    # 示例：对某一只股票做十字星策略回测
    result = backtest_single_stock("300661", "ef")
    print("===== 十字星策略回测结果 =====")
    for k, v in result.items():
        if k != "交易明细":
            print(f"{k}: {v}")

    # 打印每一笔交易的时间和盈亏情况
    if result["交易明细"]:
        print("\n===== 交易明细 =====")
        for trade in result["交易明细"]:
            buy_date = trade["buy_date"]
            sell_date = trade["sell_date"]
            profit_rate = trade["profit_rate"]
            print(
                f"买入日期: {buy_date}, 卖出日期: {sell_date}, "
                f"盈亏: {profit_rate:.2%}"
            )
    else:
        print("\n本次回测无交易记录。")

