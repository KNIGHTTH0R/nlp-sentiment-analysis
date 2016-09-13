# coding: utf-8
__author__ = 'zhourunlai'

from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import Selector
from Douban.items import DoubanItem
import sys
from time import sleep

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


class DoubanSpyder(BaseSpider):
    name = 'douban'
    allowed_domains = ["movie.douban.com"]
    start_urls = []

    # 定期更新 Cookie
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ko;q=0.2,ja;q=0.2,es;q=0.2',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie':'bid=73xC4b52Yuk; gr_user_id=f6988999-d81d-4ed6-aa2c-4a15e48faf85; __utma=223695111.2107527990.1487155950.1487828604.1488617293.15; __utmz=223695111.1488617293.15.10.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/people/zhongchiyu/statuses; ps=y; ct=y; ll="118254"; dbcl2="100617219:/bSYdG1zkWE"; __utma=30149280.1651654104.1486352837.1494148650.1494728266.43; __utmz=30149280.1490678609.41.31.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmv=30149280.10061; ck=6dRs; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1495004555%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; ap=1; _vwo_uuid_v2=353B4B60F717F331958FBE2B3330F5D9|e46bf44f14ed0a4ff46a09c6f115b42c; _pk_id.100001.4cf6=9e9ba595307c5fa3.1487155950.33.1495007451.1494676609.; _pk_ses.100001.4cf6=*; push_noty_num=0; push_doumail_num=0',
        'Host': 'movie.douban.com',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    # 电影搜索页
    def start_requests(self):
        file_opened = open('input.txt', 'r')
        try:
            url_head = "http://movie.douban.com/subject_search?search_text="
            for line in file_opened:
                self.start_urls.append(url_head + line + "&cat=1002")
            for url in self.start_urls:
                yield Request(url, callback=self.parse, cookies=[
                    {'name': 'COOKIE_NAME', 'value': 'VALUE', 'domain': '.douban.com', 'path': '/'}, ])
        finally:
            file_opened.close()

    # 解析搜索结果
    def parse(self, response):
        hxs = Selector(response)
        movie_link = hxs.xpath(
            '//*[@id="content"]/div/div/div/table/tr/td/a/@href').extract()
        # 搜索结果的第一条
        item = movie_link[0]
        yield Request(item, meta={'keyword': ''}, callback=self.parse_article,
                      cookies=[{'name': 'COOKIE_NAME', 'value': 'VALUE', 'domain': '.douban.com', 'path': '/'}, ])

    # 电影详情页
    def parse_article(self, response):
        hxs = Selector(response)
        movie_name = hxs.xpath(
            '//*[@id="content"]/h1/span[1]/text()').extract()
        comment_link_origin = hxs.xpath(
            '//div[@id="comments-section"]/div/h2/span/a/@href').extract()[0]
        comment_link = comment_link_origin.split('?', 1)[0]
        item = DoubanItem()
        item['movie_name'] = movie_name
        item['comment_link'] = comment_link
        yield Request(comment_link, meta={'item': item}, callback=self.parse_item,
                      cookies=[{'name': 'COOKIE_NAME', 'value': 'VALUE', 'domain': '.douban.com', 'path': '/'}, ])

    # 电影评论页
    def parse_item(self, response):
        hxs = Selector(response)
        item = response.meta['item']
        comment_link = item['comment_link']
        comment_content = hxs.xpath(
            '//div[@class="comment-item"]/div[@class="comment"]/p/text()').extract()
        comment_grade = hxs.xpath(
            '//div[@class="comment-item"]/div[@class="comment"]/h3/span/span[contains(@class, "rating")]/@title').extract()
        item['comment_content'] = comment_content
        item['comment_grade'] = comment_grade
        yield item
        # 后页
        next_page = '//div[@id="paginator"]/a[@class="next"]/@href'
        if hxs.xpath(next_page):
            url_nextpage = comment_link + hxs.xpath(next_page).extract()[0]
            item['comment_link'] = comment_link
            yield Request(url_nextpage, meta={'item': item}, callback=self.parse_item, cookies=[
                {'name': 'COOKIE_NAME', 'value': 'VALUE', 'domain': '.douban.com', 'path': '/'}, ], headers=self.headers)
