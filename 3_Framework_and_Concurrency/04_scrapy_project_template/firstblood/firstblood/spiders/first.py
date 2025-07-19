import scrapy


class FirstSpider(scrapy.Spider):
    name = "first"
    allowed_domains = ["www.xxx.com"]
    #允许的域名(限定start_urls中那些域名可以进行发送请求，通常注释掉)
    start_urls = ["https://www.baidu.com",'https://www.sogou.com']
    #起始的url列表(该列表中存放的url会被scripy自动进行请求的发送)

    #用作于数据解析，response表示的是响应对象，parse的调用次数即为start_urls中元素个数
    def parse(self, response):
        print(response)
