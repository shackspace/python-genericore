
import logging, sys
from utils import Configurable
from pymongo import Connection
log = logging.getLogger('MongoConnect')


# this is the "sub-configuration" of the given module name
GENERIC_CONFIG = {
    "mongodb" : {
      "host" : "localhost",
    },
    "database" : {
      "database" : "genericore",
      "collection" : "generic",
      "drop_collection" : False
    }
}
class MongoConnect(Configurable):

  def create_connection(self): 
    """ Will create a connection to the mongodb and, if wanted by user
    ('drop_collection' in config is set True) clean up the database,
    clean up the collection 
    will set following member variables:
    conn - the connection to the database
    db   - the open database in the mongodb
    coll - the open collection (similar to table in relational db)
    """
    conf = self.config[self.MODULE_NAME]
    dconf = conf['database']
    try:
      self.conn = Connection(**conf['mongodb'])

      self.db = self.conn[dconf['database']]
      self.coll = self.db[dconf['collection']]
    except Exception as e:
      log.error('Mongodb not running or unreachable ! Bailing out:\n' + str(e))
      sys.exit(0)
    print dconf
    if dconf['drop_collection'] : 
      log.info('dropping collection due to public demand')
      self.drop_collection()

  def drop_collection(self,collection=None):
    """ will drop a given collection (via collection name) from the open
    database object self.db --> delete all data from collection """
    if not collection:
      self.coll.drop()
    else:
      self.db[collection].drop()

  def __init__(self,MODULE_NAME='mongo_connect',conf=None):
    self.MODULE_NAME = MODULE_NAME
    newConfig = {}
    newConfig[MODULE_NAME] = GENERIC_CONFIG # extend our config and
                                                 #personalize it
    Configurable.__init__(self,newConfig)
    self.load_conf(conf)

  def close(self): 
    self.conn.close()

  def populate_parser(self,parser): 
    parser.add_argument('--mongohost',metavar='HOST',help='Mongodb Host')
    parser.add_argument('--collection',metavar='PATH',help='Collection to save data in')
    parser.add_argument('--drop-collection',action='store_true',help='drops the collection after successful connection, then continues')

  def eval_parser(self,parsed): 
    conf = self.config[self.MODULE_NAME]
    mconf = conf['mongodb']
    dconf = conf['database']
    mconf['host'] = parsed.mongohost if parsed.mongohost else mconf['host']
    dconf['collection'] = parsed.collection if parsed.collection else dconf['collection']
    dconf['drop_collection'] = parsed.drop_collection
