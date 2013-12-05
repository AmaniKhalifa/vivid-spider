from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy import log
from movies.items import Movie
from scrapy.http import Request
import re
from urlparse import urljoin

class imdbSpider(CrawlSpider):
    name = "imdb"
    domain_name = "imdb.com"
    CONCURRENT_REQUESTS = 1

    start_urls = ["http://www.imdb.com/movies-in-theaters/","http://www.imdb.com/movies-coming-soon/"]
    
    rules = (

    	     #Coming Soon pages
             
             #Rule(SgmlLinkExtractor(restrict_xpaths=('//ul[@class="list_tabs"]/li/a[contains(text(),"Soon")]'), unique=True), follow=True,callback='parse_pages'),
             #Movies
             Rule(SgmlLinkExtractor(restrict_xpaths=('//div[contains(@class,"list_item")]//tr/td/h4[@itemprop="name"]/a'), unique=True), follow=True,callback='parse_movie'),
           )

    def parse_start_url(self,response):
    	hxs = HtmlXPathSelector(response)
    	pages = hxs.select('//select[contains(@name,"sort")]/option/@value').extract()
    	if len(pages) > 0 :
	    	for page in pages:
	    		url = urljoin(response.url, page)
	    		yield Request(url)
	   	else:
	   		yield Request(response.url)
    
    def parse_movie(self, response):
        hxs = HtmlXPathSelector(response)
        items = []
        item = Movie()
        item['name'] = ''.join(hxs.select('//h1/span[@itemprop="name"]/text()').extract())
        dur = hxs.select('normalize-space(//div[@class="infobar"]/time[@itemprop="duration"]/text())').extract()
        item['duration'] = dur[0] if len(dur) > 0 else ''
        classi = hxs.select('//div[@class="infobar"]/span[contains(@itemprop,"Rating")]/@content').extract()
        item['classification'] = classi[0] if len(classi) > 0 else ''
        release = hxs.select('//div[@class="infobar"]/span[@class="nobr"]/a/text()').extract()

        item['genere'] = hxs.select('//div[@class="infobar"]/a[contains(@href,"genre")]/span/text()').extract()
        item['release_date'] = release[0]
        item['release_country'] = re.findall(r'\((.*)\)',release[1])[0]
        rating = hxs.select('//div[@class="star-box-details"]/strong//span[contains(@itemprop,"rating")]/text()').extract()
        item['imdb_rating'] = rating[0] if len(rating) > 0 else ''
        num_of_users_rated = hxs.select('//div[@class="star-box-details"]/a/span[contains(@itemprop,"rating")]/text()').extract()
        item['num_user_rated'] = num_of_users_rated[0] if len(num_of_users_rated) > 0 else ''
    	item['description'] = ''.join(hxs.select('//p[@itemprop="description"]/text()').extract())
    	item['story_line'] = ''.join(hxs.select('//div[@id="titleStoryLine"]/div[@itemprop="description"]/p/text()').extract())
    	item['directors'] = hxs.select('//div[@itemprop="director"]/a/span/text()').extract()
    	item['writers'] = hxs.select('//div[@itemprop="creator"]/a/span/text()').extract()
    	item['cast'] = hxs.select('//table[@class="cast_list"]//tr/td[@itemprop="actor"]/a/span/text()').extract()
    	item['image_url'] = hxs.select('//td[@id="img_primary"]//img/@src').extract()
    	item['url'] = response.url
        return item


        
        





