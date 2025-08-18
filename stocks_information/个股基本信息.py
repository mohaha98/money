import tushare as ts
from datetime import datetime, timedelta
from tools.logger import log
from tools.send_request import send_request

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




#或者
#pro = ts.pro_api('your token')
def get_introduction(code):
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
    print('---------------------业绩情况--------------------')
    code=get_stock_code_by_name(code)
    df = pro.forecast_vip(ts_code=code,fields='ts_code,ann_date,end_date,type,p_change_min,p_change_max,net_profit_min').iloc[:4]
    #预披露日期
    pre_date = pro.disclosure_date(ts_code=code).sort_values(by='pre_date', ascending=False).iloc[0]['pre_date']
    print(f'预披露日期：{pre_date}')
    print(f"{df['ann_date'][0]}业绩预告:{df['type'][0]}({df['p_change_min'][0]}%)")
    print(f"{df['ann_date'][1]}:{df['type'][1]}")
    df1 = pro.fina_mainbz(ts_code=code, type='P',fields='end_date,bz_item,bz_cost').iloc[:12]
    # 2. 筛选出所有 end_date 与第一条相同的记录
    filtered_df = df1[df1['end_date'] == df1.iloc[0]['end_date']]
    # 3. 按 bz_cost 倒序排序
    result_df = filtered_df.sort_values(by='bz_cost', ascending=False)['bz_item'][:3]
    print(f"前三利润来源：{result_df.tolist()}")
    # print(result_df[1])

def money_go(code):
    print('---------------------资金流入--------------------')
    code = get_stock_code_by_name(code)
    # 获取单个股票数据
    today = datetime.today().strftime('%Y%m%d')
    df = pro.moneyflow_dc(ts_code=code).iloc[0]
    # df2 = pro.moneyflow_dc(ts_code=code, trade_date=today).iloc[0]
    # print(df)
    print(f"{df['trade_date']}净流入 {df['net_amount']}万")


def get_information(code):
    get_introduction(code)
    get_forecast(code)
    money_go(code)
    hxtc_dc(code)

if __name__  ==  '__main__':

    get_information('002080')


