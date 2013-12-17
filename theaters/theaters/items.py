from scrapy.item import Item, Field

class Theater(Item):
  name = Field()
  country = Field()
  options = Field()
  cin_id = Field()
  telephones = Field()

  address = Field()
  district = Field()
  city = Field()
  #separate city,country,address
  url = Field()
  #add url of google map location
  google_map = Field()
  #add rating and num of rated users
  rating = Field()
  rating_n = Field()
  #add number of screens
  screens = Field()
  #add link to rating stats
  rating_stats = Field()

  image = Field()
  job_id = Field()