# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class ElcinemaMovie(Item):
  film_name = Field()
  theaters = Field()
  duration = Field()
  genere = Field()
  country = Field()
  release_countries_dates = Field()
  elcinema_rating = Field()
  elcinema_rating_link = Field()
  description = Field()
  directors = Field()
  writers = Field()
  cast = Field()
  thumbnail_url = Field()
  image_urls = Field()
  videos = Field()
  url = Field()
  job_id = Field()