from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy import log
from imdbmovies.items import IMDBMovie
from scrapy.http import Request
import re
from urlparse import urljoin
import os

class imdbSpider(CrawlSpider):
  name = "imdb_movies"
  domain_name = "imdb.com"
  CONCURRENT_REQUESTS = 1

  """
    USAGE: 
    scrapy crawl imdb_movies
  """

  start_urls = ["http://www.imdb.com/movies-in-theaters/","http://www.imdb.com/movies-coming-soon/"]

  rules = (
    Rule(SgmlLinkExtractor(restrict_xpaths=('//div[contains(@class,"list_item")]//tr/td/h4[@itemprop="name"]/a'), unique=True), follow=True,callback='get_images_videos'),
  )

  def parse_start_url(self,response):
    sel = Selector(response)
    pages = sel.xpath('//select[contains(@name,"sort")]/option/@value').extract()
    if len(pages) > 0 :
      for page in pages:
        yield Request(page)
    else:
      yield Request(response.url)

  def get_images_videos(self,response):
    sel = Selector(response)
    images = sel.xpath('//div[contains(@class,"media")]/div[contains(@class,"see-more")]/a/span[contains(@class,"Vids")]/../@href').extract()
    images_url = urljoin(response.url,images[0]) if len(images) > 0 else None

    videos = sel.xpath('//div[contains(@class,"media")]/div[contains(@class,"see-more")]/a[contains(text(),"videos")]/@href').extract()
    videos_url = urljoin(response.url,videos[0]) if len(videos) > 0 else None

    movie_url = response.url
    if images_url != None:
      images_url = images_url+"?&refine=poster"
      yield Request(images_url,meta={"videos_url":videos_url, 'movie_url':movie_url},callback=self.get_all_images)

  def get_all_images(self,response):
    sel = Selector(response)
    images = sel.xpath('//div[contains(@id,media)]/a/img/@src').extract()
    images = map(lambda s: s.replace('V1_SX100_CR0,0,100,100_.jpg','V1_SX640_SY720_.jpg'), images)
    images = '\n'.join(images)
    videos_url = response.request.meta['videos_url']
    movie_url = response.request.meta['movie_url']

    if videos_url != None:
      yield Request(videos_url,meta = {'images':images,'movie_url':movie_url},callback=self.get_all_videos)
    else:
      yield Request(movie_url,meta = {'images':images,'videos':''},callback=self.parse_movie)

  def get_all_videos(self,response):
    sel = Selector(response)
    videos = sel.xpath('//div[@id="main"]/div/ol/li//div/a/@href').extract()
    videos = map(lambda s: urljoin(response.url,s),videos)
    videos = '\n'.join(videos)
    images = response.request.meta['images']
    movie_url = response.request.meta['movie_url']
    yield Request(movie_url,meta={'images':images,'videos':videos},callback=self.parse_movie,dont_filter=True)


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
    item = IMDBMovie()
    item['posters'] = response.request.meta['images'].split('\n')
    item['videos'] = response.request.meta['videos'].split('\n')

    names = sel.xpath('//h1/span[@itemprop="name"]/text()').extract()
    item['film_name'] = names[0] if len(names) > 0 else ''
    item['original_name'] = names[1] if len(names) > 1 else ''

    item['imdb_id'] = response.url.split('/')[-2]

    also_knows_as = ''.join(sel.xpath('//div[@class="txt-block"]/*[contains(text(),"Also Known")]/../text()[2]').extract()).strip()
    also_knows_as_link = sel.xpath('//div[@class="txt-block"]/*[contains(text(),"Also Known")]/..//a/@href').extract()
    also_knows_as_link = map(lambda s:urljoin(response.url,s),also_knows_as_link)
    item['also_known_as'] = {"main":also_knows_as,"link":also_knows_as_link}

    dur = sel.xpath('normalize-space(//div[@class="infobar"]/time[@itemprop="duration"]/text())').extract()
    item['duration'] = dur[0] if len(dur) > 0 else ''
    classi = sel.xpath('//div[@class="infobar"]/span[contains(@itemprop,"Rating")]/@content').extract()
    item['classification'] = classi[0] if len(classi) > 0 else ''
    item['genere'] = sel.xpath('//div[@class="infobar"]/a[contains(@href,"genre")]/span/text()').extract()

    release = sel.xpath('//div[@class="infobar"]/span[@class="nobr"]/a/text()').extract()
    item['release_date'] = release[0]
    item['release_country'] = re.findall(r'\((.*)\)',release[1])[0]
    url = sel.xpath('//div[@class="infobar"]/span[@class="nobr"]/a/@href').extract()
    item['release_countries_link'] = urljoin(response.url,url[0]) if len(url) > 0 else ''

    par_guide = sel.xpath('//div[@class="txt-block"]/*[contains(text(),"Parents")]/../span/a/@href').extract()
    item['parent_guide'] = urljoin(response.url,par_guide[0]) if len(par_guide) > 0 else ''

    rating = sel.xpath('//div[@class="star-box-details"]/strong//span[contains(@itemprop,"rating")]/text()').extract()
    item['imdb_rating'] = rating[0] if len(rating) > 0 else ''
    num_of_users_rated = sel.xpath('//div[@class="star-box-details"]/a/span[contains(@itemprop,"rating")]/text()').extract()
    item['num_user_rated'] = num_of_users_rated[0].replace(',','').strip() if len(num_of_users_rated) > 0 else ''

    metascore = sel.xpath('//div[@itemprop="aggregateRating"]/a[contains(@href,"critic") and contains(text(),"100")]/text()').extract()
    item['metascore'] = metascore[0].strip() if len(metascore) > 0 else ''
    users_num = sel.xpath('//div[@itemprop="aggregateRating"]/a[contains(@href,"reviews") and contains(@title,"user")]/*/text()').extract()
    users_num = users_num[0].replace('user','').replace(',','').strip() if len(users_num) > 0 else ''
    users_link = sel.xpath('//div[@itemprop="aggregateRating"]/a[contains(@href,"reviews") and contains(@title,"user")]/@href').extract() 
    users_link = urljoin(response.url,users_link[0]) if len(users_link) > 0 else ''

    critic_num = sel.xpath('//div[@itemprop="aggregateRating"]/a[contains(@href,"reviews") and contains(@title,"critic")]/*/text()').extract()
    critic_num = critic_num[0].replace('critic','').replace(',','').strip() if len(critic_num) > 0 else ''
    critic_link = sel.xpath('//div[@itemprop="aggregateRating"]/a[contains(@href,"externalreviews") and contains(@title,"critic")]/@href').extract()
    critic_link = urljoin(response.url,critic_link[0]) if len(critic_link) > 0 else ''

    excerpts_link = sel.xpath('//div[@itemprop="aggregateRating"]/a[contains(@href,"criticreviews") and contains(@title,"critic") and not(contains(text(),"100") ) ]/@href').extract()
    excerpts_link = urljoin(response.url,excerpts_link[0]) if len(excerpts_link) > 0 else ''

    excerpts_num = sel.xpath('//div[@itemprop="aggregateRating"]/a[contains(@href,"criticreviews") and contains(@title,"critic") and not(contains(text(),"100") ) ]/text()').extract()
    excerpts_num = excerpts_num[0].replace(',','').strip() if len(excerpts_num) > 0 else ''

    item['metacritic_reviews'] = {'users':{'num':users_num,'link':users_link},'critic':{'num':critic_num,'link':critic_link},'excerpts':{'num':excerpts_num,'link':excerpts_link}}

    item['description'] = ''.join(sel.xpath('//p[@itemprop="description"]/text()').extract())
    item['story_line'] = ''.join(sel.xpath('//div[@id="titleStoryLine"]/div[@itemprop="description"]/p/text()').extract())

    directors_name = sel.xpath('//div[@itemprop="director"]/a/span/text()').extract()
    directors_link = sel.xpath('//div[@itemprop="director"]/a/@href').extract()
    directors_link = map(lambda s:urljoin(response.url,s),directors_link)

    item['directors'] = self.gen_double_list("name",directors_name,"link",directors_link)

    writers_name = sel.xpath('//div[@itemprop="creator"]/a/span/text()').extract()
    writers_link = sel.xpath('//div[@itemprop="creator"]/a/@href').extract()
    writers_link = map(lambda s: urljoin(response.url,s),writers_link)

    item['writers'] = self.gen_double_list("name",directors_name,"link",directors_link)

    cast_name = sel.xpath('//table[@class="cast_list"]//tr/td[@itemprop="actor"]/a/span/text()').extract()
    cast_link = sel.xpath('//table[@class="cast_list"]//tr/td[@itemprop="actor"]/a/@href').extract()
    cast_link = map(lambda s:urljoin(response.url,s),cast_link)
    item['cast'] = self.gen_double_list("name",cast_name,"link",cast_link)

    item['url'] = response.url

    taglines = sel.xpath('//div[@class="txt-block"]/*[contains(text(),"Tag")]/../text()').extract()
    if len(taglines) > 0 :
      taglines_url = sel.xpath('//ul[@class="quicklinks"]/li/a[contains(@href,"taglines")]/@href').extract()
      item['taglines'] = {"name":taglines[1],"link":urljoin(response.url,taglines_url[0])}

    summary = sel.xpath('//div[@id="titleStoryLine"]/span[contains(@class,"see-more")]/a[contains(text(),"Summary")]/@href').extract()

    item['plot_summary'] = urljoin(response.url,summary[0]) if len(summary) > 0  else ''

    synopsis = sel.xpath('//div[@id="titleStoryLine"]/span[contains(@class,"see-more")]/a[contains(text(),"Synopsis")]/@href').extract()

    item['plot_synopsis'] = urljoin(response.url,synopsis[0]) if len(synopsis) > 0 else ''

    item['plot_keywords'] = sel.xpath('//div[@itemprop="keywords"]/a/span/text()').extract()
    keywords_link = sel.xpath('//div[@itemprop="keywords"]/*/a/@href').extract()
    item['plot_keywords_link'] = urljoin(response.url,keywords_link[0]) if len(keywords_link) > 0 else ''
    item['job_id'] = os.getenv('SCRAPY_JOB', "crawler")

    return item