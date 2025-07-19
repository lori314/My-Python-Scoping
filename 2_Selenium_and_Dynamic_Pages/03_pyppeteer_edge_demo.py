import asyncio
from pyppeteer import launch

async def browse_website_with_edge(url):
    # 注意：executablePath 需要指向 Edge 的可执行文件
    edge_executable_path = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" # <-- 替换为你的 Edge 实际路径

    try:
        # 启动 Edge 浏览器实例
        browser = await launch(executablePath=edge_executable_path, headless=False, devtools=True)
        page = await browser.newPage()

        print(f"正在使用 Edge 打开页面: {url}")
        await page.goto(url, {'waitUntil': 'networkidle0'})
        print("页面加载完成")

        # ... 后续操作代码 ...

        # await asyncio.sleep(60)
        # await browser.close()

    except Exception as e:
        print(f"启动 Edge 失败或发生错误: {e}")

if __name__ == "__main__":
    website_url = "https://jx.oxah.cn/user/parse"
    asyncio.get_event_loop().run_until_complete(browse_website_with_edge(website_url))