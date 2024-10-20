"""=================不积跬步无以至千里==================
作    者： 莫景怀
创建时间： 2023/5/9 23:07
文件名： send_request.py
功能作用：
=================不积小流无以成江海=================="""
import requests
import time
from tools.logger import log
from requests.exceptions import Timeout

def send_request(method, url, headers=None, data=None, name=None,timeout=10):
    """
    发送HTTP请求并返回响应信息
    :param method: 请求方法
    :param url: 请求URL
    :param headers: 请求头
    :param name: 接口名称
    :param data: 请求数据
    :return: 响应信息
    """
    retries=3  ##超时重跑次数
    response = None
    method = method.upper()
    for i in range(retries):
        start_time = time.time()  # 记录请求时间
        try:
            if method == 'GET':
                response = requests.get(url, params=data,headers=headers,timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data,timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data,timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers,timeout=timeout)
            else:
                log.error(f"不合法请求：{method}")
                raise ValueError(f"不合法请求: {method}")

            if response.status_code == 200:
                return response.json()
            else:
                log.error(f"{url} error status_code {response.status_code}")
            # print(response)
            break

        except Timeout:
            log.error(f"url:{url}")
            log.error(f"请求超时，正在进行第 {i + 1}/{retries} 次重试...")
            continue
        except Exception as e:
            # raise e
            log.error(f"url:{url}--请求发生异常：{e}")
            log.error(f'body:{data}')
            log.error(f'response:{response}')
            break

        finally:
            end_time = time.time()
            #log.info(f"耗时： {end_time - start_time:.3f} seconds")
    return None


if __name__ == '__main__':
    method = 'post'
    url = 'https://investec-uat.dragonpass.com.cn/investec/lounge/trafficSites'
    headers = {'Content-Type': 'application/json',
               'signaturerequired':'false'}

    body = {}
    response = send_request('post', url, headers, body)
    print(response)
