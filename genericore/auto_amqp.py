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
  def __init__(self,config=None):
    Configurable.__init__(self,DEFAULT_CONFIG)
    self.load_conf(config)

  def create_connection(self):
    """ starts the connection the the AMQP Serve """
    if self.conn:
      raise Exception("Connection already open")
    cfg = self.config['amqp']['connection']
    log.debug (str(cfg))
    locals().update()
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
    inp = self.config['amqp']['in']
    out = self.config['amqp']['out']
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
      delattr(self,'start_loo')
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
    conf = self.config['amqp']['connection']
    conf['host'] = parsed.amqpHost if 'amqpHost' in dir(parsed) else conf['host']
    conf['port'] = parsed.amqpHost if 'amqpPort' in dir(parsed) else conf['port']
    conf['username'] = parsed.amqpHost if 'amqpUsername' in dir(parsed) else conf['username']
    conf['password'] = parsed.amqpHost if 'amqpPassword' in dir(parsed) else conf['password']
    conf['heartbeat'] = parsed.amqpHost if 'amqpHeartbeat' in dir(parsed) else conf['heartbeat']
    conf['vhost'] = parsed.amqpHost if 'amqpVhost' in dir(parsed) else conf['vhost']


