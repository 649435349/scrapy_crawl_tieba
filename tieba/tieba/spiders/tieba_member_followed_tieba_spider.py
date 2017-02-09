# -*- coding: utf-8 -*-

'''
__author__='hzfengyufei'
这个用来爬会员的关注贴吧
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
import re
import time
import datetime
import json
import traceback
import hashlib
from scrapy.http import Request
from tieba.items import TiebaItem

class delete_error(Exception):
    '''
    用户名可能注销的错误
    '''
    pass

class tieba_member_spider(scrapy.Spider):
    name='tieba_member_followed_tieba_spider'
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
        yield Request(url, callback=self.get_member_page_number)

    def get_member_page_number(self,response):
        '''
        获得会员页面的页数，如果没有则为1
        :return:
        '''
        span = response.xpath('//span[@class="tbui_total_page"]')
        try:
            page_number = int(re.findall(r'共(\d+)页'.decode('utf-8'), span.extract()[0].decode('utf-8'))[0])
        except:
            page_number = 1
        for i in range(1, page_number + 1):
            url = 'http://tieba.baidu.com/bawu2/platform/listMemberInfo?word={}&pn={}&ie=utf-8'.format(self.tieba_name,
                                                                                                       i)
            yield Request(url, callback=self.get_member_page)

    def get_member_page(self,response):
        '''
        进入每一页每个会员的关注贴吧界面
        :param response:
        :return:
        '''
        member_list=response.xpath('//a[@class="user_name"]/text()')
        for i,j in enumerate(member_list):
            member_list[i]=j.extract().decode('utf-8')
        for i in member_list:
            #关注贴吧的页面
            url='https://www.baidu.com/p/{}?from=tieba&ie=utf-8'.format(i.decode('utf-8'))
            yield Request(url, callback=self.get_member_followed_tieba,meta={'user_name':i,'url':url})
            time.sleep(2)


    def get_member_followed_tieba(self,response):
        '''
        获取信息存入Mysql
        :param response:
        :return:
        '''
        try:
            if 'error' in response.url:
                raise delete_error
            dic_user=dict()
            dic_user['user_name']=response.meta['user_name']
            s=response.xpath('//body/script[9]').extract()[0].decode('utf8')#TMD在js脚本里面我真是日了狗
            l=re.findall(r'(?<=title=)(.{1,30})(?=>)'.decode('utf8'),s)#这个条件很弱，希望能重写。
            dic_user['followed_tieba']=l
            result=json.dumps(dic_user).encode('hex')
            url=response.url
            taskid=hashlib.md5(url).hexdigest()
            updatetime=float(time.mktime(time.strptime(time.ctime())))
            dt = '{}-{}-{}'.format(self.change(datetime.date.today().year), self.change(datetime.date.today().month),
                                   self.change(datetime.date.today().day))
            item=TiebaItem()
            item['taskid']=taskid
            item['url'] = url
            item['result'] = result
            item['updatetime'] = updatetime
            item['dt'] = dt
            yield item
        except delete_error:
            print response.meta['user_name']+'此人可能已经注销～'
            pass
        except:
            print traceback.print_exc()
            print response.meta['url'],dic_user['user_name']
            pass

    def change(self,item):
        item=str(item)
        if len(item)<2:
            item='0'+item
        return item

