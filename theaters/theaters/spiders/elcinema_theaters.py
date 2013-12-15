from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy import log
from theaters.items import Theater
from scrapy.http import Request
import re
from urlparse import urljoin
import os

class elcinemaSpider(CrawlSpider):
  name = "elcinema_theaters"
  domain_name = "elcinema.com"
  CONCURRENT_REQUESTS = 1

  start_urls = ["http://www.elcinema.com/en/theaters/eg","http://www.elcinema.com/en/theaters/ae","http://www.elcinema.com/en/theaters/lb"]

  """
    scrapy crawl elcinema_theaters  -o elcinema_theaters.json
  """

  
  rules = (
   #pagination
     Rule(SgmlLinkExtractor(allow=('/\d+'),restrict_xpaths=('//div[contains(@class,"pagination")]/ul/li'), unique=True), follow=True),
     #Movies
     Rule(SgmlLinkExtractor(restrict_xpaths=('//div[@class="boxed-1"]//div[@class="media-photo"]/a'), unique=True), follow=True,callback='parse_theater'),
   )

  
  def parse_theater(self, response):
    sel = Selector(response)
    c = sel.xpath('//div[contains(@class,"breadcrumb")]/ul/li[2]/a/@href').extract()
    country = c[0].split('/')[-2]
    items = []
    item = Theater()
    item['name'] = ''.join(sel.xpath('//div[contains(@class,"breadcrumb")]/ul/li[@class="active"]/text()').extract())
    item['country'] = country
    item['cin_id'] = response.url.split('/')[-2]
    item['telephones'] = sel.xpath('//ul[@class="unstyled"]/li/*[contains(text(),"Telephone")]/../ul/li/text()').extract()
    item['address'] = ''.join(sel.xpath('normalize-space(//ul[@class="unstyled"]//ul[@class="stats"]/li[1]/text()[2])').extract())
    item['district'] = ''.join(sel.xpath('normalize-space(//ul[@class="unstyled"]//ul[@class="stats"]/li[2]/a/text())').extract())
    item['city'] = ''.join(sel.xpath('normalize-space(//ul[@class="unstyled"]//ul[@class="stats"]/li[3]/a/text())').extract())
    item['url'] = response.url
    item['options'] = sel.xpath('//div/ul[contains(@class,"theater-options")]/li/div/@title').extract()

    item['google_map'] = ''.join(sel.xpath('//div[@class="boxed-1"]//iframe[contains(@src,"google")]/@src').extract())

    rating =''.join(sel.xpath('//div[@class="boxed-2"]//ul/li/div/span/text()').extract())
    r = re.findall(r'(\d+.*)\s/',rating)
    item['rating'] = r[0] if len(r) > 0 else 0 
    n = re.findall(r'\d+',''.join(sel.xpath('normalize-space(//div[@class="boxed-2"]//ul/li/div/text()[contains(.,"users")])').extract()))
    item['rating_n'] = n[0] if len(n) > 0 else 0
    screens = ''.join(sel.xpath('//div[@class="span7more"]/ul/li/text()[contains(.,"Screen")]').extract())
    s = re.findall(r'\d+',screens)
    item['screens'] = s[0] if len(s) > 0 else 0
    item['rating_stats'] = urljoin(response.url,''.join(sel.xpath('//div[@class="boxed-2"]/*/a/@href[contains(.,"stats")]').extract()))

    item['image'] = urljoin(response.url,''.join(sel.xpath('//div[@class="span3"]/div[contains(@class,"media-photo")]/a/img/@src').extract()))
    item['job_id'] = os.getenv('SCRAPY_JOB', "crawler")
    return item
