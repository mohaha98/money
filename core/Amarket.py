"""=================不积跬步无以至千里==================
作    者： LEGION
创建时间： 2024/10/20 12:41
文件名： Amarket.py
功能作用： 
=================不积小流无以成江海=================="""
import time
from tqdm import tqdm
from tools.send_request import send_request
from tools.logger import log
from jsonpath import jsonpath
from tools.send_email import send_email
def all_company_code():
    """
    获取所有股票
    """

    url = "https://12.push2.eastmoney.com/api/qt/clist/get"

    payload = {'pn': '1',
               'pz': '6000',
               "fid": 'f3',
               "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048",
               "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152"}
    response = send_request('get', url, data=payload)
    data = jsonpath(response,'$.data.diff[*].f12')
    # print(data)
    return data


def get_QuoteID(code):
    """
    获取QuoteID，东方财富专用入参
    """
    url = "https://searchadapter.eastmoney.com/api/suggest/get"
    payload = {
                    "input": code,
                    "type": 14
                }
    response = send_request("GET", url, data=payload)
    QuoteID=response.get('QuotationCodeTable').get('Data')[0].get('QuoteID')
    # print(QuoteID)
    name=response.get('QuotationCodeTable').get('Data')[0].get('Name')
    return [QuoteID,name]


def get_detail(code):
    """
    股票详情 价格 开盘价 收盘价 量比等信息
    [名字，今天收盘价，今天开盘价，昨天开盘价，昨天收盘价，量比]
    """
    QuoteID=get_QuoteID(code)
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    payload = {'fields1':"f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13",
               "fields2":"f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
               "beg":0,
                "end":'20500101',
               "secid":QuoteID[0],
              "klt":"101",
               "fqt":1}
    response = send_request("GET", url, data=payload)
    today_kline=response.get('data').get('klines')[-1].split(",")
    yesterday_kline = response.get('data').get('klines')[-2].split(",")
    #######  名字        收盘           开盘           涨跌幅         成交量            最高            最低
    today=[QuoteID[1],today_kline[1],today_kline[2],today_kline[8],today_kline[5],today_kline[3],today_kline[4]]
    yesterday=[QuoteID[1],yesterday_kline[1],yesterday_kline[2],yesterday_kline[8],yesterday_kline[5],yesterday_kline[3],yesterday_kline[4]]
    # print(today_kline,yesterday_kline)
    return today,yesterday


def up_to_top(date):
    """
    涨停池的股票信息
    """

    url = "https://push2ex.eastmoney.com/getTopicZTPool"
    payload = {
                    "ut": "7eea3edcaed734bea9cbfc24409ed989",
                    "dpt": "wz.ztzt",
                    "Pageindex": 0,
                    "pagesize": 500,
                    "sort": "fbt:asc",
                    "date": date
                }
    response = send_request("GET", url,data=payload)
    return response.get("data").get('pool')

def up_to_top_code(date):
    """
    涨停池的股票信息
    """

    url = "https://push2ex.eastmoney.com/getTopicZTPool"
    payload = {
                    "ut": "7eea3edcaed734bea9cbfc24409ed989",
                    "dpt": "wz.ztzt",
                    "Pageindex": 0,
                    "pagesize": 500,
                    "sort": "fbt:asc",
                    "date": date
                }

    response = send_request("GET", url,data=payload)
    # print(jsonpath(response, '$.data.pool[*].c'))
    return jsonpath(response, '$.data.pool[*].c')


def contine_to_top_times(times):
    """
    连续涨停n次的股票
    """
    data=up_to_top()
    GP_set=set()
    for i in data:
        if i.get('lbc')>=times:
            GP_set.add(i.get('n'))
    print(f"连续涨停{times}次以上的股票有：\n {contine_to_top_times}" )

def hs(m,n):
    """
    涨停股票中，换手率大于n的股票
    """
    data=up_to_top()
    GP_set=set()
    for i in data:
        if m<=i.get('hs')<=n:
            GP_set.add(i.get('n'))
    print(f"换手率大于{n}的股票有：\n {GP_set}" )


def pd_cjl(QuoteID,n):
    """
    涨停股票中，排队和成交量比例大于n的股票
    """
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    payload = {
                    "invt": 2,
                    "fltt": 1,
                    "secid": QuoteID,
                    "dect": 1
                }
    response = send_request("GET", url,data=payload).get('data')
    x=round(response.get('f20')/response.get('f47'),2)
    if x>=n:
        log.info(f'排队和成交量比例大于{n}的股票')
        # print(response.get('f58'))
        return True
    else:
        return False



if __name__ == '__main__':
    def zt_pd_cjl():
        """
        涨停股票中，排队和当前成交量比值大于0.1的所有股票名称
        """
        codelist = []
        up_to_top_code1 = up_to_top_code(20241021)
        print(up_to_top_code)
        for code in up_to_top_code1:
            print(code)
            QuoteID = get_QuoteID(code)[0]
            name = get_QuoteID(code)[1]
            if pd_cjl(QuoteID, 0.1):
                codelist.append(name)
        print(codelist)


    #for code in tqdm(all_code,desc="当前进度",colour="green",unit="items"):

    def test():
        all_code=all_company_code()
        result=[]
        for code in all_code:
            try:
                today,yesterday=get_detail(code)
                #######  名字        收盘           开盘           涨跌幅         成交量            最高
                print(today[0])
                    # 价格大于8块
                if 70>=float(today[1])>=8:
                    print('价格大于8块')
                    #今天成交量大于昨天成交量
                    if int(today[4])>int(yesterday[4]):
                        print('今天成交量大于昨天成交量')
                        #昨天和今天是红的
                        if float(yesterday[1])>=float(yesterday[2]) and float(today[1])>float(today[2]):
                            print('昨天和今天是涨的')
                            #跳涨
                            if float(today[2])>float(yesterday[1]):
                                print('跳涨')
                                result.append(today[0])
            except:
                log.error(code)
        log.info(result)
        send_email(str(result))

    zt_pd_cjl()





