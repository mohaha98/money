"""=================不积跬步无以至千里==================
作    者： White
创建时间： 2023/5/10 13:47
文件名： html_parser
功能作用： 
=================不积小流无以成江海=================="""
from bs4 import BeautifulSoup
import requests

class HtmlParser:
    def __init__(self, url):
        self.url = url

    def parse(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                html = response.content
                soup = BeautifulSoup(html, 'html.parser')
                # 获取页面标题
                title = soup.title.string
                # 获取页面中的所有链接
                links = [link.get('href') for link in soup.find_all('a')]
                # 获取页面中的所有段落
                paragraphs = [p.text for p in soup.find_all('p')]
                # 返回解析结果
                return {
                    'title': title,
                    'links': links,
                    'paragraphs': paragraphs
                }
            else:
                return None
        except Exception as e:
            print(e)
            return None

if __name__=='__main__':
    parser = HtmlParser('http://example.com')
    result = parser.parse()
    if result:
        print('页面标题：', result['title'])
        print('页面链接：', result['links'])
        print('页面段落：', result['paragraphs'])
    else:
        print('无法获取页面数据。')
