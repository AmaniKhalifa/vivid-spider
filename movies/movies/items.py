# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class Movie(Item):
    #add imdb id
    name = Field()
    #Also Known As: Gravedad See more  (and link)
    theaters = Field()

    duration = Field()
    #imdb
    classification = Field()

    #add link to parent_guide
    parent_guide = Field()

    genere = Field()
    release_date = Field()
    release_country = Field()
    #add link to Plot Summary | Plot Synopsis

    #link of all release dates

    #imdb
    imdb_rating = Field()
    #imdb
    num_user_rated = Field()
    #add all details 

    #elcinema
    elcinema_rating = Field()

    description = Field()
    story_line = Field()

    directors = Field()
    writers = Field()
    cast = Field()
    #add actor's link and actor's role name
    image_url = Field()
    #adding thumb and whole image and video
    #add all trailers 
    #add 10 images including all posters
    #add tagline
    url = Field()

class elcinema_movie(Item):
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

class Game(Item):
    i = Field()
    #virginmegastore
    #imdb
    #all from virgin

    #add certificate

class Album(Item):
    i = Field()
    #virginmegastore dubai
    #all
    #top tracks, pics, videos (links)
    #events upcoming events where and when 




    #pass

class DVD(Item):
    i = Field()
    #virginmegastore


class TVshow(Item):
    i = Field()
    #imdb

