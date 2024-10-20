# 配置文件
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')


if __name__ == '__main__':
    print(DATA_DIR)
