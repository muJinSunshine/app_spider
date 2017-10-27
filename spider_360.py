# coding=utf8
import re
from pymysql import *
import requests
from lxml import etree
from datetime import datetime


class Spider360(object):
    def __init__(self):
        self.con = connect(
            host="localhost",
            port=3306,
            database='bdweb',
            user='root',
            password='mysql',
            charset='utf8',
        )
        self.cs1 = self.con.cursor()

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36"
            }

    def get_not_app_list(self):
        query_sql = """
                    select app from app_not2
                """
        self.cs1.execute(query_sql)
        query_list = self.cs1.fetchall()
        return query_list

    def parse(self, query):

        url = 'http://zhushou.360.cn/search/index/?kw={}'.format(query)

        res = requests.get(url, headers=self.headers)

        res = etree.HTML(res.content)
        detail_url_list = res.xpath('//div[@class="SeaCon"]/ul/li/dl/dd/h3/a/@href')
        print(detail_url_list)
        for detail_url in detail_url_list[:1]:
            detail_url = "http://zhushou.360.cn" + detail_url

            self.parse_detail(detail_url)

    def parse_detail(self, detail_url):
        response = requests.get(detail_url, headers=self.headers)
        # print(response.content)
        tree = etree.HTML(response.content)
        company_name = tree.xpath('//*[@id="sdesc"]/div/div/table/tbody/tr[1]/td[1]/text()')
        if len(company_name) == 0:
            company_name = [""]
        company_name = company_name[0]
        name = tree.xpath('//*[@id="app-name"]/span/text()')
        if len(name) == 0:
            name = ['']
        name = name[0]
        # print(name, company_name)
        package = ""
        version_num = tree.xpath('//*[@id="sdesc"]/div/div/table/tbody/tr[2]/td[1]/text()')
        if len(version_num) == 0:
            version_num = ['']
        version_num = version_num[0]
        brief_list = tree.xpath('//div[@class="breif"]/text()')
        brief = "".join(brief_list).strip()
        logo = tree.xpath('//*[@id="app-info-panel"]/div/dl/dt/img/@src')[0]
        picshows = tree.xpath('//*[@id="scrollbar"]/div/div/img/@src')
        picshows = "|".join(picshows)
        size = tree.xpath('//*[@id="app-info-panel"]/div/dl/dd/div/span[4]/text()')
        if len(size) == 0:
            size = [""]
        size = size[0]
        download_vol_desc = tree.xpath('//*[@id="app-info-panel"]/div/dl/dd/div/span[3]/text()')[0].split("：")[-1]

        app_utime = tree.xpath('//*[@id="sdesc"]/div/div/table/tbody/tr[1]/td[2]/text()')
        if len(app_utime) == 0:
            app_utime = [""]
        app_utime = app_utime[0]

        good_ratio = ""
        # print(good_ratio_num)
        reply_num = ""
        print(reply_num)
        tag_list = tree.xpath('/html/body/div[3]/div[2]/div/div[2]/div[2]/div[2]/a/text()')
        category_all = "|".join(tag_list)
        # print(company_name, name, package, version_num, brief,
        #               picshows, size, download_vol_desc, app_utime, good_ratio, reply_num, category_all, logo)
        self.connect_mysql(company_name, name, package, version_num, brief,
                      picshows, size, download_vol_desc, app_utime, good_ratio, reply_num, category_all, logo)

    def connect_mysql(self, company_name, name, package, version_num, brief,
                      picshows, size, download_vol_desc, app_utime, good_ratio, reply_num, category_all, logo):

        insert_sql = """
            insert into app_360_1(company_name, name, package, version_no,
                   brief, picshows, size, download_vol_desc,
                   app_utime, good_ratio, reply_num, category_all, utime, ctime, logo, source_id) value(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        utime = ctime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        par = [company_name, name, package, version_num,
               brief, picshows, size, download_vol_desc,
               app_utime, good_ratio, reply_num, category_all, utime, ctime, logo, 2]
        self.cs1.execute(insert_sql, par)
        self.con.commit()

    def run(self):
        query_list = self.get_not_app_list()
        for query in query_list:
            query = query[0]
            self.parse(query)

spider = Spider360()
spider.run()