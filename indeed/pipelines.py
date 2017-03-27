# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import sys
import pymongo

from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log 

class IndeedPipeline(object):
    def process_item(self, item, spider):
    
        i = item['summary'][0]
        # i = remove_tags(i)
        # i = replace_escape_chars(i)
        item['summary'][0] = i

        i = item['job_title'][0]
        # i = remove_tags(i)
        # i = replace_escape_chars(i)
        item['job_title'][0] = i

        i = item['company'][0]
        # i = remove_tags(i)
        # i = replace_escape_chars(i)
        item['company'][0] = i.strip()
        
        return item

class MongoDBPipeline(object):
    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_URL'],
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
    
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            check=self.collection.find_one({"job_key" : item['job_key']})
            print(check)
            if not check:
                self.collection.insert(dict(item))
                log.msg("Question added to MongoDB database!",
                    level=log.DEBUG, spider=spider)
            else:
                print ("item already exist")
        return item

