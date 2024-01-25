import pymongo
from dotenv import dotenv_values

config = dotenv_values('.env')

class MongoTibiaDB(object):
    URI = config['CONNECTION_STRING'] + 'market'
    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(MongoTibiaDB.URI, tls=True,  tlsAllowInvalidCertificates=True)
        MongoTibiaDB.DATABASE = client['market']
    
    @staticmethod
    def insert(collection, data):
        MongoTibiaDB.DATABASE[collection].insert_one(data)

    @staticmethod
    def find(collection, query):
        return MongoTibiaDB.DATABASE[collection].find(query)
    
    @staticmethod
    def find_one(collection, query):
        return MongoTibiaDB.DATABASE[collection].find_one(query)
