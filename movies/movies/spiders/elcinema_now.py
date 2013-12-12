from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy import log
from movies.items import elcinema_movie
from scrapy.http import Request
import re
from urlparse import urljoin
from scrapy.selector import Selector

class elcinemaSpider(CrawlSpider):
    name = "elcinema_now"
    domain_name = "elcinema.com"
    CONCURRENT_REQUESTS = 1

    """
    USAGE:
    to crawl a specific country :
        scrapy crawl elcinema_now  -a country=ae -o elcinema_now_ae.json
        scrapy crawl elcinema_now  -a country=lb -o elcinema_now_lb.json
        scrapy crawl elcinema_now  -a country=eg -o elcinema_now_eg.json
    """
    #default country to crawl in eg

    start_urls = ["http://www.elcinema.com/en/now/eg", "http://www.elcinema.com/en/now/lb", "http://www.elcinema.com/en/now/ae"]
    
    rules = (
    	     #pagination
             Rule(SgmlLinkExtractor(allow=('/\d+'),restrict_xpaths=('//div[contains(@class,"pagination")]/ul/li'), unique=True), follow=True),
             #Movies
             Rule(SgmlLinkExtractor(restrict_xpaths=('//div[@class="row"]/div//span/a'), unique=True), follow=True,callback='start'),
           )

    def start(self,response):
        hxs=Selector(response)
        movie_url = response.url #meta
        url = hxs.select('//div[@class="boxed-1"]/*/a[contains(text(),"More") and contains(@href,"theater")]/@href').extract()
        image_url = hxs.select('//div[@class="page-content"]/div[@class="row"]/*/div[contains(@class,"media-photo")]/a/@href').extract()
        theaters_url = urljoin(response.url,url[0]) if len(url) > 0 else None
        if len(image_url) > 0: 
            image_url = urljoin(response.url,image_url[0])
        else:
            image_url = None
        if not theaters_url == None:
            yield Request(url=theaters_url,meta={'url':response.url,'image_url':image_url},callback=self.parse_movie_theaters)

    def parse_movie_theaters(self,response):
        hxs=Selector(response)
        theaters = hxs.select('//div[@class="boxed-1" and contains(.//@id,"'+self.country+'")]/div/ul/li//a[not(contains(@href,"#"))]/text()').extract()
        theaters_urls = hxs.select('//div[@class="boxed-1" and contains(.//@id,"'+self.country+'")]/div/ul/li//a[not(contains(@href,"#"))]/@href').extract()
        movie_url = response.request.meta['url']
        image_url = response.request.meta['image_url']
        if not  image_url == None:
            yield Request(url=image_url, meta={'url':movie_url,'theaters_strings':('\n'.join(theaters)),'theaters_urls':('\n'.join(theaters_urls)) },dont_filter=True,callback=self.get_photos)
        else:
            yield Request(url=movie_url, meta={'theaters_strings':('\n'.join(theaters)),'theaters_urls':('\n'.join(theaters_urls))},dont_filter=True,callback=self.parse_movie)


    def get_photos(self,response):
        hxs = Selector(response)
        images = hxs.select('//div[@class="media-photo"]/a/img/@src | //div[@class="photo-navigate"]/img/@src').extract()

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
        name = response.request.meta['theaters_strings'].split('\n')
        url =  response.request.meta['theaters_urls'].split('\n')
        images = response.request.meta['image_url'].split('\n')
   
        item = elcinema_movie()

        item['theaters'] = self.gen_double_list("name",name,"link",map(lambda s: urljoin(response.url,s) , url) )

        item['image_urls'] = images
       
        hxs = HtmlXPathSelector(response)
        item['film_name'] = ''.join(hxs.select('normalize-space(//*[@itemprop="name"]/text())').extract())
        
        dur = hxs.select('normalize-space(//div[@class="row"]/ul[@class="stats"]/li/text()[contains(.,"min")])').extract()
        item['duration'] = dur[0] if len(dur) > 0 else ''

        #item['release_date'] = ' '.join(hxs.select('//div[contains(@itemtype,"Movie")]/ul/li/text()[contains(.,"Date")]/../a/text()[not(contains(.,"Add Release date"))]').extract()).replace(u'\xa0',' ')

        countries = hxs.select('//li[contains(text(),"Releases")]/ul[contains(@class,"stats")]/li/img/@title').extract()
        dates = hxs.select('//li[contains(text(),"Releases")]/ul[contains(@class,"stats")]/li/text()').extract()

        dates = map(lambda s: s.strip().replace(u'\xa0',' '),dates)
        dates = filter(lambda a: a != '', dates)

        item['release_countries_dates'] = self.gen_double_list("release_country",countries,"release_date",dates)

        gen = hxs.select('//div[@class="padded1-v"]//ul/li/text()[2]').extract()
        item['genere'] =  map(lambda s: s.strip(), gen)

        item['country'] = ''

    	item['description'] = ' '.join(hxs.select('//p[@itemprop="description"]/text()[1] | //p[@itemprop="description"]/span/text()').extract()).strip()
        cast = hxs.select('//div[@class="padded1-h"]//a/@title').extract()
        cast_urls = hxs.select('//div[@class="padded1-h"]//a[not(contains(./img/@src ,"."))]/@href').extract()
        item['cast'] = self.gen_double_list("name",cast,"link",map(lambda s: urljoin(response.url,s) , cast_urls) )

    	item['url'] = response.url

        item['elcinema_rating'] = ''.join(hxs.select('//*[@itemprop="ratingValue"]/text()').extract())
        item['elcinema_rating_link'] = ''.join( map(lambda s: urljoin(response.url,s),hxs.select('//*[@itemprop="name"]/a/@href').extract()) ) 

        directors = hxs.select('//div[contains(@itemtype,"Movie")]/ul/li/text()[contains(.,"Director")]/..//a/text()').extract()
        directors_links = hxs.select('//div[contains(@itemtype,"Movie")]/ul/li/text()[contains(.,"Director")]/..//a/@href').extract()
        """for i in xrange(0,len(directors)-1) :
            x = {}
            x['link'] = urljoin(response.url,directors[i])
            i = i + 1
            x['name'] = directors[i]
            directors_link.append(x)"""

        item['directors'] = self.gen_double_list("name",directors,"link",map(lambda s: urljoin(response.url,s) ,  directors_links))
        writers = hxs.select('//div[contains(@itemtype,"Movie")]/ul/li/text()[contains(.,"Written")]/..//a/text()').extract()
        writers_link = hxs.select('//div[contains(@itemtype,"Movie")]/ul/li/text()[contains(.,"Written")]/..//a/@href').extract()
        """for i in xrange(0,len(writers)-1) :
            x = {}photo_list/
            x['link'] = urljoin(response.url,writers[i])
            i = i + 1
            x['name'] = writers[i]
            writers_link.append(x)
        """
        item['writers'] = self.gen_double_list("name",writers,"link",map(lambda s: urljoin(response.url,s) ,  writers_link))

        item['videos'] = map(lambda s: urljoin(response.url,s) ,  hxs.select('//div[contains(@class,"media-video")]/a/@href').extract())
        return item





        
        





