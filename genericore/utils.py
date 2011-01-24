#parses all "default" parser values with argparse

import argparse,hashlib,sys
import logging
import simplejson as json #need to decode in ascii
log = logging.getLogger('genericore-utils')

class Configurable(object):
  config = {}

  def __init__(self,config=None):
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
      self.load_conf(new_conf)
    def load_conf_parser(self,parser):
      """ loads the configuration from a parser object """

class Configurator(Configurable):
  def __init__(self,PROTO_VERSION,conf=None):
    """ PROTO_VERSION is the protocol version of the module to configure """
    Configurable.__init__(self,conf)
    self.PROTO_VERSION = PROTO_VERSION

  def configure(self,conf_list):
    for i in conf_list:
      i.load_conf(self.config)
  def populate_parser(self,parser):
    parser.add_argument('-c','--config',dest='genConfig', help='configuration file',metavar='FILE') 
    #parser.add_argument('-d','--debug_level',help='Debug Level') 
    parser.add_argument('--unique-key',action='store_true',   help='Unique Key')

  def eval_parser(self,parsed):
    if 'genConfig' in dir(parsed):
      self.load_conf_file(parsed.genConfig)

    if 'unique-key' in dir(parsed):
      print self.generate_unique(parsed)
      sys.exit(0)

  def generate_unique(self,args):
      print(hashlib.sha1(str(self.PROTO_VERSION) + 
        json.dumps(args,sort_keys=True)).hexdigest())
