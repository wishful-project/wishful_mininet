"""
Wishful Mininet integration
"""

import logging
import os
import subprocess
import re

__author__ = "Zubow"
__copyright__ = "Copyright (c) 2016, Technische Universitaet Berlin"
__version__ = "0.1.0"
__email__ = "{zubow}@tkn.tu-berlin.de"


class WishfulNode( object ):
    """A Wishful node is either a Wishful agent or controller."""

    def __init__( self, network_node, config, logfile, verbose=False ):
        self.log = logging.getLogger("{module}.{name}".format(
            module=self.__class__.__module__, name=self.__class__.__name__))

        self.network_node = network_node
        self.config = config
        self.logfile = logfile
        if logfile is None:
            logfile = '/tmp/wishful_' + network_node.name + '.log'
        else:
            self.logfile = logfile

        self.verbose = verbose
        self.script = 'wishful-agent'

        print('Starting Wishful agent with config: %s and logfile: %s' % (self.config, self.logfile))

    def start( self ):
        """Start agent or controller.
           Log to /tmp/*.log"""

        # exec on network node
        try:
            if self.verbose:
                verbose_str = '-v'
            else:
                verbose_str = ''

            self.network_node.cmd( self.script + ' ' + verbose_str + ' --logfile ' + self.logfile + ' --config ' + self.config + ' &' )
            self.execed = False
        except Exception as e:
            print("{} !!!Exception!!!: {}".format(datetime.datetime.now(), e))

    def stop( self ):
        """Stop wishful node."""
        print('Stopping Wishful agent')
        self.network_node.cmd( 'kill %' + self.script )
        self.network_node.cmd( 'wait %' + self.script )

    def find_process( self, process_name ):
      ps = subprocess.Popen("ps -eaf | grep -v grep | grep " + process_name, shell=True, stdout=subprocess.PIPE)
      output = ps.stdout.read()
      ps.stdout.close()
      ps.wait()

      return output

    # This is the function you can use
    def check_is_running( self ):
      output = self.find_process( self.script )

      if re.search(self.script, output) is None:
        return False
      else:
        return True

    def read_log_file( self ):
        fid = open(self.logfile)
        content = fid.read()

        return content
