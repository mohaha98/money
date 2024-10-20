import jwt
import datetime
import time
import base64




SECRET_KEY ='iqbvqc9a3r9BV2ptc0PSRoZPZiMvlCqW'
def encode_jwt(payload, secret=SECRET_KEY, algorithm='HS256'):
    """
    使用指定的密钥和算法对给定的payload进行JWT加密。

    参数：
    - payload: dict，负载数据
    - secret: str，密钥
    - algorithm: str，加密算法，默认使用HS256

    返回：
    - str，加密后的JWT字符串
    """
    # 添加过期时间（可选）
    # # 获取当前本地时间
    # current_time = datetime.datetime.now()
    # # 当前时间加上一年
    # new_time = current_time + datetime.timedelta(days=365)
    # # 将新的时间转换为时间戳
    # timestamp = int(time.mktime(new_time.timetuple()))
    payload['exp'] = 1749807248
    print(payload)
    token = jwt.encode(payload, secret, algorithm=algorithm)
    return token

#
# def decode_jwt(token, secret=SECRET_KEY, algorithms=['HS256']):
#     """
#     使用指定的密钥和算法对给定的JWT进行解密。
#
#     参数：
#     - token: str，加密的JWT字符串
#     - secret: str，密钥
#     - algorithms: list，解密算法列表
#
#     返回：
#     - dict，解密后的负载数据
#     """
#     try:
#         decoded_payload = jwt.decode(token, secret, algorithms=algorithms)
#         return decoded_payload
#     except jwt.ExpiredSignatureError:
#         return 'Token has expired'
#     except jwt.InvalidTokenError:
#         return 'Invalid token'


# 示例使用
if __name__ == '__main__':

    payload = {'iss': 'Su9DOFNj5wyEYbxjGWvJIKIVb5dfa7Gm'}
    token = encode_jwt(payload)
    print(token)

