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

class elcinemaSpider(CrawlSpider):
  name = "elcinema_now"
  domain_name = "elcinema.com"
  CONCURRENT_REQUESTS = 1

  """
    USAGE:
    scrapy crawl elcinema_now 
  """
  start_urls = ["http://www.elcinema.com/en/now/eg","http://www.elcinema.com/en/now/ae","http://www.elcinema.com/en/now/lb"]

  rules = (
    #pagination
    Rule(SgmlLinkExtractor(allow=('/\d+'),restrict_xpaths=('//div[contains(@class,"pagination")]/ul/li'), unique=True), follow=True),
    #Movies
    Rule(SgmlLinkExtractor(restrict_xpaths=('//div[@class="row"]/div//span/a'), unique=True), follow=True,callback='start'),
  )

  def start(self,response):
    sel = Selector(response)
    movie_url = response.url #meta
    url = sel.xpath('//div[@class="boxed-1"]/*/a[contains(text(),"More") and contains(@href,"theater")]/@href').extract()
    image_url = sel.xpath('//div[@class="page-content"]/div[@class="row"]/*/div[contains(@class,"media-photo")]/a/@href').extract()
    theaters_url = urljoin(response.url,url[0]) if len(url) > 0 else None
    if len(image_url) > 0: 
      image_url = urljoin(response.url,image_url[0])
    else:
      image_url = None
    if not theaters_url == None:
      yield Request(url=theaters_url,meta={'url':response.url,'image_url':image_url},callback=self.parse_movie_theaters)

  def parse_movie_theaters(self,response):
    sel = Selector(response)
    countries = sel.xpath('//div[contains(.//@id,"box-")]/@id').extract()
    theaters_strings = []
    theaters_urls = []
    for country in countries:
      theaters_strings.append(country)
      theaters_urls.append(country)

      theaters = sel.xpath('//div[contains(@id,"'+country+'")]/ul/li//a[not(contains(@href,"#"))]/text()').extract()
      theaters_strings.append('\n'.join(theaters))
      urls = sel.xpath('//div[contains(@id,"'+country+'")]/ul/li//a[not(contains(@href,"#"))]/@href').extract()
      theaters_urls.append('\n'.join(urls))

    movie_url = response.request.meta['url']
    image_url = response.request.meta['image_url']
    if not  image_url == None:
      yield Request(url=image_url, meta={'url':movie_url,'theaters_strings':('<splitter>'.join(theaters_strings)),'theaters_urls':('<splitter>'.join(theaters_urls)) },dont_filter=True,callback=self.get_photos)
    else:
      yield Request(url=movie_url, meta={'theaters_strings':('\n'.join(theaters)),'theaters_urls':('\n'.join(theaters_urls))},dont_filter=True,callback=self.parse_movie)

  def get_photos(self,response):
    sel = Selector(response)
    images = sel.xpath('//div[@class="media-photo"]/a/img/@src | //div[@class="photo-navigate"]/img/@src').extract()

    images = map(lambda s : re.sub(r'_\d+\.', '_147.', s), images)
    images = '\n'.join(images)
    movie_url = response.request.meta['url']

    name = response.request.meta['theaters_strings']
    url =  response.request.meta['theaters_urls']
    yield Request(url=movie_url,meta={'image_url':images, 'theaters_strings':name,'theaters_urls':url},dont_filter=True,callback=self.parse_movie)



  def gen_double_list(self,s1,l1,s2,l2):
    l = []
    for i in xrange(0,len(l1)):
      x = {}
      x[s1] = l1[i]
      x[s2] = l2[i]
      l.append(x)
    return l

  def parse_movie(self, response):

    sel = Selector(response)
    theaters_names = response.request.meta['theaters_strings'].split('<splitter>')
    theaters_urls =  response.request.meta['theaters_urls'].split('<splitter>')

    images = response.request.meta['image_url'].split('\n')
    name  = sel.xpath('normalize-space(//*[@itemprop="name"]/text())').extract() 
    if len(name) == 0 or (len(name) > 0 and name[0] == ''):
        name  = sel.xpath('normalize-space(//span[@itemprop="name"]/text())').extract()
    film_name = ''.join(name)
    dur = sel.xpath('normalize-space(//div[@class="row"]/ul[@class="stats"]/li/text()[contains(.,"min")])').extract()
    duration = dur[0] if len(dur) > 0 else ''

    countries = sel.xpath('//li[contains(text(),"Releases")]/ul[contains(@class,"stats")]/li/img/@title').extract()
    dates = sel.xpath('//li[contains(text(),"Releases")]/ul[contains(@class,"stats")]/li/text()').extract()

    dates = map(lambda s: s.strip().replace(u'\xa0',' '),dates)
    dates = filter(lambda a: a != '', dates)
    release_countries_dates = self.gen_double_list("release_country",countries,"release_date",dates)

    gen = sel.xpath('//div[@class="padded1-v"]//ul/li/text()[2]').extract()
    genere =  map(lambda s: s.strip(), gen)

    description = ' '.join(sel.xpath('//p[@itemprop="description"]/text()[1] | //p[@itemprop="description"]/span/text()').extract()).strip()

    cast = sel.xpath('//div[@class="padded1-h"]//a/@title').extract()
    cast_urls = sel.xpath('//div[@class="padded1-h"]//a[not(contains(./img/@src ,"."))]/@href').extract()
    item_cast = self.gen_double_list("name",cast,"link",map(lambda s: urljoin(response.url,s) , cast_urls) )
    elcinema_rating = ''.join(sel.xpath('//*[@itemprop="ratingValue"]/text()').extract())
    elcinema_rating_link = ''.join( map(lambda s: urljoin(response.url,s),sel.xpath('//*[@itemprop="name"]/a/@href').extract()) ) 

    directors = sel.xpath('//div[contains(@itemtype,"Movie")]/ul/li/text()[contains(.,"Director")]/..//a/text()').extract()
    directors_links = sel.xpath('//div[contains(@itemtype,"Movie")]/ul/li/text()[contains(.,"Director")]/..//a/@href').extract() 

    item_directors = self.gen_double_list("name",directors,"link",map(lambda s: urljoin(response.url,s) ,  directors_links))

    writers = sel.xpath('//div[contains(@itemtype,"Movie")]/ul/li/text()[contains(.,"Written")]/..//a/text()').extract()
    writers_link = sel.xpath('//div[contains(@itemtype,"Movie")]/ul/li/text()[contains(.,"Written")]/..//a/@href').extract()
    item_writers = self.gen_double_list("name",writers,"link",map(lambda s: urljoin(response.url,s) ,  writers_link))

    videos = map(lambda s: urljoin(response.url,s) ,  sel.xpath('//div[contains(@class,"media-video")]/a/@href').extract())
    items = []

    i = 0
    while i in xrange(int(len(theaters_names)/2) + 1):

      item = ElcinemaMovie()

      item['country'] = theaters_names[i].replace('box-','')

      j = i+1
      theaters_names_per_country = theaters_names[j].split('\n')
      theaters_urls_per_country = theaters_urls[j].split('\n')
      i = i + 2
      item['theaters'] = self.gen_double_list("name",theaters_names_per_country,"link",map(lambda s: urljoin(response.url,s) , theaters_urls_per_country) )

      item['image_urls'] = images
     
      item['film_name'] = film_name            
      
      item['duration'] = duration

      item['release_countries_dates'] = release_countries_dates

      item['genere'] =  genere

      item['description'] = description

      item['cast'] = item_cast

      item['url'] = response.url

      item['elcinema_rating'] = elcinema_rating
      item['elcinema_rating_link'] = elcinema_rating_link

      item['directors'] = item_directors
      item['writers'] = item_writers

      item['videos'] = videos
      item['job_id'] = os.getenv('SCRAPY_JOB', "crawler")

      items.append(item)
        
    return items