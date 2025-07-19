import requests
from lxml import etree
headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
}
url='https://dl.pcgamestorrents.org/get-url.php'
html='https://pcgamestorrents.com/games-list-pc-616134483-torrent-download-free.html'
response=requests.get(url=html,headers=headers)
response_text=response.text
tree=etree.HTML(response_text)
ul_list=tree.xpath('//div[@class="uk-margin-medium-top"]/ul')
with open('file_2.txt','w+') as fp:
    for ul in ul_list:
        li_list=ul.xpath('./li')
        for li in li_list:
            detail_url=li.xpath('./a/@href')[0]
            fp.write(detail_url)
            fp.write(' ')
