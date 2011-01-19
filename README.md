GENERICORE
==========
This is the python port of genericore, the generic information gathering
framework.

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
  * load\_conf(str) - loads and merges configuration from the given dictionary

  * load\_conf\_file(fname) - loads and merges configuration directly from a file

  * create\_connection() - starts the connection the the AMQP Server

  * [internal] \_setup\_tubes - creates the in 'config' configured input and output
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



Dependencies
===========
* simplejson 
* pika
