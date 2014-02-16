# -*- coding: utf-8 -*- 
from imdb_movies import imdbSpider
from scrapy.contrib.spiders import Rule
from scrapy.http import Request
from scrapy.selector import Selector
from urlparse import urljoin

class BatmanImdbMovie(imdbSpider):
  name = "batman_imdb_movie"
  domain_name = "imdb.com"
  CONCURRENT_REQUESTS = 1

  """
    USAGE:
    scrapy crawl batman_imdb_movies 
  """
  start_urls = ["http://www.imdb.com/title/tt0468569"]
  rules = ()

  def parse(self, response):
    yield Request(response.url, callback=self.get_images_videos)


  def get_images_videos(self,response):
    sel = Selector(response)
    images = sel.xpath('//div[contains(@class,"media")]/div[contains(@class,"see-more")]/a/span[contains(@class,"Vids")]/../@href').extract()
    images_url = urljoin(response.url,images[0]) if len(images) > 0 else None

    videos = sel.xpath('//div[contains(@class,"media")]/div[contains(@class,"see-more")]/a[contains(text(),"video")]/@href').extract()
    videos_url = urljoin(response.url,videos[0]) if len(videos) > 0 else None

    movie_url = response.url
    print movie_url
    if images_url != None:
      images_url = images_url+"?&refine=poster"
      yield Request(images_url,meta={"videos_url":videos_url, 'movie_url':movie_url},callback=self.get_all_images)

  def get_all_images(self,response):
    sel = Selector(response)
    images = sel.xpath('//div[contains(@id,media)]/a/img/@src').extract()
    images = map(lambda s: s.replace('V1_SX100_CR0,0,100,100_.jpg','V1_SX640_SY720_.jpg'), images)
    images = '\n'.join(images)
    movie_url = response.request.meta['movie_url']
    yield Request(movie_url,meta = {'images':images,'movie_url':movie_url},callback=self.get_all_videos,dont_filter=True)

  def get_all_videos(self,response):
    sel = Selector(response)
    videos = 'http://www.youtube.com/watch?v=yQ5U8suTUw0'
    video_imgs = 'http://i1.ytimg.com/vi/yQ5U8suTUw0/mqdefault.jpg'
    images = response.request.meta['images']
    movie_url = response.request.meta['movie_url']
    yield Request(movie_url,meta={'images':images,'videos':videos, 'video_imgs': video_imgs},callback=super(BatmanImdbMovie, self).parse_movie,dont_filter=True)