"""=================不积跬步无以至千里==================
作    者： White
创建时间： 2023/5/10 12:51
文件名： re_extract
功能作用： 
=================不积小流无以成江海=================="""
import re
def extract_string(string, pattern):
    match = re.findall(pattern, string)
    return match



if __name__=='__main__':
    text='n12345344n545345k53453n5345'
    pattern=r'n\d{4}'
    print(extract_string(text,pattern))