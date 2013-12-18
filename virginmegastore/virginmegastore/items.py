from scrapy.item import Item, Field

class Album(Item):
    image = Field()
    album_name = Field()
    artist_name = Field()
    album_format = Field()
    original_release_date = Field()
    number_of_disks = Field()
    labels = Field()
    genre = Field()
    original_SKU = Field()
    tracks = Field()
    url = Field()

