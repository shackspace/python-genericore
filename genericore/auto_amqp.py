import pika
import sys,time
from utils import Configurable
import logging
log = logging.getLogger('genericore-amqp')

DEFAULT_CONFIG = {
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

class auto_amqp(Configurable):
  conn = None
  def __init__(self,config=None):
    Configurable.__init__(self,DEFAULT_CONFIG)
    self.load_conf(config)

  def create_connection(self):
    """ starts the connection the the AMQP Serve """
    if self.conn:
      raise Exception("Connection already open")
    cfg = self.config['connection']
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
    inp = self.config['in']
    out = self.config['out']
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
