import pika
import sys,time
from utils import Configurable
import logging
log = logging.getLogger('multi_amqp')

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
    "exchanges" : { 
      # ======== Example =========
      #"basic" : { 
      #  "in" : {
      #    "exchange" : False,
      #    "type" : "fanout"
      #    },
      #  "out" : {
      #    "exchange" : False,
      #    "type" : "fanout"
      #    }
      #  } 
      }
    }
  }

class C():
  #dummy class for extending
  pass

class multi_amqp(Configurable):
  """ Multi-amqp works similar to auto_amqp with the difference that it can
  create multiple 'tubes' (input and output exchanges),
  the configuration therefore looks a bit different"""
  conn = None
  def __init__(self,MODULE_NAME='multi_amqp',config=None):
    self.NAME = MODULE_NAME
    newConfig = { MODULE_NAME : DEFAULT_CONFIG}
    Configurable.__init__(self,newConfig)
    self.load_conf(config)
    

  def create_connection(self):
    """ starts the connection the the AMQP Serve """
    if self.conn:
      raise Exception("Connection already open")
    cfg = self.config[self.NAME]['amqp']['connection']
    log.debug(str(cfg))
    self.conn = pika.AsyncoreConnection(pika.ConnectionParameters(
          credentials = pika.PlainCredentials(cfg['login'],cfg['password']), 
          heartbeat=cfg['heartbeat'],
          virtual_host=cfg['vhost'],
          port=cfg['port'],
          host=cfg['host'],
          ),reconnection_strategy=pika.SimpleReconnectionStrategy())
    self.channel = self.conn.channel()

    self.tubes = self._setup_tubes()
    return self.tubes

  def _setup_tubes(self):
    """ creates the in 'config' configured input and output """
    chan = self.channel
    ret = []
    print self.config[self.NAME]['amqp']['exchanges']
    for k,v in self.config[self.NAME]['amqp']['exchanges'].items():
      o = C()
      inp = v['in']  if 'in' in v else None
      out = v['out'] if 'out' in v  else None
      o.name = k
      print str(k),str(inp),str(out)
      if inp and inp['exchange']:
        log.info('generating Input Queue'+ str(inp))
        inp['type'] = inp['type'] if 'type' in inp else 'fanout'
        chan.exchange_declare(**inp)
        o.qname = chan.queue_declare(exclusive=True).queue
        o.inp = inp['exchange']
        chan.queue_bind(exchange=inp['exchange'],queue=o.qname)
        o.consume = lambda cb,queue : chan.basic_consume(cb,queue=queue,no_ack=True)
        o.start_loop = lambda : pika.asyncore_loop()

      if out and out['exchange']:
        out['type'] = out['type'] if 'type' in out else 'fanout'
        log.info('generating Output Exchange'+ str(out))
        chan.exchange_declare(**out)
        o.out = out['exchange']
        o.publish = lambda msg,exchange: self.channel.basic_publish(exchange=exchange,routing_key='',body=msg)
      ret.append(o)
    print ret
    return ret

  def close_connection(self):
    self.conn.close()
    self.conn= None
    del self.tubes[:]

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
    conf = self.config[self.NAME]['amqp']['connection']
    conf['host'] = parsed.amqpHost if parsed.amqpHost else conf['host']
    conf['port'] = parsed.amqpPort if parsed.amqpPort else conf['port']
    conf['login'] = parsed.amqpUsername if parsed.amqpUsername else conf['login']
    conf['password'] = parsed.amqpPassword if parsed.amqpPassword else conf['password']
    conf['heartbeat'] = parsed.amqpHeartbeat if parsed.amqpHeartbeat in dir(parsed) else conf['heartbeat']
    conf['vhost'] = parsed.amqpVhost if parsed.amqpVhost else conf['vhost']


