# @Desc: HTTP请求
import requests
import time
from tools.logger import log


class HttpRequest(object):
    def __init__(self):
        self.session = requests.session()
    def send_request(self, method, url, name=None, **kwargs):
        method = method.upper()
        log.info("接口名称: {name}".format(name=name))
        log.info(f"> 请求方法：{method}  请求地址：{url}".format(method=method, url=url))
        log.info("> 参数kwargs: {kwargs}".format(kwargs=kwargs))
        kwargs.setdefault('timeout', 10)
        ##时间戳
        start_timestamp = time.time()
        # 发起HTTP请求，获得HTTP响应信息
        response = self.session.request(method, url, **kwargs)

        response_time = round((time.time() - start_timestamp) * 1000, 2)
        try:
            response.raise_for_status()
            log.info('> 响应: {}'.format(response.json()))
        except requests.RequestException as e:
            raise e
        else:
            log.info('状态码: {} , '
                     '响应时间: {}ms'.format(response.status_code, response_time))

        return response


if __name__ == '__main__':
    urls = 'http://47.112.0.183:8801/base/user/v2/login'
    headers = {
        "content-type": "application/json;charset=UTF-8",
    }
    methods = 'POST'
    data = {
    "password": "000000",
    "appType": "1",
    "mobile": "13367587442",
    "type": "1",
    "device": {
        "deviceType": "1",
        "deviceTagApp": "c2:54:7c:86:4f:35",
        "oaid": "86adb349-f06b-4097-857f-a87934e1abbe"
    }
        }
    data = {'headers':headers,
             'json':data}
    res = HttpRequest().send_request(methods, urls, **data)
    assert res.json()['code'] == 200
    assert res.json()['msg'] == "操作成功"
