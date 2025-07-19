import requests
import json
if __name__=="__main__":
    url='https://movie.douban.com/j/chart/top_list'
    param={
        'interval_id':'100:90',
        'action':'',
        'type':'5',
        'start':'20',
        'limit':'20',
    }
    head={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",'Accept':'application/json'}
    response=requests.get(url=url,params=param,headers=head)
    print(response.status_code)
    list_data=response.json()

    fp = open('./douban.json','w',encoding='utf-8')
    json.dump(list_data,fp=fp,ensure_ascii=False)

    print('over')
