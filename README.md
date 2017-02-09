# scrapy_crawl_tieba
scrapy写成。
爬取贴吧的所有会员和所有发回帖人的关注贴吧和个人信息，还有贴吧的信息。
使用方法：
输入
scrapy crawl 爬虫名 -a tieba_name=***
贴吧名字不要加上‘吧’
爬虫有
tieba_member_detail_spider
tieba_fahuitiederen_detail_spider
tieba_member_followed_tieba_spider
tieba_fahuitiederen_detail_followed_tieba_spider
tieba_information_spider
