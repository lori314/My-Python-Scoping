import requests
import json
if __name__=="__main__":
    post_url='https://fanyi.baidu.com/sug'
    word=input("enter a word:")
    data={
        'kw':word
    }
    head={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"}
    response=requests.post(url=post_url,data=data,headers=head)
    #确认服务器响应数据为json类型
    dic_obj=response.json()
    fileName=word+'.json'
    fp=open(fileName,'w',encoding='utf-8')
    json.dump(dic_obj,fp=fp,ensure_ascii=False)
    #有中文ascii为false

    print('over!')

    