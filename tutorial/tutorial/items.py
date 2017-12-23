# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy

class AmazonItem(scrapy.Item):
#    {"actors", "directors", "producers", "writers", "language", "number_of_discs", "number_of_tapes", "rated", "studio", "dvd_release_date", "run_time", "average_rating"}
    genres = scrapy.Field()
    studio = scrapy.Field()
    director = scrapy.Field()
    starring = scrapy.Field()
    supporting_actors = scrapy.Field()
    mpaa_rating = scrapy.Field()
    desc = scrapy.Field()
    runtime = scrapy.Field()
    
    producers = scrapy.Field()
    writers = scrapy.Field()
    language = scrapy.Field()
    number_of_discs = scrapy.Field()
    number_of_tapes = scrapy.Field()
    dvd_release_date = scrapy.Field()
    average_rating = scrapy.Field()
    ptype = scrapy.Field()
    oid = scrapy.Field()