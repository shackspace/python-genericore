import pika
import sys,time
from utils import Configurable
import logging
log = logging.getLogger('genericore-amqp')

DEFAULT_CONFIG = {
    "amqp" : {
        "connection" : {
          "login" : "guest",
          "password" : "guest",
          "host" : "localhost",
          "port" : 5672,
          "heartbeat" : 0,
          "vhost" : "/"
          },
        "in" : {
          "exchange" : False,
          "type" : "fanout",
        },
        "out" : {
          "exchange" : False,
          "type" : "fanout",
        }
      }
    }

class auto_amqp(Configurable):
  conn = None
  def __init__(self,MODULE_NAME='auto_amqp',config=None):
    """ constructor if auto_amqp
    MODULE_NAME is important to distinguish the namespaces for the
    different Objects"""
    newConfig = {}
    newConfig[MODULE_NAME] = DEFAULT_CONFIG
    Configurable.__init__(self)
    self.load_conf(config)
    self.MODULE_NAME = MODULE_NAME
    

  def create_connection(self):
    """ starts the connection the the AMQP Serve """
    if self.conn:
      raise Exception("Connection already open")
    cfg = self.config[self.MODULE_NAME]['amqp']['connection']
    log.debug(str(cfg))
    self.conn = pika.AsyncoreConnection(pika.ConnectionParameters(
          credentials = pika.PlainCredentials(cfg['login'],cfg['password']), 
          heartbeat=cfg['heartbeat'],
          virtual_host=cfg['vhost'],
          port=cfg['port'],
          host=cfg['host']))
    self.channel = self.conn.channel()

    self._setup_tubes()

  def _setup_tubes(self):
    """ creates the in 'config' configured input and output """
    chan = self.channel
    inp = self.config[self.MODULE_NAME]['amqp']['in']
    out = self.config[self.MODULE_NAME]['amqp']['out']
    if inp['exchange']:
      log.info('generating Input Queue'+ str(inp))
      chan.exchange_declare(**inp)
      self.qname = chan.queue_declare(exclusive=True).queue
      chan.queue_bind(exchange=inp['exchange'],queue=self.qname)
      self.consume = lambda cb : chan.basic_consume(cb,queue=self.qname,no_ack=True)
      self.start_loop = lambda : pika.asyncore_loop()

    if out['exchange']:
      log.info('generating Output Exchange'+ str(out))
      chan.exchange_declare(**out)
      self.publish = lambda msg: self.channel.basic_publish(exchange=out['exchange'],routing_key='',body=msg)

  def close_connection(self):
    self.conn.close()
    self.conn= None
    #cleanup
    if hasattr(self,'consume'):
      delattr(self,'consume')
      delattr(self,'start_loop')
    if hasattr(self,'publish'):
      delattr(self,'publish')

  def populate_parser(self,parser):
    """ populates an argparse parser """
    parser.add_argument('-s','--host',dest='amqpHost', help='AMQP host ip address',metavar='HOST')
    parser.add_argument('--port',type=int,dest='amqpPort',help='AMQP host port',metavar='PORT') 
    parser.add_argument('-u','--username',dest='amqpUsername', help='AMQP username',metavar='USER') 
    parser.add_argument('-p','--password',dest='amqpPassword',help='AMQP password',metavar='PASS') 
    parser.add_argument('-b','--heartbeat',dest='amqpHeartbeat',type=int,help='AMQP Heartbeat value',metavar='SECONDS') 
    parser.add_argument('-v','--vhost',dest='amqpVhost',help='AMQP vhost definition',metavar='VHOST') 
  def eval_parser(self,parsed):
    """ loads its individual configuration from the parsed output """
    conf = self.config[self.MODULE_NAME]['amqp']['connection']
    conf['host'] = parsed.amqpHost if parsed.amqpHost else conf['host']
    conf['port'] = parsed.amqpPort if parsed.amqpPort else conf['port']
    conf['login'] = parsed.amqpUsername if parsed.amqpUsername else conf['login']
    conf['password'] = parsed.amqpPassword if parsed.amqpPassword else conf['password']
    conf['heartbeat'] = parsed.amqpHeartbeat if parsed.amqpHeartbeat in dir(parsed) else conf['heartbeat']
    conf['vhost'] = parsed.amqpVhost if parsed.amqpVhost else conf['vhost']


