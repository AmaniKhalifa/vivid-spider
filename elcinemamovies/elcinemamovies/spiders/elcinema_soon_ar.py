# -*- coding: utf-8 -*- 
from elcinema_soon import ElcinemaSoonSpider
from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

class ElcinemaSoonSpiderAR(ElcinemaSoonSpider):
  name = "elcinema_soon_ar"
  domain_name = "elcinema.com"
  CONCURRENT_REQUESTS = 1

  """
    USAGE : scrapy crawl elcinema_soon
    only for eg
  """

  start_urls = ["http://www.elcinema.com/ar/soon/"]

  country = 'eg'
  rules = (
    #pagination
    Rule(SgmlLinkExtractor(allow=('/\d+'),restrict_xpaths=('//div[contains(@class,"pagination")]/ul/li'), unique=True), follow=True),
    #Movies
    Rule(SgmlLinkExtractor(restrict_xpaths=('//div[@class="row"]/div//span/a'), unique=True), follow=True,callback='start'),
  )
  site_language = "ar"