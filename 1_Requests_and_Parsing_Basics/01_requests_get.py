import requests

if __name__=="__main__":
    #step:url
    url='https://www.sogou.com/'
    response=requests.get(url)
    #get information
    page_text=response.text
    print(page_text)
    with open('./sougou.txt','w',encoding='utf-8') as fp:
        fp.write(page_text)
print('finished！')
