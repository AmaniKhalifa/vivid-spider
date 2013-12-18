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

class Video(Item):
    image = Field()
    video_name = Field()
    actors = Field()
    directors = Field()
    synopsis = Field()
    album_format = Field()
    number_of_disks = Field()
    language = Field()
    subtitles = Field()
    parental_guidance = Field()
    studio = Field()
    dvd_release_date = Field()
    run_time = Field()
    genre = Field()
    description = Field()
    url = Field()