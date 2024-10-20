import pymysql


def execute_sql(sql):
    # 定义变量db，使用pymysql连接数据库
    db = pymysql.connect(host="192.168.241.13",user="gjdev",password="12345678",db="user",port=3306)
    # 定义变量cr，获取游标
    cr = db.cursor()

    try:
        # 执行sql语句
        cr.execute(sql)

    except Exception as e:
        raise e
    req=cr.fetchone()
    # 关闭数据库连接
    db.close()
    # 关闭游标
    cr.close()
    return req
