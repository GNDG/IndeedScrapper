from scrapy.selector import Selector
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.spiders import BaseSpider
from scrapy.http import Request
import time
import sys
import json
from indeed.items import IndeedItem


class IndeedSpider(CrawlSpider):
    name = "indeed"
    allowed_domains = ["indeed.co.in"]
    start_time = time.time()
    start_urls = [
        "http://www.indeed.co.in/jobs?l=Delhi"
    ]

    rules = ( 
        Rule(LxmlLinkExtractor(allow=('/jobs.q=&l=Delhi&sort=date$','q=&l=Delhi&sort=date&start=[0-9]+$',),deny=('/my/mysearches', '/preferences', '/advanced_search','/my/myjobs')), callback='parse_item', follow=True),
        )

    def parse_next_site(self, response):
        item = response.request.meta['item']
        item['summary_url'] = response.url
        print('\n Crawling  %s\n' % response.url)
        hxs1 = Selector(response)
        item['detailed_summary'] = hxs1.select("//span[@class='summary']").extract()
        item['crawl_timestamp'] =  time.strftime('%Y-%m-%d %H:%M:%S')
        print("--- %s seconds ---" % (time.time() - self.start_time))
        return item 


    def parse_item(self, response):
        print(response)
        print('\n Crawling  %s\n' % response.url)
        hxs = Selector(response)
        sites = hxs.select("//div[@class='  row  result'] | //div[@class='row  result'] | //div[@class='lastRow  row  result'] | //div[@class='row sjlast result']")
        print (len(sites))
        items = []
#--------------------------------------------------------------------------------------------#
        for site in sites:
            print ("test1")
            item = IndeedItem(company='none')
            #print(site.select("descendant::a[@data-tn-element='jobTitle']/@href").extract())
            item['job_title'] = site.select("descendant::a[@data-tn-element='jobTitle']/text()").extract()
            link_url= site.select("descendant::a[@data-tn-element='jobTitle']/@href").extract()
            item['link_url'] = link_url[0]
            item['crawl_url'] = response.url
            # Not all entries have a company
            if  site.select("descendant::span[@class='company']/span/text()").extract() == []:
                if site.select("descendant::span[@class='company']/span/a/text()").extract() == []:
                    if len(site.select("descendant::span[@class='company']/a/text()").extract()) == 1:
                        item['company'] = site.select("descendant::span[@class='company']/a/text()").extract()
                    else:
                        item['company'] = site.select("descendant::span[@class='company']/text()").extract()
                else:
                    item['company'] = site.select("descendant::span[@class='company']/a/text()").extract()
                item['salary'] = site.select("descendant::div[@class='sjcl']/div/text()").extract()
                item['location'] = site.select("descendant::span[@class='location']/text()").extract()
            else:
                if len(site.select("descendant::span[@class='company']/span/a/text()").extract()) == 1:
                    item['company'] = site.select("descendant::span[@class='company']/span/a/text()").extract()
                else:
                    item['company'] = site.select("descendant::span[@class='company']/span/text()").extract()    
                item['salary'] = site.select("descendant::td[@class='snip']/nobr/text()").extract()
                item['location'] = site.select("descendant::span[@class='location']/span/text()").extract()
            tempSource = str(site.select("descendant::div[@class='result-link-bar']/script/text()").extract()[0]).split('=',1)
            tempSource = tempSource[1]
            tempSource = json.loads(tempSource[:-1])
            try:
                item['source'] = tempSource['source']
            except KeyError, e:
                item['source'] = []
            try:
                item['sponsored'] = tempSource['sponsored']
            except KeyError, e:
                item['sponsored'] = []
            
            try:
                item['found_date'] = tempSource['relativeJobAge']
            except KeyError, e:
               item['found_date'] = []
        

            try:
                item['job_key'] = tempSource['jobKey']
            except KeyError, e:
               item['job_key'] = []
            
            item['summary'] = site.select("descendant::span[@class='summary']/text()").extract()
            if(item['source'] == 'Indeed'):
                request = Request("http://www.indeed.co.in" + item['link_url'], callback=self.parse_next_site)
                request.meta['item'] = item
                yield request
            else:
                yield item
            items.append(item)
        return
            
SPIDER=IndeedSpider()
