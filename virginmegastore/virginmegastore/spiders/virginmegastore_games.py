from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy import log
from scrapy.http import FormRequest, Request
from virginmegastore.items import Game
from scrapy.http import Request
import re
from urlparse import urljoin
import os

class VirginGamesSpider(CrawlSpider):
  name = "virginmegastore_games"
  domain_name = "virginmegastore.me"
  CONCURRENT_REQUESTS = 1

  start_urls = ["http://www.virginmegastore.me/Games.aspx?pageid=15"]


  
  rules = (
     Rule(SgmlLinkExtractor(restrict_xpaths=('//div[@class="musictypes"]/table//tr[2]//div/a[not(contains(@href,"pageid")) and contains(@href,"GamesCategory")]'), unique=True, process_value=lambda x: x.replace('GamesCategory','GamesAllItems')), follow=False,callback='parse_pages'),
     #Rule(SgmlLinkExtractor(restrict_xpaths=('//a[@id="hlAllItems"]'), unique=True), follow=False,callback='parse_pages'),

   )


  def parse_pages(self,response):
    sel = Selector(response)
    #first page
    games = sel.xpath('//table[@id="dlProducts"]//tr/td/div/div/a/@href').extract()
    for m in games:
      url = urljoin(response.url,m)
      yield Request(url,callback=self.parse_game)
    pages = sel.xpath('//table[@id="dlPages"]//tr[last()]/td/a/text()').extract()
    if len(pages) > 0:
      n = int(pages[-1])
      for i in xrange(1,n+1):
            page = str(i) if i > 10 else '0'+str(i)
            yield FormRequest.from_response(response,formdata={'searchfield':'SEARCH','ControlTopMenu1$ScriptManager1':'PanelProducts|dlPages$ctl'+page+'$lbtnPage','__EVENTTARGET': 'dlPages$ctl'+page+'$lbtnPage'},dont_click=True,callback=self.parse_all)
   
  def parse_all(self,response):
    sel = Selector(response)
    games = sel.xpath('//table[@id="dlProducts"]//tr/td/div/div/a/@href').extract()
    for m in games:
      url = urljoin(response.url,m)
      yield Request(url,callback=self.parse_game)
  
  def parse_game(self,response):
    sel = Selector(response)
    item = Game()
    img = sel.xpath('//img[@id="imgProduct"]/@src').extract()
    item['image'] = urljoin(response.url,'/'+img[0]) if len(img) > 0 else ''
    item['age_rating'] = ''.join(sel.xpath('//span[@id="lbRating"]/text()').extract())

    item['game_name'] = ''.join(sel.xpath('//span[@id="lbTitle"]/text()').extract()).strip()

    item['format'] = ''.join(sel.xpath('//span[@id="lbFormat"]/text()').extract()).strip()
    syno = sel.xpath('//div[@id="bigSynopsis"]//*/text()').extract()
    if len(syno) > 0:
      syno = sel.xpath('//div[@id="smallSynopsis"]//*/text()').extract()
    item['synopsis'] = '\n'.join(syno)

    available_consoles = ''.join(sel.xpath('//div[@id="divDescription"]/text()').extract())
    available_consoles = available_consoles.split(',')
    item['available_consoles'] = map(lambda a:a.strip(),available_consoles)
    item['publisher'] = ''.join(sel.xpath('//table[@id="GVCustomFields"]//tr/td//span[contains(text(),"Publisher")]/../../span/text()').extract())
    item['original_SKU'] = ''.join(sel.xpath('//table[@id="GVCustomFields"]//tr/td//span[contains(text(),"SKU")]/../../span/text()').extract()).strip()
    item['region'] = ''.join(sel.xpath('//table[@id="GVCustomFields"]//tr/td//span[contains(text(),"Region")]/../../span/text()').extract())
    item['original_release_date'] = ''.join(sel.xpath('//table[@id="GVCustomFields"]//tr/td//span[contains(text(),"Release Date")]/../../span/text()').extract()).strip()
    item['url'] = response.url
    return item
