#parses all "default" parser values with argparse

import argparse,hashlib
import logging
import simplejson as json #need to decode in ascii
log = logging.getLogger('genericore-utils')
def parse_default(parser):
  parser.add_argument('-s','--host',default='141.31.8.11',      help='AMQP host ip address')
  parser.add_argument('--port',type=int,default=5672,      help='AMQP host port')
  parser.add_argument('-u','--username',default='shack',   help='AMQP username') 
  parser.add_argument('-c','--config',default='',   help='configuration file') 
  parser.add_argument('-p','--password',default='guest',   help='AMQP password') 
  parser.add_argument('-b','--heartbeat',type=int,default=0,help='AMQP Heartbeat value') 
  parser.add_argument('-v','--vhost',default='/',help='AMQP vhost definition') 
  parser.add_argument('-d','--debug_level',default='/',help='AMQP vhost definition') 
  parser.add_argument('--unique-key',action='store_true',   help='Unique Key')

def generate_unique(PROTO_VERSION,args):
  return hashlib.sha1(str(PROTO_VERSION) + 
      json.dumps(args,sort_keys=True)).hexdigest()

class Configurable(object):
  config = {}

  def __init__(self,config=None):
    if config:
      self.load_conf(config)

  def load_conf(self,new_config):
    """ loads and merges configuration from the given dictionary """
    if not new_config:
      return
    stack = [(self.config, new_config)]
    while stack:
      current_dst, current_src = stack.pop()
      for key in current_src:
        if key not in current_dst:
          current_dst[key] = current_src[key]
        else:
          if isinstance(current_src[key], dict) and isinstance(current_dst[key], dict) :
            stack.append((current_dst[key], current_src[key]))
          else:
            current_dst[key] = current_src[key]

  def load_conf_file(self,config_file):
    """ loads and merges configuration directly from a file """
    if not config_file :
      log.debug('config file is empty')
      return
    with open(config_file) as f:
      new_conf = json.load(f,encoding='ascii')
      self.load_conf(new_conf["genericore"])
