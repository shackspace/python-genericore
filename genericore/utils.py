#parses all "default" parser values with argparse

import argparse

def parse_default(parser):
  parser.add_argument('-s','--host',default='141.31.8.11',      help='AMQP host ip address')
  parser.add_argument('--port',type=int,default=5672,      help='AMQP host port')
  parser.add_argument('-u','--username',default='shack',   help='AMQP username') 
  parser.add_argument('-p','--password',default='guest',   help='AMQP password') 
  parser.add_argument('-b','--heartbeat',type=int,default=0,help='AMQP Heartbeat value') 
  parser.add_argument('-v','--vhost',default='/',help='AMQP vhost definition') 
  parser.add_argument('-d','--debug_level',default='/',help='AMQP vhost definition') 
