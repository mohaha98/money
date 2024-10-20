"""=================不积跬步无以至千里==================
作    者： White
创建时间： 2023/7/14 16:43
文件名： test11
功能作用： 
=================不积小流无以成江海=================="""
import requests
import json

def send_webhook(data_dict):
    msg ="核销列表告警：\n"
    for agent in data_dict:
        msg=msg+f"{agent}变动列表：{data_dict.get(agent)}\n"
    url='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f1ec92f3-28b3-4144-a47a-27d632a4003d'


    headers = {'Content-Type': 'application/json'}
    payload = {'msgtype': 'text', 'text': {'content': msg,'mentioned_mobile_list':['15296869712',]}}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print("Webhook发送成功")
        else:
            print(f"Webhook发送失败，错误代码: {response.status_code}")
    except requests.RequestException as e:
        print(f"Request failed: {e}")
    return '111'
# data={'1111':[1,2,3]}
# send_webhook(data)
