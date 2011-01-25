
import logging, sys
from utils import Configurable
from pymongo import Connection
log = logging.getLogger('MongoConnect')


# this is the "sub-configuration" of the given module name
GENERIC_CONFIG = {
    "mongodb" : {
      "host" : "localhost"
    },
    "collection" : {
      "name" : "mail_user_stats",
      "drop_collection" : False
    }
}
class MongoConnect(Configurable):

  def create_connection(self): 
    conf = self.config[self.MODULE_NAME]
    coll_conf = conf['collection']
    try:
      self.conn = Connection(**conf['mongodb'])
      self.db = self.conn[coll_conf['name']]
    except Exception as e:
      log.error('Mongodb not running or unreachable ! Bailing out' + str(e))
      sys.exit(0)

    if coll_conf ['drop_collection'] : 
      log.info('dropping collection due to public demand')
      self.db.drop()

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
    cconf = conf['collection']
    mconf['host'] = parsed.mongohost if parsed.mongohost else mconf['host']
    cconf['name'] = parsed.collection if parsed.collection else cconf['name']
    cconf['drop_collection'] = parsed.drop_collection
