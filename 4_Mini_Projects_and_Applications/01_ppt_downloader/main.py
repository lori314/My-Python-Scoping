import requests
from lxml import etree

url='https://www.ypppt.com/moban/'

headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
    'Referer':'https://www.ypppt.com/',
    }
ppt_list=[]
main_html=requests.get(url=url,headers=headers)
main_html_text=main_html.text
main_html_tree=etree.HTML(main_html_text)
href_list=main_html_tree.xpath('//div[@class="wrapper"]/ul/li/a[1]/@href')

for href in href_list:
    url1='https://www.ypppt.com'+href
    detail_html=requests.get(url1,headers=headers)
    detail_html.encoding='utf-8'
    detail_html_text=detail_html.text
    detail_html_text_tree=etree.HTML(detail_html_text)
    next_href=detail_html_text_tree.xpath('/html/body/div[2]/div[2]/div/div[1]/div[2]/a/@href')
    name=detail_html_text_tree.xpath('/html/body/div[2]/div[2]/div/div[1]/h1/text()')
    url2='https://www.ypppt.com'+next_href[0]
    next_html_text=requests.get(url2,headers=headers).text
    next_html_tree=etree.HTML(next_html_text)
    download_link=next_html_tree.xpath('/html/body/div[1]/div/ul/li[1]/a/@href')
    ppt_list.append(name[0]+':'+download_link[0]+'\n')
    print(name[0]+':'+download_link[0])

with open('ppt.txt','w+',encoding='utf-8') as fp:
    for message in ppt_list:
        fp.write(message)
