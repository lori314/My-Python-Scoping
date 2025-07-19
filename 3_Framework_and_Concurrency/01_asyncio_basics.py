import asyncio

async def request(url):
    print('正在请求',url)
    print('finished')
    return url
#调用后返回一个协程对象

c=request('www.baidu.com')

#创建一个事件循环对象：
loop= asyncio.get_event_loop()

#将协程对象注册到loop中,并启动loop
#loop.run_until_complete(c)

#task的使用
#task=loop.create_task(c)
#基于loop创建了一个task
#print(task)

#future 的使用
# task=asyncio.ensure_future(c)
# print(task)
# loop.run_until_complete(task)
# print(task)

def callback_func(task):
    print(task.result())
    #result 返回的是原函数的返回值
#绑定回调
task=asyncio.ensure_future(c)
#绑定
task.add_done_callback(callback_func)
loop.run_until_complete(task)

#aiohttp:基于异步的网络请求发送的模块
#import aiohttp
#async with aiohttp.ClientSession() as session:
#   async with session.get(url) as response:
#       page_text=response.text() #返回字符串形式的响应数据//read()返回二进制形式的响应数据//json()返回json类型的响应数据
# post()发起POST请求
# headers,params/data依然成立,proxy='hrrp://ip:port'(代理ip)



