#parses all "default" parser values with argparse

import argparse,hashlib,sys
import logging,copy
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
    self.config = copy.deepcopy(self.config)
    stack = [(self.config,new_config)]
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

class Configurator(Configurable):
  def __init__(self,PROTO_VERSION=1,DESCRIPTION='description not set!',conf=None):
    """ PROTO_VERSION is the protocol version of the module to configure """
    Configurable.__init__(self,conf)
    self.PROTO_VERSION = PROTO_VERSION
    self.DESCRIPTION = DESCRIPTION

  def configure(self,conf_list):
    """ configures all configurable objects with current config 

    Steps:
    1. load DEFAULT CONFIG (implicitly loaded when instanciating)
    2. load Config File (in eval_parser of self)
    3. load Parameters (in every eval_parser)

    Each step may overwrite already existing keys in config
    """
    parser = argparse.ArgumentParser(description=self.DESCRIPTION)

    self.populate_parser(parser)
    for configurable in conf_list:
      try: configurable.populate_parser(parser) 
      except Exception as e: print (str(configurable.__class__) + "does not have populate_parser" + str(e))

    args = parser.parse_args()

    self.eval_parser(args)
    for i in conf_list:
      try:
        i.load_conf(self.config)
        i.eval_parser(args)
      except Exception as e: print (str(i.__class__) + "does not have eval_parser or load_conf" + str(e))

    #self.blend(conf_list)
    #log.debug ('New Configuration:' + str(self.config))

  def _blend(self,conf_list):
    """ blends all configurations of all configurables into this object 
        WARNING: This function is considered harmful! DO NOT USE 
    """
    for i in conf_list:
      self.load_conf(i.config)

  def populate_parser(self,parser):
    parser.add_argument('-c','--config',dest='genConfig', help='configuration file',metavar='FILE') 
    parser.add_argument('-d','--debug',action='store_true',help='Debug Mode') 
    parser.add_argument('--unique-key',action='store_true',   help='Unique Key')

  def eval_parser(self,parsed):
    """ will evaluate the parsed values 
    genConfig   - eventually loads configuration file
    debug       - will set logging.basicConfig(logging.DEBUG) if debug is set
                  othewise default is logging.INFO
    unique_key  - will print the unique key of this module to stdout and
                  exits!
    """
    if parsed.genConfig:
      print 'loading file %s' % parsed.genConfig
      self.load_conf_file(parsed.genConfig)

    if parsed.unique_key:
      print self.generate_unique(parsed)
      sys.exit(0)

    if parsed.debug:
      logging.basicConfig(level=logging.DEBUG)
    else:
      logging.basicConfig(level=logging.INFO)

  def generate_unique(self,args):
      return (hashlib.sha1(str(self.PROTO_VERSION) + 
        str(args)).hexdigest())
