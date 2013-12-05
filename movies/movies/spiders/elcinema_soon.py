from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy import log
from movies.items import elcinema_movie
from scrapy.http import Request
import re
from urlparse import urljoin

class elcinemaSpider(CrawlSpider):
    name = "elcinema_soon"
    domain_name = "elcinema.com"
    CONCURRENT_REQUESTS = 1
    
    
 
    """
    USAGE : scrapy crawl elcinema_soon -o elcinema_soon.json

    only for Egypt but if they add coming soon movies to other countries it will work.
    so for now you only use 
    scrapy crawl elcinema_soon -o elcinema_soon.json

    #These ones won't work for now as they only list Coming soon for egypt
    to crawl a specific country :
        scrapy crawl elcinema_soon  -a country=ae -o elcinema_soon_ae.json
        scrapy crawl elcinema_soon -a country=lb  -o elcinema_soon_lb.json
        scrapy crawl elcinema_soon  -a country=eg -o elcinema_soon_eg.json
    """

    urls = ["http://www.elcinema.com/en/soon/"]
    #default is eg
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
             Rule(SgmlLinkExtractor(restrict_xpaths=('//div[@class="row"]/div//span/a'), unique=True), follow=True,callback='start'),
           )

    def start(self,response):
        hxs=HtmlXPathSelector(response)
        movie_url = response.url #meta
        image_url = hxs.select('//div[@class="page-content"]/div[@class="row"]/*/div[contains(@class,"media-photo")]/a/@href').extract()
        if len(image_url) > 0: 
            image_url = urljoin(response.url,image_url[0])
            yield Request(url=image_url,meta={'url': response.url},dont_filter=True,callback=self.get_photos)

        else:
            yield Request(url=response.url,meta={'image_url': ''},dont_filter=True,callback=self.parse_movie)

    def get_photos(self,response):
        hxs = HtmlXPathSelector(response)
        images = hxs.select('//div[@class="media-photo"]/a/img/@src | //div[@class="photo-navigate"]/img/@src').extract()

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
   
        item = elcinema_movie()

        item['image_urls'] = images
       
        hxs = HtmlXPathSelector(response)
        item['film_name'] = ''.join(hxs.select('normalize-space(//*[@itemprop="name"]/text())').extract())
        
        dur = hxs.select('normalize-space(//div[@class="row"]/ul[@class="stats"]/li/text()[contains(.,"min")])').extract()
        item['duration'] = dur[0] if len(dur) > 0 else ''

        countries = hxs.select('//li[contains(text(),"Releases")]/ul[contains(@class,"stats")]/li/img/@title').extract()
        dates = hxs.select('//li[contains(text(),"Releases")]/ul[contains(@class,"stats")]/li/text()').extract()

        dates = map(lambda s: s.strip().replace(u'\xa0',' '),dates)
        dates = filter(lambda a: a != '', dates)

        item['release_countries_dates'] = self.gen_double_list("release_country",countries,"release_date",dates)

        gen = hxs.select('//div[@class="padded1-v"]//ul/li/text()[2]').extract()
        item['genere'] =  map(lambda s: s.strip(), gen)

        item['country'] = self.country

        item['description'] = ' '.join(hxs.select('//p[@itemprop="description"]/text()[1] | //p[@itemprop="description"]/span/text()').extract()).strip()
        cast = hxs.select('//div[@class="padded1-h"]//a/@title').extract()
        cast_urls = hxs.select('//div[@class="padded1-h"]//a[not(contains(./img/@src ,"."))]/@href').extract()
        item['cast'] = self.gen_double_list("name",cast,"link",map(lambda s: urljoin(response.url,s) , cast_urls) )

        item['url'] = response.url

        item['elcinema_rating'] = ''.join(hxs.select('//*[@itemprop="ratingValue"]/text()').extract())
        item['elcinema_rating_link'] = ''.join( map(lambda s: urljoin(response.url,s),hxs.select('//*[@itemprop="name"]/a/@href').extract()) ) 

        directors = hxs.select('//div[contains(@itemtype,"Movie")]/ul/li/text()[contains(.,"Director")]/..//a/text()').extract()
        directors_links = hxs.select('//div[contains(@itemtype,"Movie")]/ul/li/text()[contains(.,"Director")]/..//a/@href').extract()

        item['directors'] = self.gen_double_list("name",directors,"link",map(lambda s: urljoin(response.url,s) ,  directors_links))
        writers = hxs.select('//div[contains(@itemtype,"Movie")]/ul/li/text()[contains(.,"Written")]/..//a/text()').extract()
        writers_link = hxs.select('//div[contains(@itemtype,"Movie")]/ul/li/text()[contains(.,"Written")]/..//a/@href').extract()

        item['writers'] = self.gen_double_list("name",writers,"link",map(lambda s: urljoin(response.url,s) ,  writers_link))

        item['videos'] = map(lambda s: urljoin(response.url,s) ,  hxs.select('//div[contains(@class,"media-video")]/a/@href').extract())
        
        return item


        
        





