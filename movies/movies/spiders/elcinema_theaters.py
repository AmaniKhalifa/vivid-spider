from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy import log
from movies.items import Movie
from movies.items import Theater
from scrapy.http import Request
import re
from urlparse import urljoin

class elcinemaSpider(CrawlSpider):
    name = "elcinema_theaters"
    domain_name = "elcinema.com"
    CONCURRENT_REQUESTS = 1

    urls = ["http://www.elcinema.com/en/theaters/"]

    """
    to crawl a specific country :
        scrapy crawl elcinema_theaters  -a country=ae -o elcinema_theaters_ae.json
        scrapy crawl elcinema_theaters  -a country=lb -o elcinema_theaters_lb.json 
        scrapy crawl elcinema_theaters  -a country=eg -o elcinema_theaters_eg.json 
    """
    #default country to crawl in eg
    country = 'eg'

    def __init__(self, country=None):
        super(elcinemaSpider, self).__init__()
        self.country = country
        if country != None:
            for url in self.urls:
                self.start_urls.append(url+country)
        else:
            self.start_urls = self.urls

    
    rules = (

    	     #pagination
             Rule(SgmlLinkExtractor(allow=('/\d+'),restrict_xpaths=('//div[contains(@class,"pagination")]/ul/li'), unique=True), follow=True),
             #Movies
             Rule(SgmlLinkExtractor(restrict_xpaths=('//div[@class="boxed-1"]//div[@class="media-photo"]/a'), unique=True), follow=True,callback='parse_theater'),
           )

    
    def parse_theater(self, response):
        hxs = HtmlXPathSelector(response)
        items = []
        item = Theater()
        item['name'] = ''.join(hxs.select('//div[contains(@class,"breadcrumb")]/ul/li[@class="active"]/text()').extract())
        item['country'] = self.country
        item['cin_id'] = response.url.split('/')[-2]
        item['telephones'] = hxs.select('//ul[@class="unstyled"]/li/*[contains(text(),"Telephone")]/../ul/li/text()').extract()
        item['address'] = ''.join(hxs.select('normalize-space(//ul[@class="unstyled"]//ul[@class="stats"]/li[1]/text()[2])').extract())
        item['district'] = ''.join(hxs.select('normalize-space(//ul[@class="unstyled"]//ul[@class="stats"]/li[2]/a/text())').extract())
        item['city'] = ''.join(hxs.select('normalize-space(//ul[@class="unstyled"]//ul[@class="stats"]/li[3]/a/text())').extract())
        item['url'] = response.url
        item['options'] = hxs.select('//div/ul[contains(@class,"theater-options")]/li/div/@title').extract()

        item['google_map'] = ''.join(hxs.select('//div[@class="boxed-1"]//iframe[contains(@src,"google")]/@src').extract())
    
        rating =''.join(hxs.select('//div[@class="boxed-2"]//ul/li/div/span/text()').extract())
        r = re.findall(r'(\d+.*)\s/',rating)
        item['rating'] = r[0] if len(r) > 0 else 0 
        n = re.findall(r'\d+',''.join(hxs.select('normalize-space(//div[@class="boxed-2"]//ul/li/div/text()[contains(.,"users")])').extract()))
        item['rating_n'] = n[0] if len(n) > 0 else 0
        screens = ''.join(hxs.select('//div[@class="span7more"]/ul/li/text()[contains(.,"Screen")]').extract())
        s = re.findall(r'\d+',screens)
        item['screens'] = s[0] if len(s) > 0 else 0
        item['rating_stats'] = urljoin(response.url,''.join(hxs.select('//div[@class="boxed-2"]/*/a/@href[contains(.,"stats")]').extract()))

        item['image'] = urljoin(response.url,''.join(hxs.select('//div[@class="span3"]/div[contains(@class,"media-photo")]/a/img/@src').extract()))
        return item
