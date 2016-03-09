"""
Wishful Mininet integration
"""

__author__ = "Zubow"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{zubow}@tkn.tu-berlin.de"


class WishfulNode( object ):
    """A Wishful node is either a Wishful agent or controller."""

    def __init__( self, network_node, script, config, verbose, logfile ):
        self.network_node = network_node
        self.script = script
        self.config = config
        self.verbose = verbose
        self.logfile = logfile
        self.ctrl_ip = '127.0.0.1'
        self.ctrl_dl_port = 8989
        self.ctrl_ul_port = 8990

    def start( self ):
        """Start agent or controller.
           Log to /tmp/*.log"""

        if self.verbose:
            verbose_str = '--verbose'
        else:
            verbose_str = ''
        # exec on network node
        self.network_node.cmd( self.script + ' ' + verbose_str + ' --logfile ' + self.logfile + 
		' --config ' + self.config + ' &' )
        self.execed = False

    def stop( self ):
        "Stop controller."
        self.network_node.cmd( 'kill %' + self.script )
        self.network_node.cmd( 'wait %' + self.script )

    def checkListening( self ):
        "Make sure no controllers are running on our port"
        # Verify that Telnet is installed first:
        out, _err, returnCode = errRun( "which telnet" )
        if 'telnet' not in out or returnCode != 0:
            raise Exception( "Error running telnet to check for listening "
                             "controllers; please check that it is "
                             "installed." )
        listening = self.cmd( "echo A | telnet -e A %s %d" %
                              ( self.ctrl_ip, self.ctrl_dl_port ) )
        if 'Connected' in listening:
            servers = self.cmd( 'netstat -natp' ).split( '\n' )
            pstr = ':%d ' % self.ctrl_dl_port
            clist = servers[ 0:1 ] + [ s for s in servers if pstr in s ]
            raise Exception( "Please shut down the controller which is"
                                     " running on port %d:\n" % self.ctrl_dl_port +
                                     '\n'.join( clist ) )


class WishfulAgent( WishfulNode ):
    """The Wishful agent which is running on each wireless node to be controlled."""

    def __init__( self, network_node, script, config, verbose=False, logfile=None ):
	if logfile is None:
	    logfile = '/tmp/agent_' + network_node.name + '.log'
        WishfulNode.__init__( self, network_node, script, config, verbose, logfile )
        #self.checkListening()

    def start( self ):
        print "Start Wishful agent."
	WishfulNode.start(self)

    def stop( self ):
        print "Stop Wishful agent."
	WishfulNode.stop(self)

class WishfulController( WishfulNode ):
    """The Wishful controller which is communicating with Wishful agents in order to control wireless nodes."""

    def __init__( self, network_node, script, config, verbose=False, logfile=None ):
	if logfile is None:
	    logfile = '/tmp/controller_' + network_node.name + '.log'
        WishfulNode.__init__( self, network_node, script, config, verbose, logfile )
        #self.checkListening()

    def start( self ):
        print "Start Wishful controller."
	WishfulNode.start(self)

    def stop( self ):
        print "Stop Wishful controller."
	WishfulNode.stop(self)

