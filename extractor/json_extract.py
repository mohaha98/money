"""=================不积跬步无以至千里==================
作    者： White
创建时间： 2023/5/10 12:52
文件名： json_extract
功能作用： 
=================不积小流无以成江海=================="""
from tools.logger import log
import jsonpath
from extractor.yaml_loader import load_yaml

def jsonpath_extract(json_path:str):
    """
        获取json_dict相应字段的值
        :param json_dict: dict type: 字典对象
        :param json_path: str type: jsonpath表达式
        :return: field_value: 字典对象中的指定值
    """
    json_dict=load_yaml()
    if not isinstance(json_dict, dict):
        log.error('响应不是字典类型！！！！')
        raise TypeError
    # 在json_dict中查找匹配的值
    matches = jsonpath.jsonpath(json_dict,json_path)
    # 如果没有找到匹配的值，返回 None
    if len(matches) == 0:
        return None
    # 如果找到匹配的值，返回第一个匹配的值
    # 如果有多个匹配的值，也只返回第一个匹配的值
    return matches[0]

def get_target_value(json_data:dict, key, index:int):
    """
        获取json所有相应字段的值，取第index个
        :param json_data: dict type: 字典对象
        :param key: str type: key键
        :return: field_value: 字典对象中的指定值
    """
    if not isinstance(json_data, dict):
        log.error('响应不是字典类型！！！！')
        raise TypeError
    # JSONPath语法".."表示不管位置，选择符合条件的节点 "$"表示根节点
    #res = jsonpath.jsonpath(d,'$..name')
    expr = '$..{}'.format(key)
    field_value = jsonpath.jsonpath(obj=json_data, expr=expr)[int(index)]
    return field_value


if __name__=='__main__':
    name = jsonpath_extract('$.gbms2.headers.base.Content-Type')
    print(name)  # 输出：Alice
