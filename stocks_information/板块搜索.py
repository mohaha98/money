"""=================不积跬步无以至千里==================
作    者： LEGION
创建时间： 2025/8/10 17:01
文件名： 板块搜索.py
功能作用： 
=================不积小流无以成江海=================="""
import tushare as ts
from datetime import datetime, timedelta
from tools.logger import log
from tools.send_request import send_request

pro = ts.pro_api()
def get_bkid(key):
    """通过名字模糊查询板块id"""
    """通过id查询板块名字"""
    """type=2是板块  3是概念"""

    url = "https://push2.eastmoney.com/api/qt/clist/get"
    payload = {'np':1,
               "fltt":1,
               "invt": 2,
               # "cb": 'jQuery37100979687889627896_1754804094712',
               "fs":f'm:90+t:2+f:!50',
               "fields": "f12,f13,f14,f1,f2,f4,f3,f152,f20,f8,f104,f105,f128,f140,f141,f207,f208,f209,f136,f222",
               "fid": 'f3',
               'pn':1,
               'po':1,
               'pz':100,
               'ut':'fa5fd1943c7b386f172d6893dbfba10b',
               'wbp2u':'|0|0|0|web'}
    haed={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
          'referer':'https://quote.eastmoney.com/center/gridlist.html'}
    try:
        response1 = send_request("GET", url, data=payload,headers=haed).get('data').get('diff')
        response2=[]
        for i in range(5):
            payload.update({"fs":f'm:90+t:3+f:!50','pn':i+1})
            response2 = send_request("GET", url, data=payload, headers=haed).get('data').get('diff')+response2
        result={}
        response=response1+response2
        if not any(char.isdigit() for char in key):
            #入参是名字
            for item in response:
                if key in item['f14']:
                    result.update({item['f14']:item['f12']})
            print(result)
            chose_id=input("请选择：")
            rqlt_dc(chose_id)
        else:
            # 入参是板块id
            for item in response:
                if key in item['f12']:
                    # print(item['f14'])
                    return item['f14']
    except:
        return None

def rqlt_dc(code):
    """
板块人气龙头
输入东方财富板块编码 BK开头
    """
    try:
        url = "https://datacenter.eastmoney.com/securities/api/data/get"
        url2='https://push2.eastmoney.com/api/qt/clist/get'
        payload = {'type':"RTP_F10_POPULAR_LEADING",
                   "sty":"SECUCODE,SECURITY_NAME_ABBR",
                   "extraCols": 'f2~01~SECURITY_CODE~NEWEST_PRICE,f3~01~SECURITY_CODE~YIELD',
                   "params": f"{code.replace('K','I')}",
                   "source": "HSF10",
                   'client':'PC'}
        payload2={'np':1,
                   "fltt":2,
                   "invt": 2,
                   # "cb": 'jQuery37100979687889627896_1754804094712',
                   "fields": "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13",
                   "fid": 'f62',
                   'pn':1,
                   'po':1,
                   'pz':10,
                   'ut':'fa5fd1943c7b386f172d6893dbfba10b',
                   'wbp2u':'|0|0|0|web',
                  'fs':f'b:{code}'}
        haed={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'}
        response = send_request("GET", url, data=payload,headers=haed).get('result')
        response2 = send_request("GET", url2, data=payload2, headers=haed).get('data').get('diff')
        # print(response2)
        print(f'----------------<{get_bkid(code)}>人气龙头--------------')
        for item in response:
            print(f"{item['SECURITY_NAME_ABBR']}--涨幅：{item['YIELD']}%")
        print(f'----------------<{get_bkid(code)}>个股资金流入排行--------------')
        for item in response2:
            print(f"{item['f14']}--流入：{round(item['f62']/1e8, 2)}亿")
    except:
        return None


if __name__ == '__main__':
    pass
    get_bkid('量子')

