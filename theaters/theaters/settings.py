# Scrapy settings for movies project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'theaters'
#comment log level in case of debugging
LOG_LEVEL = "WARNING"

SPIDER_MODULES = ['theaters.spiders']
NEWSPIDER_MODULE = 'theaters.spiders'

ITEM_PIPELINES = {
  'theaters.pipelines.MoviesPipeline':100,
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'movies (+http://www.yourdomain.com)'
