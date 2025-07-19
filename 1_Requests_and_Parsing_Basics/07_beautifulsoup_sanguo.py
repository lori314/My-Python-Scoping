from bs4 import BeautifulSoup
import requests
if __name__=="__main__":
    #将本地数据导入的方法
    #soup=Beatifulsoup('','lxml')
    # BeatifulSoup提供的方法和属性：
    # soup.tagName(可以任选标签{a,p,span等})：返回html中第一次出现的tagName标签
    # soup.find('tagName'):相当于soup.tagName
    # soup.find('tagName',class_/id/attr='className'):属性定位
    # soup.find_all('tagName',):找到所有符合条件的，返回列表
    # soup.select('类/id选择器写法'):返回符合要求的列表
    # soup.select('最外层标签>中层标签>里标签>...'):层级选择器
    # soup.select('最外层 里标签...):空格表示多个层级
    # soup.a.text/string/get_text()：对soup对象的处理方法，text/get_text:获取标签下的所有文本内容  string:只获取直系文本内容
    # soup.a['href']:获取属性值
    url='https://www.shicimingju.com/book/sanguoyanyi.html'
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"}
    response=requests.get(url=url,headers=headers)
    response.encoding='utf-8'
    page_text=response.text

    soup=BeautifulSoup(page_text,'lxml')
    li_list=soup.select('.book-mulu > ul > li')
    fp = open('./sanguoyanyi.text','w',encoding="utf-8")
    for li in li_list:
        title=li.a.string
        detail_url='https://www.shicimingju.com'+li.a['href']
        detail_url_response=requests.get(url=detail_url,headers=headers)
        detail_url_response.encoding='utf-8'
        detail_url_text=detail_url_response.text
        detail_soup=BeautifulSoup(detail_url_text,'lxml')
        div_tag=detail_soup.find('div',class_='chapter_content')
        content=div_tag.text
        fp.write(title+':'+content+'\n')
        print(title+'爬取成功!!')
        

