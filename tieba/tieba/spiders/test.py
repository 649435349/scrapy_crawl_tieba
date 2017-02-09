# -*- coding: utf-8 -*-

'''
__author__='hzfengyufei'
这个用来爬会员的详细信息
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
import re
import time
import datetime
import json
import hashlib
from scrapy.http import Request
from tieba.items import TiebaItem
import traceback

class tieba_member_spider(scrapy.Spider):
    name='test'
    allowed_domains = ["baidu.com"]

    def __init__(self,tieba_name=None):
        '''
        输入贴吧的名字
        :param tieba_name:
        '''
        self.tieba_name=tieba_name

    def start_requests(self):
        '''
        从会员的页面开始
        :return:
        '''
        url='http://tieba.baidu.com/bawu2/platform/listMemberInfo?word={}&ie=utf-8'.format(self.tieba_name)
        yield Request(url, callback=self.get_member_page)

    def get_member_page_number(self,response):
        '''
        获得会员页面的页数，如果没有则为1
        :param response:
        :return:
        '''
        span=response.xpath('//span[@class="tbui_total_page"]')
        try:
            page_number=int(re.findall(r'共(\d+)页'.decode('utf-8'),span.extract()[0].decode('utf-8'))[0])
        except:
            page_number=1
        for i in range(1,page_number+1):
            url='http://tieba.baidu.com/bawu2/platform/listMemberInfo?word={}&pn={}&ie=utf-8'.format(self.tieba_name,i)
            yield Request(url, callback=self.get_member_page)



    def get_member_page(self,response):
        '''
        进入每一页每个会员的信息界面
        :param response:
        :return:
        '''
        member_list=response.xpath('//a[@class="user_name"]/text()')
        for i,j in enumerate(member_list):
            member_list[i]=j.extract().decode('utf-8')
        for i in member_list:
            #个人信息的页面
            url='http://www.baidu.com/p/{}/detail&ie=utf-8'.format(6089518)#i.decode('utf-8')
            yield Request(url, callback=self.get_member_detail,meta={'user_name':i})
            break


    def get_member_detail(self,response):
        '''
        获取信息存入Mysql
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
                    key=i.xpath('span[1]/text()').extract()[0]
                    value=i.xpath('span[2]/text()').extract()[0]
                print key,value
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





