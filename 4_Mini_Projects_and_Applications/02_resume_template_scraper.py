import requests
from lxml import etree
import os
if __name__=="__main__":
    url='https://sc.chinaz.com/jianli/zhengtao.html'
    if not os.path.exists('./jianlimoban'):
        os.makedirs('./jianlimoban')
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"}
    page_text=requests.get(url=url,headers=headers).text
    tree=etree.HTML(page_text)
    a_list=tree.xpath('//div[@class="box col3 ws_block"]/a/@href')
    for a in a_list:
        response=requests.get(url=a,headers=headers)
        response.encoding=response.apparent_encoding
        a_text=response.text
        a_tree=etree.HTML(a_text)
        # print(a_text)
        # break
        link=a_tree.xpath('//ul[@class="clearfix"]/li[1]/a/@href')[0]
        title=a_tree.xpath('//div[@class="ppt_tit clearfix"]/h1/text()')[0]
        data=requests.get(url=link,headers=headers).content
        fileName=title+'.rar'
        filePath='./jianlimoban/'+fileName
        with open(filePath,'wb') as fp:
           fp.write(data)
        print(title+"下载成功!!")
