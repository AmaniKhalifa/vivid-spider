from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy import log
from elcinemamovies.items import ElcinemaMovie
from scrapy.http import Request
import re
from urlparse import urljoin
import os

class ElcinemaSoonSpider(CrawlSpider):
  name = "elcinema_soon"
  domain_name = "elcinema.com"
  CONCURRENT_REQUESTS = 1

  """
    USAGE : scrapy crawl elcinema_soon
    only for eg
  """

  start_urls = ["http://www.elcinema.com/en/soon/"]

  country = 'eg'
  rules = (
    #pagination
    Rule(SgmlLinkExtractor(allow=('/\d+'),restrict_xpaths=('//div[contains(@class,"pagination")]/ul/li'), unique=True), follow=True),
    #Movies
    Rule(SgmlLinkExtractor(restrict_xpaths=('//div[@class="row"]/div//span/a'), unique=True), follow=True,callback='start'),
  )

  def start(self,response):
    sel = Selector(response)
    movie_url = response.url #meta
    image_url = sel.xpath('//div[@class="page-content"]/div[@class="row"]/*/div[contains(@class,"media-photo")]/a/@href').extract()
    if len(image_url) > 0: 
      image_url = urljoin(response.url,image_url[0])
      yield Request(url=image_url,meta={'url': response.url},dont_filter=True,callback=self.get_photos)
    else:
      yield Request(url=response.url,meta={'image_url': ''},dont_filter=True,callback=self.parse_movie)

  def get_photos(self,response):
    sel = Selector(response)
    images = sel.xpath('//div[@class="media-photo"]/a/img/@src | //div[@class="photo-navigate"]/img/@src').extract()

    images = map(lambda s : re.sub(r'_\d+\.', '_147.', s), images)
    images = '\n'.join(images)
    movie_url = response.request.meta['url']
    
    yield Request(url=movie_url,meta={'image_url':images},dont_filter=True,callback=self.parse_movie)

  def gen_double_list(self,s1,l1,s2,l2):
    l = []
    for i in xrange(0,len(l1)):
      x = {}
      x[s1] = l1[i]
      x[s2] = l2[i]
      l.append(x)
    return l
  
  def parse_movie(self, response):
    images = response.request.meta['image_url'].split('\n')

    item = ElcinemaMovie()

    item['image_urls'] = images
   
    sel = Selector(response)
    item['film_name'] = ''.join(sel.xpath('normalize-space(//*[@itemprop="name"]/text())').extract())
    
    dur = sel.xpath('normalize-space(//div[@class="row"]/ul[@class="stats"]/li/text()[contains(.,"min")])').extract()
    item['duration'] = dur[0] if len(dur) > 0 else ''

    countries = sel.xpath('//li[contains(text(),"Releases")]/ul[contains(@class,"stats")]/li/img/@title').extract()
    dates = sel.xpath('//li[contains(text(),"Releases")]/ul[contains(@class,"stats")]/li/text()').extract()

    dates = map(lambda s: s.strip().replace(u'\xa0',' '),dates)
    dates = filter(lambda a: a != '', dates)

    item['release_countries_dates'] = self.gen_double_list("release_country",countries,"release_date",dates)

    gen = sel.xpath('//div[@class="padded1-v"]//ul/li/text()[2]').extract()
    item['genere'] =  map(lambda s: s.strip(), gen)

    item['country'] = self.country

    item['description'] = ' '.join(sel.xpath('//p[@itemprop="description"]/text()[1] | //p[@itemprop="description"]/span/text()').extract()).strip()
    cast = sel.xpath('//div[@class="padded1-h"]//a/@title').extract()
    cast_urls = sel.xpath('//div[@class="padded1-h"]//a[not(contains(./img/@src ,"."))]/@href').extract()
    item['cast'] = self.gen_double_list("name",cast,"link",map(lambda s: urljoin(response.url,s) , cast_urls) )

    item['url'] = response.url

    item['elcinema_rating'] = ''.join(sel.xpath('//*[@itemprop="ratingValue"]/text()').extract())
    item['elcinema_rating_link'] = ''.join( map(lambda s: urljoin(response.url,s),sel.xpath('//*[@itemprop="name"]/a/@href').extract()) ) 

    directors = sel.xpath('//div[contains(@itemtype,"Movie")]/ul/li/text()[contains(.,"Director")]/..//a/text()').extract()
    directors_links = sel.xpath('//div[contains(@itemtype,"Movie")]/ul/li/text()[contains(.,"Director")]/..//a/@href').extract()

    item['directors'] = self.gen_double_list("name",directors,"link",map(lambda s: urljoin(response.url,s) ,  directors_links))
    writers = sel.xpath('//div[contains(@itemtype,"Movie")]/ul/li/text()[contains(.,"Written")]/..//a/text()').extract()
    writers_link = sel.xpath('//div[contains(@itemtype,"Movie")]/ul/li/text()[contains(.,"Written")]/..//a/@href').extract()

    item['writers'] = self.gen_double_list("name",writers,"link",map(lambda s: urljoin(response.url,s) ,  writers_link))

    item['videos'] = map(lambda s: urljoin(response.url,s) ,  sel.xpath('//div[contains(@class,"media-video")]/a/@href').extract())
    
    item['job_id'] = os.getenv('SCRAPY_JOB', "crawler")
    item['elcinema_work_id'] = response.url.split('/')[-2]
    item['language'] = self.site_language
    
    return item