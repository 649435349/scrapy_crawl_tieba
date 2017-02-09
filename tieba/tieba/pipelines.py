# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import os
op_sys = os.uname()[0]

if "fengyufei" in ''.join(os.uname()):
    DB_URL = "127.0.0.1"
    DB_USER = "root"
    DB_PSW = "fyf!!961004"
    DB_NAME = "scraping"
    DB_CHARSET = "utf8"
else:
    DB_URL = "10.63.76.38"
    DB_USER = "us_player_base"
    DB_PSW = "7DY87EEmVXz8qYf2"
    DB_NAME = "us_player_base_test"
    DB_CHARSET = "utf8"
class TiebaPipeline(object):
    def __init__(self):
        self.conn=MySQLdb.connect(host=DB_URL,user=DB_USER,passwd=DB_PSW,db=DB_NAME,charset=DB_CHARSET)
        self.cur=self.conn.cursor()

    def process_item(self, item, spider):
        if spider.name=='tieba_member_detail_spider' or spider.name=='tieba_fahuitiederen_detail_spider' or spider.name=='test':
            try:
                taskid = item['taskid']
                url = item['url']
                result = item['result']
                updatetime = item['updatetime']
                dt = item['dt']
                sql = 'insert into member_detail(taskid,url,result,updatetime,dt) values (%s,%s,%s,%s,%s)'
                self.cur.execute(sql, (taskid, url, result, updatetime, dt))
                self.conn.commit()
                return item
            except Exception,e:
                print e
        elif spider.name=='tieba_member_followed_tieba_spider' or spider.name=='tieba_fahuitiederen_followed_tieba_spider':
            try:
                taskid = item['taskid']
                url = item['url']
                result = item['result']
                updatetime = item['updatetime']
                dt = item['dt']
                sql = 'insert into member_followed_tieba(taskid,url,result,updatetime,dt) values (%s,%s,%s,%s,%s)'
                self.cur.execute(sql, (taskid, url, result, updatetime, dt))
                self.conn.commit()
                return item
            except Exception,e:
                print e
        elif spider.name=='tieba_information_spider':
            try:
                taskid = item['taskid']
                url = item['url']
                result = item['result']
                updatetime = item['updatetime']
                dt = item['dt']
                sql = 'insert into tieba_information(taskid,url,result,updatetime,dt) values (%s,%s,%s,%s,%s)'
                self.cur.execute(sql, (taskid, url, result, updatetime, dt))
                self.conn.commit()
                return item
            except Exception,e:
                print e


    def close_spider(self,*args,**kw):
        self.conn.close()