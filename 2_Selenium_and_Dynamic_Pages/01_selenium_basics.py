#selenium模块
#便捷获取动态加载的信息
#便捷实现模拟登录

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains #导入动作链
import time
from selenium.webdriver.edge.options import Options
from selenium.webdriver import EdgeOptions
bro=webdriver.Edge()
bro.get('https://www.taobao.com')

#获取浏览器当前页面的源码数据
page_text=bro.page_source
#标签定位
search_input=bro.find_element(By.ID,'q')
#标签交互
search_input.send_keys('Iphone') #录入词条
search_button=bro.find_element(By.CSS_SELECTOR,'.btn-search')

#点击搜索按钮
search_button.click()
time.sleep(5)
#bro.back()
#bro.forward() 前进和后退
#bro.execute_script('jsCode') 执行js代码

bro.quit() #退出




#如果待定位的标签在iframe标签下
#bro.switch_to.frame('')#填入iframe的id
#然后正常定位即可

action=ActionChains(bro)

action.click_and_hold()

for i in range(5):
    #采用perform(立即执行动作连操作)
    action.move_by_offset(17,0).perform()
    time.sleep(0.3)
    #offset传入位移的向量坐标

#实现无头浏览器
edge_options=Options()
edge_options.add_argument('--headless')
edge_options.add_argument('--disable-gpu')

#规避检测
option=EdgeOptions()
option.add_experimental_option('excludeSwitches',['enable-automation'])

bro=webdriver.Edge(edge_options=edge_options)






