# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class IMDBMovie(Item):
  film_name = Field()
  original_name = Field()
  
  imdb_id = Field()
  also_known_as = Field()


  duration = Field()
  classification = Field()

  parent_guide = Field()

  genere = Field()
  release_date = Field()
  release_country= Field()
  release_countries_link = Field()

  plot_summary = Field()
  plot_synopsis = Field()
  plot_keywords = Field()
  plot_keywords_link = Field()

  imdb_rating = Field()
  num_user_rated = Field()
  metacritic_reviews = Field()
  metascore = Field()


  description = Field()
  story_line = Field()

  directors = Field()
  writers = Field()
  cast = Field()
  posters = Field()
  videos = Field()
  taglines = Field()
  url = Field()