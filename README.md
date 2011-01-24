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
  * parse\_default (argparse ) : adds default parser parameters
  * generate\_unique (VERSION, config) : generates a unique id from the
    Version number of the script and the configuration given
* auto\_amqp.py - the amqp connector class which provides the following
  functions:
  * load\_conf(dict) - loads and merges configuration from the given dictionary

  * load\_conf\_file(fname) - loads and merges configuration directly from a file

  * create\_connection() - starts the connection the the AMQP Server

  * [internal] \_setup\_tubes() - creates the in 'config' configured input and output
    queues/exchanges. will be called by create_connection
    in addition it registers the following functions if input exchange is
    defined:
    * consume (callback) - calls amqp's basic\_consume with the correct
      params
    * start\_loop () - calls asyncore\_loop()
    the following function is registered if the output exchange is defined
    * publish (msg) - sends a message to the output exchange

  * close\_connection () - closes all connections, cleans up the object
  In addition to that, auto\_amqp.py needs to hold a "default parameter"
  list called DEFAULT\_CONFIG. 

Configurator
===========

python-genericore provides a extensive configuration submodule whichs
allows the modules to evaluate/mix and merge configuration files.

The class *Configurable* provides a basic functionality to load
configuration into the variable _config_ via load\_conf. this can be used
to merge two configurations.

In addition to that there is a *Configurator* class which provides basic
functionality for parsing defaults. please see main.py of mail\_proc how to
use these two. 


Dependencies
===========
* simplejson 
* pika
