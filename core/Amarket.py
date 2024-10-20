"""=================不积跬步无以至千里==================
作    者： LEGION
创建时间： 2024/10/20 12:41
文件名： Amarket.py
功能作用： 
=================不积小流无以成江海=================="""

from tools.send_request import send_request
from tools.logger import log
from jsonpath import jsonpath
def all_company_code():
    """
    获取所有股票
    """

    url = "https://12.push2.eastmoney.com/api/qt/clist/get"

    payload = {'pn': '1',
               'pz': '20',
               "fid": 'f3',
               "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048",
               "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152"}
    response = send_request('get', url, data=payload)
    data = response.get('data').get('diff')
    print(data)


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


def get_detail():
    """
    股票详情 价格
    """
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    payload = {'fields1':"f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13",
               "fields2":"f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
               "beg":0,
              "end":'20500101',
               "secid":"1.688141",
              "klt":"101",
               "fqt":1}
    response = send_request("GET", url, data=payload)
    print(response)


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


def pd_cjl(QuoteID,m,n):
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
    if m>=x>=n:
        log.info(f'排队和成交量比例大于{n}的股票')
        # print(response.get('f58'))
        return True



if __name__ == '__main__':
    codelist=[]
    up_to_top_code=up_to_top_code(20241021)
    print(up_to_top_code)
    for code in up_to_top_code:
        QuoteID=get_QuoteID(code)[0]
        name=get_QuoteID(code)[1]
        if pd_cjl(QuoteID, 0.01,0.05):
            codelist.append(name)
    print(codelist)




