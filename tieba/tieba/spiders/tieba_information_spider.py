# -*- coding: utf-8 -*-

'''
__author__='hzfengyufei'
这个用来爬会员的详细信息
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
from scrapy import Selector
import re
import time
import datetime
import json
import hashlib
from scrapy.http import Request
from tieba.items import TiebaItem
import traceback

class tieba_member_spider(scrapy.Spider):
    name='tieba_information_spider'
    allowed_domains = ["baidu.com"]

    def __init__(self,tieba_name=None):
        self.tieba_name=tieba_name

    def start_requests(self):
        '''
        只要用贴吧的主页面就行了
        :return:
        '''
        url='http://tieba.baidu.com/f?kw={}&ie=utf-8'.format(self.tieba_name)
        yield Request(url,callback=self.get_information)
        time.sleep(2)

    def get_information(self,response):
        '''
        抓取主要信息存入MySQL
        :param response:
        :return:
        '''
        try:
            item=TiebaItem()
            item['url']=response.url
            item['taskid']=hashlib.md5(response.url).hexdigest()
            item['updatetime']= float(time.mktime(time.strptime(time.ctime())))
            item['dt'] = '{}-{}-{}'.format(self.change(datetime.date.today().year), self.change(datetime.date.today().month), self.change(datetime.date.today().day))
            result = dict()
            result['url'] = response.url
            result['tieba_name'] = self.tieba_name + '吧'
            t = response.xpath('//code[@id="pagelet_html_frs-list/pagelet/thread_list"]').extract()[0]
            tt = t.replace('<!--', '').replace('-->', '')
            sel = Selector(text=tt)
            red_text_list=sel.xpath('//span[@class="red_text"]')
            #用户数
            result['amount'] = red_text_list[-1].xpath('text()').extract()[0]
            #发帖数
            result['papers'] = red_text_list[1].xpath('text()').extract()[0]
            ttt=response.xpath('//code[@id="pagelet_html_frs-header/pagelet/head"]').extract()[0]
            result['cata_type']=re.findall('(?<=fd=).+(?=&ie)',ttt)[0]
            result['tieba_type'] = re.findall('(?<=sd=).+(?=">)', ttt)[0]
            result=json.dumps(result).encode('hex')
            item['result']=result
            yield item
        except Exception, e:
            print traceback.print_exc()
            print e
            pass

    def change(self,item):
        item=str(item)
        if len(item)<2:
            item='0'+item
        return item





