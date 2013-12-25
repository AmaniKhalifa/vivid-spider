# Scrapy settings for music project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'virginmegastore'
#comment log level in case of debugging
LOG_LEVEL = "WARNING"

SPIDER_MODULES = ['virginmegastore.spiders']
NEWSPIDER_MODULE = 'virginmegastore.spiders'


#ITEM_PIPELINES = {
#  'virginmegastore.pipelines.VirginMegaStorePipeline':100,
#}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'movies (+http://www.yourdomain.com)'
ITEM_PIPELINES = {
  'scrapy_mongodb.MongoDBPipeline': 900,
}

#ITEM_PIPELINES = {
#  'elcinemamovies.pipelines.MoviesPipeline':100,
#}

MONGODB_URI = 'mongodb://localhost:27017'
MONGODB_DATABASE = 'scrapy'
MONGODB_COLLECTION = 'virgin_megastore_products'