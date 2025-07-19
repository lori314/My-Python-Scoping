import requests
from lxml import etree
from selenium import webdriver
import time

headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
}
file_out=open('file_in.txt','r')
url_list=file_out.readline().split(' ')
edge_options=webdriver.EdgeOptions()
edge_options.add_argument('--headless')
main_url='https://dl.pcgamestorrents.org/get-url.php'

bro=webdriver.Edge(options=edge_options)

for url in url_list:
    response=requests.get(url=url,headers=headers)
    text=response.text
    tree=etree.HTML(text)
    detail_url=tree.xpath('//p[@class="uk-card uk-card-body uk-card-default uk-card-hover"]/a/@href')[0]
    bro.get(url=detail_url)
    time.sleep(6)
    page_text=bro.page_source
    bro.quit()
    my_tree=etree.HTML(page_text)
    value=my_tree.xpath('//input[@id="url"]/@value')[0]
    params={
    'url':value,
    }
    response_text=requests.get(url=main_url,headers=headers,params=params).text
    i_tree=etree.HTML(response_text)
    magnet=i_tree.xpath('/html/body/input/@value')[0]
    print('################################')
    print(magnet)
    break