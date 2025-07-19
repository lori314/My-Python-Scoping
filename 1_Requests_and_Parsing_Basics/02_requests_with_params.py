import requests
#UA伪装：门户网站的服务器会检测对应载体的身份表示，若检测到其为某一款浏览器，则判定为正常请求；若不是浏览器，则有可能会拒绝
#User-Agent 
if __name__=="__main__":
    url = 'https://www.sogou.com/web?'
    #处理url携带的参数：封装到字典中
    kw = input('enter a word:')
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"}
    param={
        'query':kw
    }
    response=requests.get(url=url,params=param,headers=headers)

    page_text=response.text
    fileName=kw+'.html'
    with open(fileName,'w',encoding='utf-8') as fp:
        fp.write(page_text)
    print(fileName,'已保存')    