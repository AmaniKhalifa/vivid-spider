# Scrapy settings for movies project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'imdbmovies'
#comment log level in case of debugging
LOG_LEVEL = "WARNING"

SPIDER_MODULES = ['imdbmovies.spiders']
NEWSPIDER_MODULE = 'imdbmovies.spiders'


#ITEM_PIPELINES = {
#  'imdbmovies.pipelines.MoviesPipeline':100,
#}

ITEM_PIPELINES = {
  'scrapy_mongodb.MongoDBPipeline': 900,
}

MONGODB_URI = 'mongodb://localhost:27017'
MONGODB_DATABASE = 'scrapy'
MONGODB_COLLECTION = 'imdb_movies'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'movies (+http://www.yourdomain.com)'
