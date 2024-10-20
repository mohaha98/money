# @Desc: 数据处理文件
from tools import config
import yaml
from tools.logger import log
import os

def load_yaml():
    filepath=os.path.join(config.BASE_DIR,'api_data.yaml')
    """
    读取指定YAML文件数据
    :param filepath:
    :return:
    """

    with open(filepath, encoding='utf-8') as file:
        try:
            stream = yaml.safe_load(file)
        except yaml.YAMLError as e:
            log.error('解析yaml失败！:[{}]'.format(filepath))
            raise e
    #log.info('解析yaml成功！:[{}]'.format(filepath))
    return stream


if __name__ == '__main__':
    filepath=os.path.join(config.BASE_DIR,'api_data.yaml')
    res=load_yaml(filepath)
    print(res)


