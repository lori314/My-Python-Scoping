# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class FirstbloodPipeline:
    def process_item(self, item, spider):
        #用来接收文件提交的持久化存储操作
        return item
