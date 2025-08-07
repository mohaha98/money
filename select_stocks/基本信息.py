import tushare as ts
from datetime import datetime, timedelta
from tools.logger import log
pro = ts.pro_api()

def get_stock_code_by_name(name_keyword):
    df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
    result = df[df['name'].str.contains(name_keyword)].iloc[0]['ts_code']
    code=result.split('.')[0]
    ts_code = f"{code}.{'SH' if code.startswith('6') else 'SZ'}"
    return ts_code

#或者
#pro = ts.pro_api('your token')
def get_introduction(code):
    if any(char.isdigit() for char in code):
        pass
    else:
        code=get_stock_code_by_name(code)
    df = pro.stock_company(ts_code=code, fields='ts_code,introduction,main_business,business_scope,province,com_name')
    introduction=df['introduction'][0]
    business_scope=df['business_scope'][0]
    main_business = df['main_business'][0]
    print(f"{df['com_name'][0]}--{df['province'][0]}  {df['ts_code'][0]}")
    # print(f'公司介绍：{introduction}')
    print(f'业务产品：{main_business}')
    print(f'经营范围：{business_scope}')

def get_forecast(code):
    if any(char.isdigit() for char in code):
        pass
    else:
        code=get_stock_code_by_name(code)
    df = pro.forecast_vip(ts_code=code,fields='ts_code,ann_date,end_date,type,p_change_min,p_change_max,net_profit_min').iloc[:2]
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
    if any(char.isdigit() for char in code):
        pass
    else:
        code = get_stock_code_by_name(code)
    # 获取单个股票数据
    today = datetime.today().strftime('%Y%m%d')
    df = pro.moneyflow_dc(ts_code=code, trade_date=today).iloc[0]
    # df2 = pro.moneyflow_dc(ts_code=code, trade_date=today).iloc[0]
    # print(df)
    print(f"{df['trade_date']}净流入 {df['net_amount']}万元")


def get_information(code):

    get_introduction(code)
    get_forecast(code)
    money_go(code)

if __name__  ==  '__main__':
    # get_information('紫光国')

    get_information('紫光国')

