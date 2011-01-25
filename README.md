GENERICORE
==========
This is the python port of genericore, the generic information gathering
framework.

Disclamer
---------
The python-genericore and it's submodules are currently under HEAVY 
development and may suck balls in the current state. I appologize for that.

Submodules
==========
Currently the python implementation has the following submodules

* utils.py - a number of functions which define "common patterns" in all
  genericore plugins (e.g. commandline parser or unique-id generator)
* 

Configurator
------------
python-genericore provides a extensive configuration submodule whichs
allows the modules to evaluate/mix and merge configuration files.

The class *Configurable* provides a basic functionality to load
configuration into the variable _config_ via load\_conf. this can be used
to merge two configurations.

In addition to that there is a *Configurator* class which provides basic
functionality for parsing defaults. please see main.py of mail\_proc how to
use these two. 

configure your own class
------------
python-genericore provides the Configurator class which can be instanciated
in order to do all your nasty configuration and argument parsing stuff.

In order to configure YOUR Object object you may want to do the following
things:
* derive your class from Configurable ( to have the load\_conf magic )
  a "config" member variable is now available with the config dictionary
* implement populate\_parser(parser)
  in this function you can add custom arguments to the command line parser
  (argparse is the weaopn of choice in Configurator)
* implement eval\_parser(args)
  do something with the then parsed arguments

These functions will be called by the Configurator when doing a configure
for a list of modules (including your's)


Dependencies
===========
* simplejson 
* pika

Install
===========
#clone this repository
$ sudo ./setup install

Usage
=========
Configurator
------------

This is what you normally want to do when writing a new genericore module:

    conf = gen.Configurator(PROTO_VERSION,DESCRIPTION)  
    amqp = gen.auto_amqp()   
    s = YourMagic()  

    conf.configure([amqp,s])    #set up parser and eval parsed stuff

    # start network connections, probably also for your Parser (e.g. backend)
    amqp.create_connection()

    def cb (ch,method,header,body):
      entry = s.process(json.loads(body))
      amqp.publish(json.dumps(entry))

    amqp.consume(cb)
    amqp.start_loop()

MongoConnect
------------
You can derive YourMagic from the MongoConnect class for having a fresh
database connection AND all the parser magic included. It looks like this:

    MODULE_NAME = 'mail_proc'

    MODULE_NAME='YourMagic'
    DEFAULT_CONFIG = {
      MODULE_NAME : {
        "database" : {
          "collection" : "magic"
        }
      }
    }

    class YourMagic(MongoConnect): #MongoConnect derives from Configurable!
      
      def __init__(self,conf=None):
        MongoConnect.__init__(self,MODULE_NAME,DEFAULT_CONFIG)
        self.load_conf(conf)

      def process(self,mail):
        #insert your magic here
        return reply

      def populate_parser(self,parser): 
        MongoConnect.populate_parser(self,parser)
        # your configuration

      def eval_parser(self,parsed): 
        MongoConnect.eval_parser(self,parsed)
        # your config evaulation


