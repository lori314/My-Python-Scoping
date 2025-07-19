import requests
if __name__=="__main__":
    url='https://www.kfc.com.cn/kfccda/ashx/GetStoreList.ashx?op=keyword'
    keyword=input('enter a word:')
    param={
        'cname':'',
        'pid': '',
        'keyword': keyword,
        'pageIndex': '1',
        'pageSize': '10',
    }
    head={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",'Accept':'application/json'}
    response=requests.post(url=url,headers=head,params=param)
    text=response.text
    filename=keyword+'.txt'
    fp=open(filename,'w',encoding='utf-8')
    fp.write(text)

    print('over')