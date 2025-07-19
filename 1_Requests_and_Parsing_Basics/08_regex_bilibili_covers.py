import requests
import re
import os
if __name__=="__main__":
    if not os.path.exists('./fengmian'):
        os.makedirs('./fengmian')
    ex='<img src="(.*?)" alt.*?>'
    url='https://www.bilibili.com/'
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"}
    page_text=requests.get(url=url,headers=headers).text
    src_list=re.findall(ex,page_text,re.S)
    #print(src_list)
    for src in src_list:
        src='https:'+src
        img=requests.get(url=src,headers=headers).content
        file_name=src.split('/')[-1]+'.jpg'
        file_path='./fengmian/'+file_name
        with open(file_path,'wb') as fp:
            fp.write(img)
        print('{}下载成功'.format(file_name))