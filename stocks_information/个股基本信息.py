import pandas as pd
import tushare as ts
from datetime import datetime, timedelta
from tools.logger import log
from tools.send_request import send_request
from core.stocks import is_up_yj, get_kline
import akshare as ak
pro = ts.pro_api()


def get_stock_code_by_name(code):
    if any(char.isdigit() for char in code):
        pass
    else:
        today = datetime.today().strftime('%Y%m%d')
        df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
        result = df[df['name'].str.contains(code)].iloc[0]['ts_code']
        code=result.split('.')[0]
    ts_code = f"{code}.{'SH' if code.startswith('6') else 'SZ'}"
    return ts_code



def hxtc_dc(code):
    """
核心题材
    """
    code = get_stock_code_by_name(code)
    try:
        url = "https://datacenter.eastmoney.com/securities/api/data/v1/get"
        payload = {'reportName':"RPT_F10_CORETHEME_BOARDTYPE",
                   "columns":"SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,NEW_BOARD_CODE,BOARD_NAME,SELECTED_BOARD_REASON,IS_PRECISE,BOARD_RANK,BOARD_YIELD,DERIVE_BOARD_CODE",
                   "quoteColumns": 'f3~05~NEW_BOARD_CODE~BOARD_YIELD',
                   "filter": f'(SECUCODE="{code}")(IS_PRECISE="1")',
                   "pageNumber":1,
                   "source": "HSF10",
                   "sortColumns": 'BOARD_RANK',
                   'client':'PC',
                   'sortTypes':1}
        haed={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'}
        print('---------------------核心题材--------------------')
        response = send_request("GET", url, data=payload,headers=haed).get('result').get('data')
        for item in response:
            print(f"{item['BOARD_NAME']}--{item['SELECTED_BOARD_REASON']}")
    except:
        return None




#
#pro = ts.pro_api('your token')
def get_introduction(code):
    """
    基本信息
    """
    code=get_stock_code_by_name(code)
    df = pro.stock_company(ts_code=code, fields='ts_code,introduction,main_business,business_scope,province,com_name')
    # print(df)
    # introduction=df['introduction'][0]
    business_scope=df['business_scope'][0]
    main_business = df['main_business'][0]
    #查市值 当前价格
    sz = pro.daily_basic(
        ts_code=code,  # 空表示取所有股票
        # trade_date='20250811',
        fields='ts_code,trade_date,total_mv,circ_mv,close'
    ).sort_values(by='total_mv', ascending=False).sort_values(by='trade_date', ascending=False).iloc[0]

    print('---------------------基本信息--------------------')
    print(f"{df['com_name'][0]}--{df['province'][0]}  {df['ts_code'][0]}  市值{int(sz['total_mv']/ 10000)}亿   当前价格：{sz['close']}" )
    # print(f'公司介绍：{introduction}')
    print(f'业务产品：{main_business}')
    print(f'经营范围：{business_scope}')

def get_forecast(code):
    """
    业绩情况
    """

    print('---------------------业绩情况--------------------')
    code=get_stock_code_by_name(code)
    df = ak.stock_financial_abstract_ths(symbol=code[:-3]).sort_values(by='报告期', ascending=False).iloc[0]
    #预披露日期
    pre_date = pro.disclosure_date(ts_code=code).sort_values(by='pre_date', ascending=False).iloc[0]['pre_date']
    print(f'预披露日期：{pre_date}')
    print(f"{df['报告期']}业绩：{float(df['净利润同比增长率'].replace('%', ''))}%")
    df1 = pro.fina_mainbz(ts_code=code, type='P',fields='end_date,bz_item,bz_cost').iloc[:12]
    # 2. 筛选出所有 end_date 与第一条相同的记录
    filtered_df = df1[df1['end_date'] == df1.iloc[0]['end_date']]
    # 3. 按 bz_cost 倒序排序
    result_df = filtered_df.sort_values(by='bz_cost', ascending=False)['bz_item'][:3]
    print(f"前三利润来源：{result_df.tolist()}")
    # print(result_df[1])

def money_go(code):
    """
    资金流入
    """
    print('---------------------资金流入--------------------')
    code = get_stock_code_by_name(code)
    # 获取单个股票数据
    today = datetime.today().strftime('%Y%m%d')
    df = pro.moneyflow_dc(ts_code=code)[::-1] ##颠倒过来 最新的在最下面
    df['avg5'] = df['net_amount'].rolling(5).mean()
    df['avg10'] = df['net_amount'].rolling(10).mean()
    df = df.iloc[-1]
    print(f"{df['trade_date']}净流入 {df['net_amount']}万  五日平均：{round(df['avg5'],1)}万   十日平均：{round(df['avg10'],1)}万")
    print(f"【超大单】净流入占比 {df['buy_elg_amount_rate']}%  流入金额{df['buy_elg_amount']}万")
    print(f"【大单】净流入占比 {df['buy_lg_amount_rate']}%   流入金额{df['buy_lg_amount']}万")
    print(f"【中单】净流入占比 {df['buy_md_amount_rate']}%   流入金额{df['buy_md_amount']}万")
    print(f"【小单】净流入占比 {df['buy_sm_amount_rate']}%   流入金额{df['buy_sm_amount']}万")


def jszb(code):
    """
    技术指标
    """

    print('---------------------技术指标--------------------')
    code = get_stock_code_by_name(code)[:-3]
    df = get_kline(code)
    if len(df) < 30:
        raise "kline长度不够"
    df['ma5'] = df['收盘价'].rolling(5).mean()
    df['ma10'] = df['收盘价'].rolling(10).mean()
    df['ma20'] = df['收盘价'].rolling(20).mean()
    df['vol5'] = df['成交量'].rolling(5).mean()
    df['vol10'] = df['成交量'].rolling(10).mean()
    df['hs_5'] = df['换手率'].rolling(5).mean()
    df['hs_10'] = df['换手率'].rolling(10).mean()
    today = df.iloc[-1]
    print(f"{today['日期']}   涨幅:{today['涨跌幅']}%")
    print(f"收盘价   成交量(万手)   换手率   ma5   ma10   ma20   vol5(万手)   vol10(万手)   hs_5   hs_10")
    print(f"{today['收盘价']}     {round(today['成交量']/10000,1)}        {today['换手率']}  {round(today['ma5'],2)}  {round(today['ma10'],2)}  {round(today['ma20'],2)}    {round(today['vol5']/10000,1)}        {round(today['vol10']/10000,1)}        {round(today['hs_5'],2)}   {round(today['hs_10'],2)}")






def get_information(code):
    get_introduction(code)
    jszb(code)
    get_forecast(code)
    money_go(code)
    hxtc_dc(code)


if __name__  ==  '__main__' :
    # pd.set_option('display.max_colwidth', 20)
    # pd.set_option('display.float_format', '{:.2f}'.format)
    get_information('300037')



