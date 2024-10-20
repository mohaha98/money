"""=================不积跬步无以至千里==================
作    者： White
创建时间： 2023/5/10 10:12
文件名： connect_sql
功能作用：
=================不积小流无以成江海=================="""

import pymysql
from tools.logger import log

def execute_mysql(sql):
    # 连接数据库
    conn = pymysql.connect(
        host='192.168.26.237',
        user='appuser',
        password='Xgt@666888',
        db='unionbank',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        # 执行 SQL 查询
        with conn.cursor() as cursor:
            log.info(f'----{sql}')
            cursor.execute(sql)
            result = cursor.fetchall()
        conn.commit()
    except:
        log.error('执行sql错误')
    finally:
        # 关闭数据库连接
        conn.close()

    return result


import cx_Oracle

def execute_oracle(sql):
    """
    连接Oracle数据库，执行SQL语句，并返回查询结果
    user: 用户名
    password: 密码
    dsn: 数据库地址、端口号和实例名
    sql: 要执行的SQL语句
    """
    try:
        # 连接Oracle数据库
        connection = cx_Oracle.connect(
            user='dragonpass',
            password='xgt666888',
            #dsn=cx_Oracle.makedsn('192.168.26.246', '1521', 'dragon'),
            dsn='192.168.26.246:1521/dragon'
        )
        # 创建游标
        cursor = connection.cursor()
        print('连接数据库成功！')
        # 执行SQL语句
        cursor.execute(sql)
        # 提交事务
        connection.commit()
        # 获取查询结果
        result = cursor.fetchall()
        # 关闭游标和连接
        cursor.close()
        connection.close()
        # 返回查询结果
        return result
    except cx_Oracle.Error as error:
        print(error)

if __name__=="__main__":
    # sql = "SELECT * FROM usr_card where id='1650462018286587906';"
    # result = execute_mysql(sql)
    # print(result)
    sql = 'SELECT * FROM DRAGONPASS.TBLGUARANTEEBOOK;'
    result = execute_oracle(sql)
    print(result)
