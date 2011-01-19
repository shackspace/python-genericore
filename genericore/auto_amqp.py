import pika
import json, sys,time
import logging
log = logging.getLogger('genericore-amqp')

DEFAULT_CONFIG = {
        "connection" : {
          "login" : "guest",
          "password" : "guest",
          "host" : "localhost",
          "port" : 5672,
          "heartbeat" : 0
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

class auto_amqp:
  conn = None
  config = DEFAULT_CONFIG
  def __init__(self,config=None):
    if config:
      self.load_conf(config)

  def load_conf(self,config):
    self.config.update(config)

  def load_conf_file(self,config_file):
    with open(config_file) as f:
      new_conf = json.load(f)
      self.load_conf(new_conf["genericore"])

  def create_connection(self):
    if self.connection:
      raise Exception("Connection already open")
    log.debug (self.config['connection'])
    locals.update(self.config['connection'])
    self.conn = pika.AsyncoreConnection(pika.ConnectionParameters(
          credentials = pika.PlainCredentials(username,password), 
          heartbeat=heartbeat,
          virtual_host=vhost,
          port=port,
          host=host))
    self.channel = self.conn.channel()
    self._setup_tubes()

  def _setup_tubes(self):
    chan = self.channel
    inp = self.config['in']
    out = self.config['out']
    if inp['exchange']:
      chan.exchange_declare(**inp)
      self.qname = chan.queue_declare(exclusive=True).queue
      chan.queue_bind(exchange=inp['exchange'],queue=self.qname)
      self.consume = lambda cb : chan.basic_consume(cb,queue=self.qname,no_ack=True)
      self.start_loop = lambda : chan.asyncore_loop()

    if out['exchange']:
      chan.exchange_declare(**out)
      self.publish = lambda msg: chan.basic_publish(exchange=out['exchange'],routing_key='',body=msg)

  def close_connection(self):
    self.connection.close()
    self.connection = None
    #cleanup
    if hasattr(self,'consume'):
      delattr(self,'consume')
      delattr(self,'start_loo')
    if hasattr(self,'publish'):
      delattr(self,'publish')
