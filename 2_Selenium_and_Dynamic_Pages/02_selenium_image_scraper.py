from selenium import webdriver
from selenium.webdriver.common.by import By
from lxml import etree
import requests
import time

headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"}
url='https://cn.bing.com/images/search?view=detailV2&ccid=oMwJA9i%2f&id=994981DE5C4D1EB6F392000EF5B3C491CCB3B95C&thid=OIP.oMwJA9i_M1kEQSn0ceciogHaJ4&mediaurl=https%3a%2f%2fpic3.zhimg.com%2fv2-14ce9bc8343aebc7b1938af640839c4e_r.jpg&exph=1600&expw=1200&q=%e6%b4%9b%e5%a4%a9%e4%be%9d%e5%9b%be%e7%89%87&simid=607998568975110444&FORM=IRPRST&ck=A2B7A0ABFF529CCB5EE68402DEEDD660&selectedIndex=0&itb=1&qpvt=%e6%b4%9b%e5%a4%a9%e4%be%9d%e5%9b%be%e7%89%87&ajaxhist=0&ajaxserp=0'
bro=webdriver.Edge()
bro.get(url=url)

for n in range(1,51):
    page_text=bro.page_source
    tree=etree.HTML(page_text)
    img_src=tree.xpath('//*[@id="mainImageWindow"]/div[1]/div/div/div/img/@src')[0]
    img_data=requests.get(url=img_src,headers=headers).content
    fileName='天依'+str(n)+'.jpg'
    filePath='./luotianyi/'+fileName
    with open(filePath,'wb') as fp:
        fp.write(img_data)
    print(fileName+'下载完成！！')
    span=bro.find_element(By.XPATH,'//*[@id="navr"]/span')
    span.click()

bro.quit()

