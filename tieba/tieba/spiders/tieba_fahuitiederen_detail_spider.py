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
    name='tieba_fahuitiederen_detail_spider'
    allowed_domains = ["baidu.com"]

    def __init__(self,tieba_name=None):
        self.tieba_name=tieba_name


    def start_requests(self):
        '''
        获得贴吧页面
        :return:
        '''
        url='http://tieba.baidu.com/f?kw={}&ie=utf-8'.format(self.tieba_name)
        yield Request(url,callback=self.get_member_page_number)
        time.sleep(2)

    def get_member_page_number(self, response):
        '''
        获得贴吧帖子的页数
        :param response:
        :return:
        '''
        t=response.xpath('//code[@id="pagelet_html_frs-list/pagelet/thread_list"]').extract()[0]
        tt=t.replace('<!--','').replace('-->','')
        sel=Selector(text=tt)
        try:
            last_page=int(re.findall('(?<=pn=)\d+',sel.xpath('//div[@id="frs_list_pager"]/a[last()]').extract()[0])[0])
        except:
            last_page=50
        for i in range(0,last_page+50,50):
            url='http://tieba.baidu.com/f?kw={}&ie=utf-8&pn={}'.format(self.tieba_name,i)
            yield Request(url,callback=self.get_each_page)


    def get_each_page(self,response):
        '''
        找每一页的每一个帖
        :param response:
        :return:
        '''
        t = response.xpath('//code[@id="pagelet_html_frs-list/pagelet/thread_list"]').extract()[0]
        tiezi_list=re.findall('/p/\d+',t)
        for i in tiezi_list:
            url='http://tieba.baidu.com'+i
            yield Request(url, callback=self.get_each_tie_page)


    def get_each_tie_page(self,response):
        '''
        找每个帖的页数
        :param response:
        :return:
        '''
        try:
            t=response.xpath('//a[@text()="尾页"]/@href')
        except:
            t=None
        if t:
            last_page=int(re.findall('(?<=pn=)\d+',t)[0])
        else:
            last_page=1
        for i in range(1,last_page+1):
            url=response.url+'?pn='+str(i)
            yield Request(url, callback=self.get_each_tiepage_member)


    def get_each_tiepage_member(self, response):
        '''
        得到每个帖子每一页的用户的用户名
        :param response:
        :return:
        '''
        member_list=response.xpath('//a[@data-field and contains(@class,"p_author_name")]/text()')
        for i,j in enumerate(member_list):
            member_list[i]=j.extract().decode('utf-8')
        for i in member_list:
            url='http://www.baidu.com/p/{}/detail&ie=utf-8'.format(i)
            yield Request(url, callback=self.get_member_detail, meta={'user_name': i,'url':url})

    def get_member_detail(self,response):
        '''
        存入mysql
        :param response:
        :return:
        '''
        try:
            dic_user=dict()
            dic_user['user_name']=response.meta['user_name']
            dic_user_detail=dict()
            l=response.xpath('//dd')
            for i in l:
                if i.xpath('span[1]/@class').extract() and i.xpath('span[1]/@class').extract()[0]=='profile-corp-name':
                    key='公司:'+re.findall('(?<=/span>).+(?=</span)',i.xpath('span[1]').extract()[0])[0]
                    value = i.xpath('span[last()]/text()').extract()
                    if value:
                        value=value[0]
                    else:
                        value=''
                else:
                    key=i.xpath('span[1]/text()').extract()
                    if key:
                        key=key[0]
                    else:
                        key=''
                    value=i.xpath('span[2]/text()').extract()
                    if value:
                        value=value[0]
                    else:
                        value=''
                dic_user_detail[key]=value
            dic_user['user_detail']=dic_user_detail
            result=json.dumps(dic_user).encode('hex')
            url=response.url
            taskid=hashlib.md5(url).hexdigest()
            updatetime=float(time.mktime(time.strptime(time.ctime())))
            dt = '{}-{}-{}'.format(self.change(datetime.date.today().year), self.change(datetime.date.today().month), self.change(datetime.date.today().day))
            item=TiebaItem()
            item['taskid']=taskid
            item['url'] = url
            item['result'] = result
            item['updatetime'] = updatetime
            item['dt'] = dt
            yield item
        except:
            print traceback.print_exc()
            print dic_user['user_name']
            pass

    def change(self,item):
        item=str(item)
        if len(item)<2:
            item='0'+item
        return item






