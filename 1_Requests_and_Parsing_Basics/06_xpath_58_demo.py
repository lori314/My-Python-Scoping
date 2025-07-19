#xpath 解析：最常用，通用性强，工作时首选
# 1.实例化一个叫做etree的对象，将待解析的页面源码数据加载到该对象中
# 2.调用etree对象终点xpath方法结合着xpath表达式实现标签定位与内容捕获

#实例化etree：1.将本地html文档中的源码数据加载到etree对象中：etree.parse(filePath)
#从互联网上获取：etree.HTML('page_text')
#xpath('xpath表达式')
#xpath表达式：/：分隔层级  //：中间有多个层级（可以从任意位置开始定位）  @：属性选择器，/@取属性
#tree.xpath('/html/head/title')[/表示从根节点开始定位]：返回element类型对象，储存title的文本内容,多个结果会返回多个
#tree.xpath('/html//div')：表示中间有多个层级
#tree.xpaht('//div[@class='song']'):找到所有的class为song的div
#tree.xpath('//div[@class="song"]/p[3]'):索引定位（从1开始索引）
#tree.xpath('//div[@class='tang'])/p[3]/a/text()')返回text
#//text返回整个文本内容  
import requests
from lxml import etree
if __name__=="__main__":
    url="https://bj.58.com/ershoufang/"
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"}
    page_text=requests.get(url=url,headers=headers).text
    #print(page_text)

    tree = etree.HTML(page_text)
    li_list=tree.xpath('//div[@class="property-content"]')
    print(li_list)
    fp=open('58.txt','w',encoding='utf-8')
    for li in li_list:
        title=li.xpath('./div/div/h3/text()')[0]
        print(title)
        fp.write(title+'\n')
