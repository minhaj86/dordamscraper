# -*- coding: utf-8 -*-
import scrapy


class ToscrapeajkerdealSpider(scrapy.Spider):
    name = 'ToScrapeAjkerdeal'
    allowed_domains = ['ajkerdeal.com']
    start_urls = ['http://ajkerdeal.com/']

    def parse(self, response):
        pass
