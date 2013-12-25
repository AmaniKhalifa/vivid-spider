from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy import log
from scrapy.http import FormRequest, Request
from virginmegastore.items import Album
from scrapy.http import Request
import re
from urlparse import urljoin
import os

class VirginMusicSpider(CrawlSpider):
  name = "virginmegastore_music"
  domain_name = "virginmegastore.me"
  CONCURRENT_REQUESTS = 1

  start_urls = ["http://www.virginmegastore.me/Music.aspx?pageid=8"]

  rules = (
     Rule(SgmlLinkExtractor(restrict_xpaths=('//div[@class="musictypes"]/table//tr[2]//div/a'), unique=True, process_value=lambda x: x.replace('MusicCategory','MusicAllItems')), follow=False,callback='parse_pages'),
     #Rule(SgmlLinkExtractor(restrict_xpaths=('//a[@id="hlAllItems"]'), unique=True), follow=False,callback='parse_pages'),
   )

  def parse_pages(self,response):
    sel = Selector(response)
    #first page
    music = sel.xpath('//table[@id="dlProducts"]//tr/td/div/a/@href').extract()
    for m in music:
      url = urljoin(response.url,m)
      yield Request(url,callback=self.parse_music)
    pages = sel.xpath('//table[@id="dlPages"]//tr[last()]/td/a/text()').extract()
    if len(pages) > 0:
      n = int(pages[-1])
      for i in xrange(1,n+1):
        page = str(i) if i > 10 else '0'+str(i)
        yield FormRequest.from_response(response,formdata={'searchfield':'SEARCH','ControlTopMenu1$ScriptManager1':'PanelProducts|dlPages$ctl'+page+'$lbtnPage','__EVENTTARGET': 'dlPages$ctl'+page+'$lbtnPage'},dont_click=True,callback=self.parse_all)
   
  def parse_all(self,response):
    sel = Selector(response)
    music = sel.xpath('//table[@id="dlProducts"]//tr/td/div/a/@href').extract()
    for m in music:
      url = urljoin(response.url,m)
      yield Request(url,callback=self.parse_music)
  
  def parse_music(self,response):
    sel = Selector(response)
    item = Album()
    img = sel.xpath('//img[@itemprop="image"]/@src').extract()
    item['image'] = urljoin(response.url,'/'+img[0]) if len(img) > 0 else ''
    item['album_name'] = ''.join(sel.xpath('//*[@itemprop="name"]/*/text()').extract()).strip()
    item['artist_name']  = ''.join(sel.xpath('//div[@class="albumartist"]/span/text()').extract()).strip()

    item['album_format'] = ''.join(sel.xpath('//table[@id="GVCustomFields"]//tr/td//span[contains(text(),"Format")]/../../span/text()').extract()).strip()
    item['original_release_date'] = ''.join(sel.xpath('//table[@id="GVCustomFields"]//tr/td//span[contains(text(),"Release Date")]/../../span/text()').extract()).strip()
    n_disks = sel.xpath('//table[@id="GVCustomFields"]//tr/td//span[contains(text(),"Number of disks")]/../../span/text()').extract()
    item['number_of_disks'] = n_disks[0].strip() if len(n_disks) > 0 else ''
    labels = sel.xpath('//table[@id="GVCustomFields"]//tr/td//span[contains(text(),"Label")]/../../span/text()').extract()
    labels = map(lambda a:a.strip(),labels)
    item['labels'] = labels[0].split(',') if len(labels) > 0 else []
    item['genre'] = ''.join(sel.xpath('//table[@id="GVCustomFields"]//tr/td//span[contains(text(),"Genre")]/../../span/text()').extract()).strip()
    item['original_SKU'] = ''.join(sel.xpath('//table[@id="GVCustomFields"]//tr/td//span[contains(text(),"SKU")]/../../span/text()').extract()).strip()
    
    item['tracks'] = sel.xpath('//table[@id="gvTracks"]//*[contains(@id,"gvTracks_lbName")]/text()').extract()
    item['url'] = response.url
    item['job_id'] = os.getenv('SCRAPY_JOB', "crawler")
    return item
