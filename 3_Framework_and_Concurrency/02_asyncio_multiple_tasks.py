import asyncio
import time

async def request(url):
    print('正在下载',url)
    await asyncio.sleep(2)
    print('下载完毕',url)

start= time.time()
urls=[
    'www.baidu.com',
    'www.sougou.com',
    'www.goubanjia.com'
]

#任务列表:存放多个任务对象
stasks=[]
for url in urls:
    c= request(url)
    task=asyncio.ensure_future(c)
    stasks.append(task)

loop =asyncio.get_event_loop()
#将任务列表封装到wait中
loop.run_until_complete(asyncio.wait(stasks))

print(time.time()-start)