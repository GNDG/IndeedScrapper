# -*- coding: utf-8 -*-
import scrapy


class IndeedsSpider(scrapy.Spider):
    name = "indeeds"
    allowed_domains = ["indeed.com"]
    start_urls = ['http://indeed.com/']

    def parse(self, response):
        pass
