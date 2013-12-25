from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy import log
from scrapy.http import FormRequest, Request
from virginmegastore.items import Album
from virginmegastore.items import Video
from scrapy.http import Request
import re
from urlparse import urljoin
import os

class VirginVideosSpider(CrawlSpider):
  name = "virginmegastore_videos"
  domain_name = "virginmegastore.me"
  CONCURRENT_REQUESTS = 1

  start_urls = ["http://www.virginmegastore.me/Movies.aspx?pageid=14"]
  
  rules = (
     Rule(SgmlLinkExtractor(restrict_xpaths=('//div[@class="musictypes"]/table//tr[2]//div/a'), unique=True, process_value=lambda x: x.replace('MoviesCategory','MoviesAllItems')), follow=False,callback='parse_pages'),
     #Rule(SgmlLinkExtractor(restrict_xpaths=('//a[@id="hlAllItems"]'), unique=True), follow=False,callback='parse_pages'),
   )

  def parse_pages(self,response):
    sel = Selector(response)
    #first page
    videos = sel.xpath('//table[@id="dlProducts"]//tr/td/div/a/@href').extract()
    for m in videos:
      url = urljoin(response.url,m)
      yield Request(url,callback=self.parse_video)
    pages = sel.xpath('//table[@id="dlPages"]//tr[last()]/td/a/text()').extract()
    if len(pages) > 0:
      n = int(pages[-1])
      for i in xrange(1,n+1):
        page = str(i) if i > 10 else '0'+str(i)
        yield FormRequest.from_response(response,formdata={'searchfield':'SEARCH','ControlTopMenu1$ScriptManager1':'PanelProducts|dlPages$ctl'+page+'$lbtnPage','__EVENTTARGET': 'dlPages$ctl'+page+'$lbtnPage'},dont_click=True,callback=self.parse_all)
   
  def parse_all(self,response):
    sel = Selector(response)
    videos = sel.xpath('//table[@id="dlProducts"]//tr/td/div/a/@href').extract()
    for m in videos:
      url = urljoin(response.url,m)
      yield Request(url,callback=self.parse_video)
  
  def parse_video(self,response):
    sel = Selector(response)
    item = Video()
    img = sel.xpath('//img[@itemprop="image"]/@src').extract()
    item['image'] = urljoin(response.url,'/'+img[0]) if len(img) > 0 else ''

    item['video_name'] = ''.join(sel.xpath('//h2[@itemprop="name"]/*/text()').extract()).strip()
    actors = sel.xpath('//div[@itemprop="actors"]/span/text()').extract()
    actors = actors[0].split(',') if len(actors) > 0 else ''
    item['actors']  = map(lambda a:a.replace(':','').strip(),actors)

    directors = sel.xpath('//div[@itemprop="director"]/span/text()').extract()
    directors = directors[0].split(',') if len(directors) > 0 else ''
    item['directors'] = map(lambda a:a.replace(':','').strip(),directors)

    syno = sel.xpath('//div[@id="bigSynopsis"]//*/text()').extract()
    if len(syno) > 0:
    	syno = sel.xpath('//div[@id="smallSynopsis"]//*/text()').extract()
    item['synopsis'] = '\n'.join(syno)

    item['format'] = ''.join(sel.xpath('//table[@id="GVCustomFields"]//tr/td//span[contains(text(),"Format")]/../../span/text()').extract()).strip()
    n_disks = sel.xpath('//table[@id="GVCustomFields"]//tr/td//span[contains(text(),"Number of disks")]/../../span/text()').extract()
    item['number_of_disks'] = n_disks[0].strip() if len(n_disks) > 0 else ''   
    lang = sel.xpath('//table[@id="GVCustomFields"]//tr/td//span[contains(text(),"Language")]/../../span/text()').extract()
    lang = lang[0].split(',') if len(lang) > 0 else ''
    item['language'] = map(lambda a:a.strip(),lang)
    subs = sel.xpath('//table[@id="GVCustomFields"]//tr/td//span[contains(text(),"Subtitles")]/../../span/text()').extract()
    subs = subs[0].split(',') if len(subs) > 0 else ''
    item['subtitles'] = map(lambda a:a.replace(':','').strip(),subs)

    item['parental_guidance'] = ''.join(sel.xpath('//table[@id="GVCustomFields"]//tr/td//span[contains(text(),"Parental Guidance")]/../../span/text()').extract())

    item['studio'] = ''.join(sel.xpath('//table[@id="GVCustomFields"]//tr/td//span[contains(text(),"Studio")]/../../span/text()').extract())

    item['dvd_release_date'] = ''.join(sel.xpath('//table[@id="GVCustomFields"]//tr/td//span[contains(text(),"release date")]/../../span/text()').extract()).strip()
    item['run_time'] = ''.join(sel.xpath('//table[@id="GVCustomFields"]//tr/td//span[contains(text(),"Run Time")]/../../span/text()').extract()).strip()

    genre = sel.xpath('//table[@id="GVCustomFields"]//tr/td//span[contains(text(),"Genre")]/../../span/text()').extract()
    genre = genre[0].split(',') if len(genre) > 0 else ''
    item['genre'] = map(lambda a:a.strip(),genre)

    item['description'] = ''.join(sel.xpath('//div[@class="moviespad"]/p/text() | //div[@class="moviespad"]/text()[last()]').extract()).strip()
    item['url'] = response.url
    item['job_id'] = os.getenv('SCRAPY_JOB', "crawler")
    return item