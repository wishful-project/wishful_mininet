#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Wishful IEEE 802.11 example.
"""

from mininet.net import Mininet
from mininet.node import Controller,OVSKernelSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

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


def topology():

    "Create a network."
    net = Mininet( controller=Controller, link=TCLink, switch=OVSKernelSwitch )

    print "*** Creating nodes"
    sta1 = net.addStation( 'sta1', mac='00:00:00:00:00:02', ip='10.0.0.2/8' )
    sta2 = net.addStation( 'sta2', mac='00:00:00:00:00:03', ip='10.0.0.3/8' )
    ap1 = net.addBaseStation( 'ap1', ssid= 'new-ssid1', mode= 'g', channel= '1', position='15,50,0' )
    ap2 = net.addBaseStation( 'ap2', ssid= 'new-ssid2', mode= 'g', channel= '6', position='25,30,0' )
    c1 = net.addController( 'c1', controller=Controller )

    print "*** Creating links"
    net.addLink(ap1, ap2)
    net.addLink(ap1, sta1)
    net.addLink(ap1, sta2)

    print "*** Starting network"
    net.build()
    c1.start()
    ap1.start( [c1] )
    ap2.start( [c1] )

    ap1.cmd('ifconfig ap1-eth1 20.0.0.2/8')
    ap2.cmd('ifconfig ap2-eth1 20.0.0.3/8')

    print "*** Starting Wishful framework"
    folder = './examples/multiple_agents/'

    print "*** ... agents ..."
    agent1 = WishfulAgent(ap1, folder + 'wishful_simple_agent', folder + 'agent_config_1.yaml')
    agent2 = WishfulAgent(ap2, folder + 'wishful_simple_agent', folder + 'agent_config_2.yaml')
    agent1.start()
    agent2.start()

    print "*** ... controller ..."
    wf_ctrl = WishfulController(ap1, folder + 'wishful_simple_controller', folder + 'controller_config.yaml')
    wf_ctrl.start()

    print "*** Starting network"

    """uncomment to plot graph"""
    net.plotGraph(max_x=100, max_y=100)

    net.startMobility(startTime=0)
    net.mobility('sta1', 'start', time=0, position='10,45,0')
    net.mobility('sta1', 'stop', time=60, position='50,20,0')
    net.mobility('sta2', 'start', time=0, position='0,60,0')
    net.mobility('sta2', 'stop', time=60, position='30,10,0')
    net.stopMobility(stopTime=60)

    print "*** Running CLI"
    CLI( net )

    print "*** Stopping network"
    wf_ctrl.stop()    
    agent1.stop()
    agent2.stop()
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    topology()
