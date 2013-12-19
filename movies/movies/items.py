# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class imdb_movie(Item):
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



class DVD(Item):
    i = Field()
    #virginmegastore


class TVshow(Item):
    i = Field()
    #imdb

