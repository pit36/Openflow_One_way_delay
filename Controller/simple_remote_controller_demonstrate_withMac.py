from ryu.base import app_manager
from ryu import utils
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, HANDSHAKE_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, arp, ethernet, ipv4, ipv6,ether_types
from ryu.topology import event
from ryu.topology.api import get_switch, get_link
from ryu.lib import mac, hub
from ryu.lib import mac, ip
from ryu.app.wsgi import ControllerBase
from collections import defaultdict

#from threading import start_new_thread
import os
import random
import datetime
import time
import restDB
import matrix_np
import struct as pc
import binascii
import paramiko
import subprocess
import json
import socket  # Import socket module
# const from routing
# Reference bandwidth = 1 Gbp/s
REFERENCE_BW = 10000000

# wichtung bw
DEFAULT_BW = 10000000

MAX_PATHS = 2

# For synchronisation
SWITCH_IP_1 = '172.31.1.101'
SWITCH_IP_2 = '172.31.1.102'

# For controller-switch connection
SWITCH_IP_1_2 = '10.0.1.2'
SWITCH_IP_2_2 = '10.0.2.2'

INTERFACE_1 = 'eth0'#'enxa0cec81d1262'
INTERFACE_2 = 'eth1'#'enxa0cec8200aaa'

# IP for the OpenVSwitches in between, IPs of the swithces
SWITCH_IP_1_inBetween = '10.0.0.1'
SWITCH_IP_2_inBetween = '10.0.0.2'

LOOPBACK_IP = "127.0.0.1"

IPERF_START_TIME = 20.0

# virtual -> mininet
MININET = False

# Normal = Just plot
# IPERF = Increasing Bandwith
# RTT = RTT Measurement
# CHANGINGLAT = latency changes
# CHANGINGLATCONTROLLER = latency changes
# CHANGINGLATTOSHOWDIFFERENCE = stairs up
# ONELONGTIME = one latency measurement

# IMPORTANT: While measurement, RTT is useless because only every second value is taken
TESTTYPE = 'Normal'

# ALL -> statisticrequest, echo + echoboth
# RTT -> statisticreq
# ECHORTT -> echo rtt
# ECHO -> updownmeaurement
# PORTSTATS -> only recieving portstats
MEASUREMENTTYPE = 'ECHORTT'

# If Web Interface should be included
WITH_WEB_INTERFACE = False

# If performance with socket also should be evaluated
WITH_SOCKET = False

# update rate in s
UPDATE_INTERVAL_CSW = 0.51
UPDATE_INTERVAL_LAT = 1

# Waiting time before Measurements start
ADDITIONAL_WAITING_TIME = 10

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)

        # dictionary for login to ssh server
        self.pw_dict = {'10.0.1.2': ['ps1', 'tud'],'10.0.2.2': ['ps2', 'tud']}
        # self.mac_to_port = {}
        self.dpidToDatapath = {}
        # TODO: matching the macs to dpid
        self.mac_to_dpid = {}

        # sw - controlelr port to dpid
        self.port_to_dpid = {}

        # saving the values for RTTs
        self.rtt_sent_to_dpid = {}
        self.rtt_port_sent = {}

        # temporary saving RTT times
        self.echo_sent_to_dpid = {}
        self.rtt_to_dpid = {}
        self.echo_rtt_to_dpid = {}
        self.echo_timeToSw = {}
        self.echo_timeToC = {}
        self.rtt_portStats_to_dpid = {}

        # bundled saving RTT/Echo times
        self.saved_rtt_to_dpid = {}
        self.saved_echo_rtt_to_dpid = {}
        self.saved_echo_timeToSw = {}
        self.saved_echo_timeToC = {}
        self.saved_rtt_to_dpid_portStats = {}

        # BW in Kbit/s, Latency in ms
        self.data_map = {}

        # temporary saving of port stats
        self.temp_bw_map = {}
        self.rtt_port_stats_sent = {}

        # statusVariables
        #self.startingTime = 0.0
        self.timeTillPlot = 102.2
        self.allreadyPlotted = False

        self.lastArrivedPackage = {}

        # parts of routing
        self.topology_api_app = self
        self.datapath_list = {}
        self.arp_table = {}
        self.switches = [] #1
        self.hosts = {} #{'90:1b:0e:cb:8d:94': (158445886737823, 4294967294), '90:1b:0e:cb:8d:9f': (158445886737812, 4294967294)}
        self.multipath_group_ids = {}
        self.group_ids = []
        self.adjacency = defaultdict(dict)
        # change for latency
        self.bandwidths = defaultdict(lambda: defaultdict(lambda: DEFAULT_BW))

        # ping datas
        self.ping_ready = {}
        self.output = {}
        self.ping_data_C_Sw = {}
        # in between switches
        self.ping_ready_inBetween = {}

        ########## Processes ############
        # starting rest API
        if WITH_WEB_INTERFACE:
            hub.spawn(self.run_DB)
        # starting updateThread
        hub.spawn(self.checkingUpdates)
        # starting ping monitoring (thread)
        self.monitor_pings()

        if(TESTTYPE == 'IPERF'):
            self.monitor_queues()
            self.changeLatency(SWITCH_IP_1_2, 'eth0', 0.001, 3000)
            self.changeLatency(SWITCH_IP_2_2, 'eth0', 0.001, 3000)

        # iperf
        self.iperfAlready = False
        self.iperfMeasurementReady = False

        # for changing latency
        self.enamurationNumber = 1
        # each (...) seconds changed
        self.timestepsize = 30.0
        self.changingLatMap = {}
        self.changedAlready = False

        # when system is started
        self.startingTime = time.time() + ADDITIONAL_WAITING_TIME

        self.changeit = 30.0

        self.backlog = {}
        self.packets_drop = {}
        self.packets_drop_init = {}        

        ########### TODO: kick out
        # socket
        #self.socket_output = {}
        #self.socketReady = {}
        #self.monitor_sockets()

    def create_ping_map(self,output):
        linesList = output
        i = 0
        dictLat = {}
        while(i < len(linesList)):
            timeVal = float (linesList[i])
            latVal = float (linesList[i+1])
            dictLat[timeVal] = latVal
            i = i + 2
        return dictLat

    def checkingUpdates(self):
        # waiting that all data is together
        time.sleep(ADDITIONAL_WAITING_TIME + 1.1)

        if (TESTTYPE == 'CHANGINGLATCONTROLLER'):
            latencyValue1 = 40.0
            latencyValue2 = 40.0
            self.changeLatency(SWITCH_IP_1_2, 'eth0', latencyValue1)
            self.changeLatency(SWITCH_IP_2_2, 'eth0', latencyValue2)
            if (SWITCH_IP_1_2 not in self.changingLatMap.keys()):
                self.changingLatMap[SWITCH_IP_1_2] = []
                self.changingLatMap[SWITCH_IP_2_2] = []
            latencyChangingElement1 = {}
            latencyChangingElement2 = {}
            latencyChangingElement1['timestamp'] = time.time()
            latencyChangingElement2['timestamp'] = time.time()
            latencyChangingElement1['value'] = latencyValue1
            latencyChangingElement2['value'] = latencyValue2
            self.changingLatMap[SWITCH_IP_1_2].append(latencyChangingElement1)
            self.changingLatMap[SWITCH_IP_2_2].append(latencyChangingElement2)

        if(TESTTYPE == 'CHANGINGLATTOSHOWDIFFERENCE'):
            self.changeLatency(SWITCH_IP_2_2, 'eth0', 0.0)

        if(TESTTYPE == 'ONELONGTIME'):
            pass
            self.changeLatency(SWITCH_IP_2_2, 'eth0', 0.0)
            # 0 10 30 50 70 90
            latencyValue1 = 0.0
            latencyValue2 = 0.0
            self.changeLatency(SWITCH_IP_1_2, 'eth0', latencyValue1)
            if (SWITCH_IP_1_2 not in self.changingLatMap.keys()):
                self.changingLatMap[SWITCH_IP_1_2] = []
                self.changingLatMap[SWITCH_IP_2_2] = []
            latencyChangingElement1 = {}
            latencyChangingElement2 = {}
            latencyChangingElement1['timestamp'] = time.time()
            latencyChangingElement2['timestamp'] = time.time()
            latencyChangingElement1['value'] = latencyValue1
            latencyChangingElement2['value'] = latencyValue2
            self.changingLatMap[SWITCH_IP_1_2].append(latencyChangingElement1)
            self.changingLatMap[SWITCH_IP_2_2].append(latencyChangingElement2)
            self.logger.info('LatencychangeMap: {}'.format(self.changingLatMap))

        while True:
            # matrix creation
            # latencyMatrix = matrix_np.create_matrix(self.data_map, 'latency')
            # bwMatrix = matrix_np.create_matrix(self.data_map, 'bw') TODO: fix errors

            if TESTTYPE == 'IPERF' and self.iperfAlready == False and MININET == False:
                if (time.time() - self.startingTime) > IPERF_START_TIME:
                    self.logger.info("Staring Ipferf adding")
                    # 2nd switch
                    hub.spawn(self.addingBwIperfServer, SWITCH_IP_2_2)
                    # 1st switch
                    hub.spawn(self.addingBwIperfClient, SWITCH_IP_1_2, SWITCH_IP_2_inBetween)
                    self.iperfAlready = True

            if TESTTYPE == 'CHANGINGLATTOSHOWDIFFERENCE' and MININET == False:
                self.logger.info("IN HERE")
                # in 10 sec steps
                if self.changeit < time.time() - self.startingTime and self.changeit+10.0 > time.time() - self.startingTime:
                    latencyValue1 = self.changeit
                    self.changeLatency(SWITCH_IP_1_2, 'eth0', latencyValue1)
                    if (SWITCH_IP_1_2 not in self.changingLatMap.keys()):
                        self.changingLatMap[SWITCH_IP_1_2] = []
                        self.changingLatMap[SWITCH_IP_2_2] = []
                    latencyChangingElement1 = {}
                    latencyChangingElement1['timestamp'] = time.time()
                    latencyChangingElement1['value'] = latencyValue1
                    self.changingLatMap[SWITCH_IP_1_2].append(latencyChangingElement1)
                    self.logger.info('LatencychangeMap: {}'.format(self.changingLatMap))
                    #self.changedAlready = True
                    self.enamurationNumber += 1
                    self.changeit = self.changeit+10.0
                self.logger.info("OUT HERE")

            if TESTTYPE == 'CHANGINGLAT' and MININET == False:
                if 40.0 < time.time() - self.startingTime and self.changedAlready == False and 60.0 > time.time() - self.startingTime:
                #if self.enamurationNumber*self.timestepsize > time.time() - self.startingTime:
                    latencyValue1 = '40'
                        #float(self.timestepsize) *10.0 + 10.0
                    latencyValue2 = '60'
                        #float(self.timestepsize) * 10.0 + 20.0
                    self.changeLatency(SWITCH_IP_1_2,'eth0', latencyValue1)
                    self.changeLatency(SWITCH_IP_2_2,'eth0', latencyValue2)
                    if(SWITCH_IP_1_2 not in self.changingLatMap.keys()):
                        self.changingLatMap[SWITCH_IP_1_2] = []
                        self.changingLatMap[SWITCH_IP_2_2] = []
                    latencyChangingElement1 = {}
                    latencyChangingElement2 = {}
                    latencyChangingElement1['timestamp'] = time.time()
                    latencyChangingElement2['timestamp'] = time.time()
                    latencyChangingElement1['value'] = latencyValue1
                    latencyChangingElement2['value'] = latencyValue2
                    self.changingLatMap[SWITCH_IP_1_2].append(latencyChangingElement1)
                    self.changingLatMap[SWITCH_IP_2_2].append(latencyChangingElement2)
                    self.logger.info('LatencychangeMap: {}'.format(self.changingLatMap))
                    self.changedAlready = True
                    self.enamurationNumber += 1

            if TESTTYPE == 'CHANGINGLATCONTROLLER' and MININET == False:
                if 40.0 < time.time() - self.startingTime and self.changedAlready == False and 50.0 > time.time() - self.startingTime:
                #if self.enamurationNumber*self.timestepsize > time.time() - self.startingTime:
                    latencyValue1 = '20'
                    latencyValue2 = '40'
                    self.changeLatency(SWITCH_IP_1_2,'eth1', latencyValue1)
                    # self.changeLatency(SWITCH_IP_2_2,'eth0', latencyValue2)

                    if(SWITCH_IP_1_2 not in self.changingLatMap.keys()):
                        self.changingLatMap[SWITCH_IP_1_2] = []
                        self.changingLatMap[SWITCH_IP_2_2] = []

                    command = 'sudo tc qdisc change dev enxa0cec81d1262 root netem delay {}ms'.format(latencyValue2)
                    nads = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).communicate()
                    self.logger.info("!!!!!!!!!!!!!!!!!!!!!!!LATENCYVALUECHANGED AT: {}  !!!!!!!!!!!!".format(time.time()-self.startingTime))
                    latencyChangingElement1 = {}
                    latencyChangingElement2 = {}
                    latencyChangingElement1['timestamp'] = time.time()
                    latencyChangingElement2['timestamp'] = time.time()
                    latencyChangingElement1['value'] = latencyValue1
                    latencyChangingElement2['value'] = latencyValue2
                    self.changingLatMap[SWITCH_IP_1_2].append(latencyChangingElement1)
                    self.changingLatMap[SWITCH_IP_2_2].append(latencyChangingElement2)
                    self.logger.info('LatencychangeMap: {}'.format(self.changingLatMap))
                    self.changedAlready = True
                    self.enamurationNumber += 1
                if 50.0 < time.time() - self.startingTime and self.changedAlready == True and 60.0 > time.time() - self.startingTime:
                    self.changedAlready = False
                if 62.0 < time.time() - self.startingTime and self.changedAlready == False and 80.0 > time.time() - self.startingTime:
                    latencyValue1 = '60'
                    # float(self.timestepsize) *10.0 + 10.0
                    latencyValue2 = '60'
                    # float(self.timestepsize) * 10.0 + 20.0
                    self.changeLatency(SWITCH_IP_1_2, 'eth0', latencyValue1)
                    self.changeLatency(SWITCH_IP_2_2, 'eth0', latencyValue2)
                    if (SWITCH_IP_1_2 not in self.changingLatMap.keys()):
                        self.changingLatMap[SWITCH_IP_1_2] = []
                        self.changingLatMap[SWITCH_IP_2_2] = []
                    latencyChangingElement1 = {}
                    latencyChangingElement2 = {}
                    latencyChangingElement1['timestamp'] = time.time()
                    latencyChangingElement2['timestamp'] = time.time()
                    latencyChangingElement1['value'] = latencyValue1
                    latencyChangingElement2['value'] = latencyValue2
                    self.changingLatMap[SWITCH_IP_1_2].append(latencyChangingElement1)
                    self.changingLatMap[SWITCH_IP_2_2].append(latencyChangingElement2)
                    self.logger.info('LatencychangeMap: {}'.format(self.changingLatMap))
                    self.changedAlready = True
                    self.enamurationNumber += 1

            if (80.0 < time.time() - self.startingTime and self.changedAlready == True and MININET == False and TESTTYPE == 'CHANGINGLAT') or (TESTTYPE == 'CHANGINGLATTOSHOWDIFFERENCE' and MININET == False and 99.0 < time.time() - self.startingTime):
                # if self.enamurationNumber*self.timestepsize > time.time() - self.startingTime:
                latencyValue1 = '20'
                # float(self.timestepsize) *10.0 + 10.0
                latencyValue2 = '20'
                # float(self.timestepsize) * 10.0 + 20.0
                self.changeLatency(SWITCH_IP_1_2, 'eth0', latencyValue1)
                self.changeLatency(SWITCH_IP_2_2, 'eth0', latencyValue2)
                if (SWITCH_IP_1_2 not in self.changingLatMap.keys()):
                    self.changingLatMap[SWITCH_IP_1_2] = []
                    self.changingLatMap[SWITCH_IP_2_2] = []
                latencyChangingElement1 = {}
                latencyChangingElement2 = {}
                latencyChangingElement1['timestamp'] = time.time()
                latencyChangingElement2['timestamp'] = time.time()
                latencyChangingElement1['value'] = latencyValue1
                latencyChangingElement2['value'] = latencyValue2
                self.changingLatMap[SWITCH_IP_1_2].append(latencyChangingElement1)
                self.changingLatMap[SWITCH_IP_2_2].append(latencyChangingElement2)
                self.logger.info('LatencychangeMap: {}'.format(self.changingLatMap))
                self.changedAlready = False
                self.enamurationNumber += 1

            if not self.allreadyPlotted:
                timeNow = time.time()
                self.logger.info("TIME since start: {}s Time Total: {}s -> {}%".format(timeNow - self.startingTime, self.timeTillPlot,
                        ((timeNow - self.startingTime)/self.timeTillPlot)*100))
                if time.time() - self.startingTime > self.timeTillPlot:
                    self.logger.info("**********PLOTTING LATENCY***********")
                    self.handleDataForPlotting()
            time.sleep(4.1)

    def addingBwIperfClient(self, hostClientIP, serverIP, port = 5001):

        # new ssh client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostClientIP, username=self.pw_dict[hostClientIP][0], password=self.pw_dict[hostClientIP][1])

        #time.sleep(5)
        firstVal = 95
        sndVal = 97
        #print("IPERF adding bw: {}Mbit".format(startAmount + incrementAmount * x))
        stdin, stdout, stderr = ssh.exec_command(
            "sudo bash iperf_script.sh")
        print(stdout.readlines())

        #stdin, stdout, stderr = ssh.exec_command(
        #    "iperf -c {} -t 60 -p {} -b {}M -u -i 1 &".format(serverIP, port, sndVal))
        #print(stdout.readlines())
        # startingamount
        #startAmount = 95
        #time.sleep(10)
        #steps = 2
        #  gradient
        #incrementAmount = 1
        #for x in range(0, steps):
        #    print("IPERF adding bw: {}Mbit".format(startAmount + incrementAmount * x))
        #    stdin, stdout, stderr = ssh.exec_command("iperf -c {} -t 30 -p {} -b {}M -u -i 1 &".format(serverIP,port, startAmount + incrementAmount * x))
        #    print(stdout.readlines())
        #time.sleep (20)
        self.iperfMeasurementReady = True
        ssh.close()

    def addingBwIperfServer(self,serverIP,  port= 5001):

        # new ssh client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(serverIP, username=self.pw_dict[serverIP][0], password=self.pw_dict[serverIP][1])

        stdin, stdout, stderr = ssh.exec_command("iperf -s -u -p {}".format(port))
        while True:
            time.sleep(0.1)
            # check if iperf ready
            if self.iperfMeasurementReady == True:
                break
        print(stdout.readlines())
        ssh.close()

    def checkBacklog(self, hostIP):
        time.sleep(ADDITIONAL_WAITING_TIME+4)
        # new ssh client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostIP, username=self.pw_dict[hostIP][0], password=self.pw_dict[hostIP][1])

        command1 = 'sudo tc -s qdisc ls dev eth0 | grep -E -o "backlog [0-9]+b [0-9]+p" | grep -E -o "[0-9]+p" | grep -E -o "[0-9]+"'
        command2 = 'sudo tc -s qdisc ls dev eth0 | grep -E -o "dropped [0-9]+" | grep -E -o "[0-9]+"'

        while (self.ping_ready[SWITCH_IP_1] == False):
            timebefore = time.time()
            stdin, stdout, stderr = ssh.exec_command(command1)
            output1 = stdout.readlines()
            stdin, stdout, stderr = ssh.exec_command(command2)
            output2 = stdout.readlines()
            if(hostIP not in self.backlog.keys()):
                self.backlog[hostIP] = []
                # value of dropped packets
                if len(output2) > 0:
                    self.packets_drop_init[hostIP] = str(output2[0])
                self.packets_drop[hostIP] = []

            #get int
            #intVal = int(filter(str.isdigit, output))
            #print("Backlog Output_str: {}".format(output))
            #print("Backlog Output: {}".format(int(output[0])))
            if(len(output1) > 0  and len(output2) > 0):
                backlogElement = {}
                backlogElement['ts'] = timebefore
                backlogElement['value'] = int(output1[0])
                self.backlog[hostIP].append(backlogElement)
                droppedElement = {}
                droppedElement['ts'] = timebefore
                droppedElement['value'] = int(output2[0]) - int(self.packets_drop_init[hostIP])
                self.packets_drop[hostIP].append(droppedElement)
            # each 1 sec
            time.sleep(1)

    def changeLatency(self, ipConnecting, socketChanging='eth0', value=30, limit=1000):
        # new ssh client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ipConnecting, username=self.pw_dict[ipConnecting][0], password=self.pw_dict[ipConnecting][1])
        self.logger.info('Latency changed for: {} to {}'.format(socketChanging, value))
        # for egress queue
        # limit is the queue size
        command = 'sudo tc qdisc change dev {} root netem delay {}ms limit {}'.format(socketChanging, value, limit)
        self.logger.info('LatencyChangingCmd : {}'.format(command))
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.readlines()
        print("response: {}".format(output))
        ssh.close()

    def monitor_pingConnectionbetweenswitches(self, hostIP, clientIP):
        time.sleep(ADDITIONAL_WAITING_TIME+1.1)
        # new ssh client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostIP, username=self.pw_dict[hostIP][0], password=self.pw_dict[hostIP][1])

        self.ping_ready[clientIP] = False
        self.logger.info("Starting ping in between to: {} from {}".format(clientIP, hostIP))
        time.sleep(1)
        pingtime = int((self.timeTillPlot) * 9.99/5 - 2)

        # testing ssh connection and sudo rights
        cmd_test = 'sudo ls'
        stdin, stdout, stderr = ssh.exec_command(cmd_test)
        while True:
            data = stdout.readlines()
            dataErr = stderr.readlines()
            if len(data) > 0:
                print("Passed test ssh host: {} to: {}".format(hostIP, clientIP))
                break
            time.sleep(0.1)

        # send one ping
        #commandFirst = 'sudo ping {} -D -c {}'.format(clientIP, 1)
        #stdin, stdout, stderr = ssh.exec_command(commandFirst)

        time.sleep(1)
        command = 'sudo ping {} -D -c {} -i 0.5 | head -n -3 | grep -E "[0-9]+\.?[0-9]+ ms" | grep -o -E "\[[0-9]+\.[0-9]+\]|[0-9]+\.?[0-9]+ ms" | grep -o -E "[0-9]+\.?[0-9]+"'.format(clientIP, pingtime)

        timebefore = time.time()
        stdin, stdout, stderr = ssh.exec_command(command)

        while True:
            data = stdout.readlines()
            dataErr = stderr.readlines()
            if len(data) > 0:
                self.logger.info("End of ssh Ping, IP: {}, time taken: {}".format(clientIP, time.time() - timebefore))
                break
            time.sleep(0.1)
        #self.logger.info("End of ssh, answer: {}".format(data))
        self.output[clientIP] = data
        self.ping_ready[clientIP] = True

    def monitor_ping(self, host, ping_interval = 0.1):
        time.sleep(ADDITIONAL_WAITING_TIME+1.0)
        self.ping_ready[host] = False
        time.sleep(0.5)
        #pingtime = int((self.timeTillPlot)*9.99-2)
        pingtime= int((self.timeTillPlot) * 9.99 - 2)
        self.logger.info("ping to machine host: {} ping steps: {}".format(host,pingtime))
        # ping controller switch 30/0,1 = 300 steps
        command = 'sudo ping {} -D -c {} -i 0.1 | head -n -3 | grep -o -E "\[[0-9]+\.[0-9]+\]|[0-9]+\.[0-9]+ ms" | grep -o -E "[0-9]+\.[0-9]+"'.format(host, pingtime)

        self.output[host] = subprocess.Popen(command, shell = True, stdout=subprocess.PIPE).communicate()
        self.logger.info("Ping monitoring finished")
        self.ping_ready[host] = True

    def monitor_pings(self):
        if(MININET == True):
            self.logger.info("Ping loopback")
            hub.spawn(self.monitor_ping, LOOPBACK_IP)
        else:
            self.logger.info("Starting Ping Rasperry")
            hub.spawn(self.monitor_ping, SWITCH_IP_1)
            hub.spawn(self.monitor_ping, SWITCH_IP_2)
        # Between the raspian
        if MININET == False:
            # Taking the safe route (for time synchronisation)
            hub.spawn(self.monitor_pingConnectionbetweenswitches, SWITCH_IP_1_2, SWITCH_IP_2_inBetween)
            hub.spawn(self.monitor_pingConnectionbetweenswitches, SWITCH_IP_2_2, SWITCH_IP_1_inBetween)

    def monitor_queues(self):
        self.logger.info("MONITORING QUEUES STARTED")
        if MININET == False:
            # checking backlog
            hub.spawn(self.checkBacklog, SWITCH_IP_1_2)
            hub.spawn(self.checkBacklog, SWITCH_IP_2_2)

    def monitor_echo(self, datapath):
        time.sleep(ADDITIONAL_WAITING_TIME)
        data = ''
        i = 0
        if TESTTYPE == 'RTT':
            self.logger.info("TESTTYPE RTT DP: {}".format(datapath.id))
            while True:
                # ungerade
                if(i % 2 > 0):
                    self.send_stats_request(datapath)
                else:
                    self.send_echo_request(datapath, data)
                i += 1
                time.sleep(UPDATE_INTERVAL_CSW)
        else:
            if(MEASUREMENTTYPE == 'ALL'):
                while True:
                    self.send_stats_request(datapath)
                    time.sleep(UPDATE_INTERVAL_CSW / 3)
                    self.send_echo_request(datapath, data)
                    time.sleep(UPDATE_INTERVAL_CSW / 3)
                    self.send_portStatsRequest(datapath)
                    time.sleep(UPDATE_INTERVAL_CSW / 3)

            elif(MEASUREMENTTYPE == 'ECHORTT') or (MEASUREMENTTYPE == 'ECHO'):
                while True:
                    #self.logger.info('MEASUREMENTTYPE: ECHO')
                    # every tenth time portstatsrequest
                    for i in range (1,10):
                        self.send_echo_request(datapath, data)
                        time.sleep(UPDATE_INTERVAL_CSW)
                    self.send_portStatsRequest(datapath)

            elif(MEASUREMENTTYPE == 'PORTSTATS'):
                #self.logger.info('MEASUREMENTTYPE: PORTSTATS')
                while True:
                    self.send_portStatsRequest(datapath)
                    time.sleep(UPDATE_INTERVAL_CSW)

    # the monitoring package
    def monitor_latency(self, datapath, ofproto):
        time.sleep(ADDITIONAL_WAITING_TIME + 3.2)
        print("MONITORING LATENCY STARTED")
        while True:
            self.send_packet_out(datapath, ofproto.OFP_NO_BUFFER, ofproto.OFPP_CONTROLLER)
            hub.sleep(UPDATE_INTERVAL_LAT)

    def send_portStatsRequest(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPPortStatsRequest(datapath, 0, ofp.OFPP_ANY)
        # save timeStamp for RTT
        self.rtt_port_stats_sent[datapath.id] = time.time()
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def port_stats_reply_handler(self, ev):
        dpidRec = ev.msg.datapath.id
        body = ev.msg.body
        # match in dp
        currentTime = time.time()
        ports = []
        # parsing the answer
        for stat in body:
            # get port id
            port_no = (int) (stat.port_no)
            # if first package out
            if dpidRec in self.data_map.keys():
                for dpidSentElement in self.data_map[dpidRec]:
                    in_port = self.data_map[dpidRec][dpidSentElement]["in_port"]
                    if in_port == port_no:
                        # found the right connection

                        # check if bw-map is built, first time!
                        if not dpidRec in self.temp_bw_map.keys():
                            self.temp_bw_map[dpidRec] = {}

                        if not port_no in self.temp_bw_map[dpidRec].keys():
                            self.temp_bw_map[dpidRec][port_no] = {}
                            bytes_now = stat.rx_bytes
                            #bytes_now = stat.tx_bytes
                            ts_now = (stat.duration_sec + stat.duration_nsec / (10 ** 9))

                            # overwriting tempMap

                            self.temp_bw_map[dpidRec][port_no]['ts'] = ts_now
                            self.temp_bw_map[dpidRec][port_no]['bytes'] =  bytes_now

                            # save the time
                            self.temp_bw_map[dpidRec][port_no]['ts'] = ts_now

                            #self.logger.info("TS BW: {}".format(self.temp_bw_map[dpidRec][port_no]['ts']))
                            self.temp_bw_map[dpidRec][port_no]['tsUTC'] = time.time()
                        else:
                            ts_before = self.temp_bw_map[dpidRec][port_no]['ts']
                            bytes_before = self.temp_bw_map[dpidRec][port_no]['bytes']
                            #ts_now = time.time()
                            bytes_now = stat.tx_bytes
                            ts_now = (stat.duration_sec + stat.duration_nsec / (10 ** 9))
                            byteDiff = bytes_now - bytes_before
                            tsDiff = ts_now - ts_before  # TODO: ggf RTT mit einbeziehen

                            # overwriting tempMap
                            self.temp_bw_map[dpidRec][port_no]['ts'] = ts_now
                            self.temp_bw_map[dpidRec][port_no]['bytes'] = bytes_now

                            # bw (bytes/sec)
                            bw = byteDiff / tsDiff

                            # save it in map
                            self.saveBwInMap(dpidRec, port_no, bw, self.temp_bw_map[dpidRec][port_no]['tsUTC'])
                            self.temp_bw_map[dpidRec][port_no]['tsUTC'] = time.time()
                        # latencymeasurement
                        oldTime = self.rtt_port_stats_sent[dpidRec]
                        totalRTT = currentTime - oldTime
                        # setting new time
                        self.rtt_portStats_to_dpid[dpidRec] = totalRTT
                        self.rtt_port_stats_sent[dpidRec] = 0
                        # saving for plotting
                        if not dpidRec in self.saved_rtt_to_dpid_portStats:
                            self.saved_rtt_to_dpid_portStats[dpidRec] = []
                        rttElement = {}
                        rttElement[currentTime] = totalRTT
                        self.saved_rtt_to_dpid_portStats[dpidRec].append(rttElement)

    def send_echo_request(self, datapath, data):
        # OP_ECHO
        # self.logger.info("sending echo request, dp:{}".format(datapath.id))

        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        self.echo_sent_to_dpid[datapath.id] = time.time()

        req = ofp_parser.OFPEchoRequest(datapath, data=bytearray.fromhex('00' * 8))
        datapath.send_msg(req)

    # in this case: meterstatsrequest
    def send_stats_request(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        req = ofp_parser.OFPMeterStatsRequest(datapath, 0, ofp.OFPM_ALL)
        self.rtt_sent_to_dpid[datapath.id] = time.time()
        # self.logger.info("RTT request started, dpid: {}".format(datapath.id))
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPEchoReply, [HANDSHAKE_DISPATCHER, CONFIG_DISPATCHER, MAIN_DISPATCHER])
    def echo_reply_handler(self, ev):
        timeStamp_enc = pc.pack('<q', *pc.unpack('>q', bytearray(ev.msg.data)))
        #self.logger.info("Message Echo reply: {}".format(ev.msg))
        dpid = ev.msg.datapath.id
        # getting timestamp
        timeStampF = float(int(binascii.hexlify(timeStamp_enc), 16))

        # calculating the values
        timeStampT = timeStampF/10e8

        #self.logger.info('Timestamp: data={}'.format(timeStampT))

        timeWhenSent = self.echo_sent_to_dpid[dpid]
        currentTime =  time.time()

        # calculating differences
        wholeTime = currentTime - timeWhenSent
        timeSwToC = timeStampT - timeWhenSent
        timeCToSw = currentTime - timeStampT

        self.echo_rtt_to_dpid[dpid] = wholeTime
        self.echo_timeToSw[dpid] = timeSwToC
        self.echo_timeToC[dpid] = timeCToSw

        # saving for plotting
        if(dpid not in self.saved_echo_rtt_to_dpid.keys()):
            self.saved_echo_rtt_to_dpid[dpid] = []
        if (dpid not in self.saved_echo_timeToSw.keys()):
            self.saved_echo_timeToSw[dpid] = []
        if (dpid not in self.saved_echo_timeToC.keys()):
            self.saved_echo_timeToC[dpid] = []


        echoRTTElement = {}
        echoRTTElement[currentTime] = wholeTime
        echoTimeToSwElement = {}
        echoTimeToSwElement[currentTime] = timeSwToC
        echoTimeToCElement = {}
        echoTimeToCElement[currentTime] = wholeTime - timeSwToC

        self.saved_echo_rtt_to_dpid[dpid].append(echoRTTElement)
        self.saved_echo_timeToSw[dpid].append(echoTimeToSwElement)
        self.saved_echo_timeToC[dpid].append(echoTimeToCElement)

        # debug timestamps
        #self.logger.info("CurrentTime: {}, TimeEchoTimestamp: {}".format(currentTime,timeStampT))
        #self.logger.info("DpId: {}, TD R2Sw: {}ms, TD Sw2R: {}ms, TotalTimeTillArrive: {}ms".format(dpid,timeSwToC*1000,timeCToSw*1000,wholeTime*1000))

    @set_ev_cls(ofp_event.EventOFPMeterStatsReply, MAIN_DISPATCHER)
    def meter_stats_reply_handler(self, ev):
        receive_time = time.time()
        dpid = ev.msg.datapath.id
        # if key is not set
        if not self.rtt_sent_to_dpid[dpid]:
            pass
        else:
            if not dpid in self.saved_rtt_to_dpid:

                self.saved_rtt_to_dpid[dpid] = []
            # setting new time
            totalRTT = receive_time - self.rtt_sent_to_dpid[dpid]
            self.rtt_to_dpid[dpid] = totalRTT
            self.rtt_sent_to_dpid[dpid] = ""

            # saving for plotting
            rttElement = {}
            rttElement[receive_time] = totalRTT
            self.saved_rtt_to_dpid[dpid].append(rttElement)

    def run_DB(self):
        hub.spawn(restDB.app.run)

        time.sleep(ADDITIONAL_WAITING_TIME + 1.2)
        while True:
            # TODO:DEBUG:
            #self.logger.info("map: {}".format(self.data_map))
            restDB.modify_db(self.data_map)
            time.sleep(1)

    def send_packet_out(self, datapath, buffer_id, in_port):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        packet = self.create_packet(datapath.id)

        data = packet.data

        actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD, 0)]
        req = ofp_parser.OFPPacketOut(datapath, buffer_id,
                                      in_port, actions, data)
        datapath.send_msg(req)


    # register datapaths
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        #self.logger.info("Register DP: {}".format(ev.msg))
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        # self.logger.info("Register switch Message: {}".format(ev.msg))
        dpid = datapath.id
        self.logger.info("registered DP: {}".format(dpid))

        # strting the echo_request
        hub.spawn(self.monitor_echo, datapath)

        # Starting flooding thread for flooding monitoring package
        # self.logger.info("started Thread ({})".format(dpid))
        hub.spawn(self.monitor_latency, datapath, ofproto)

        # starting monitoring RTT switches
        #hub.spawn(self.monitor_rtt_switches, datapath)



        # register datapaths
        self.dpidToDatapath[dpid] = datapath

        self.lastArrivedPackage[dpid] = {}

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        print("Adding controller flow")
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    #  datapath, priority, match, actions
    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        #self.logger.info("FLOW ADDED: {}".format(mod))
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        
        # directly taking the timestamp when packet arrives
        timestampRecieve = time.time()

        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        arp_pkt = pkt.get_protocol(arp.arp)

        dpidRec = datapath.id
        dst = eth.dst
        src = eth.src

       

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        # -------------------
        # avoid broadcast from LLDP
        if eth.ethertype == 35020:
            return

        if pkt.get_protocol(ipv6.ipv6):  # Drop the IPV6 Packets.
            match = parser.OFPMatch(eth_type=eth.ethertype)
            actions = []
            self.add_flow(datapath, 1, match, actions)
            return None
        # --------------------

        

        # -------------------
        
        
        # -------------------
        # if measurement packet 
        if (eth.ethertype == 0x07c3):

            pkt_header_list = pkt[-1].decode("utf-8").split('#')

            timestampSent = (float)(pkt_header_list[0])
            dpidSent = (int)(pkt_header_list[1])

            if not dpidSent in self.lastArrivedPackage[dpidRec].keys():
                self.lastArrivedPackage[dpidRec][dpidSent] = 0.0

            # timedifference
            timeDifference = timestampRecieve - timestampSent

            # calculating link latency (with RTT) TODO: CHANGE TO ECHO!
            #self.logger.info("RTT_2_DPID: {}".format(self.rtt_to_dpid))

            # if package is newest
            if(timestampSent > self.lastArrivedPackage[dpidRec][dpidSent]):
                # creating dictionaries and arrays
                if not dpidRec in self.data_map.keys():
                    self.data_map[dpidRec] = {}

                if not dpidSent in self.data_map[dpidRec].keys():
                    self.data_map[dpidRec][dpidSent] = {}
                    self.data_map[dpidRec][dpidSent]['in_port'] = in_port
                    self.data_map[dpidRec][dpidSent]['latency'] = []
                    self.data_map[dpidRec][dpidSent]['bw'] = []
                    self.data_map[dpidRec][dpidSent]['latencyPortStats'] = []
                    self.data_map[dpidRec][dpidSent]['latencyEchoRTT'] = []
                    self.data_map[dpidRec][dpidSent]['latencyEcho'] = []

                if(MEASUREMENTTYPE == 'RTT') or (MEASUREMENTTYPE == 'ALL'):
                    latencyLinkRTT = timeDifference - (float(self.rtt_to_dpid[dpidSent]) / 2) - (
                    float(self.rtt_to_dpid[dpidRec]) / 2)
                    # latency object RTT
                    latencyObj = {}
                    latencyObj['timestamp'] = timestampSent
                    latencyObj['value'] = latencyLinkRTT * 1000
                    self.data_map[dpidRec][dpidSent]['latency'].append(latencyObj)

                if (MEASUREMENTTYPE == 'ECHORTT') or (MEASUREMENTTYPE == 'ALL') or (MEASUREMENTTYPE == 'ECHO'):
                    latencyLinkEchoRTT = timeDifference - (float(self.echo_rtt_to_dpid[dpidSent]) / 2) - (
                    float(self.echo_rtt_to_dpid[dpidRec]) / 2)
                    # latency object echo RTT
                    latencyObjEchoRTT = {}
                    latencyObjEchoRTT['timestamp'] = timestampSent
                    latencyObjEchoRTT['value'] = latencyLinkEchoRTT * 1000
                    self.data_map[dpidRec][dpidSent]['latencyEchoRTT'].append(latencyObjEchoRTT)

                if (MEASUREMENTTYPE == 'ECHO') or (MEASUREMENTTYPE == 'ALL') or (MEASUREMENTTYPE == 'ECHORTT'):
                    latencyLinkEcho = timeDifference - (float(self.echo_timeToSw[dpidSent])) - (
                    float(self.echo_timeToC[dpidRec]))
                    # latency object echo
                    latencyObjEcho = {}
                    latencyObjEcho['timestamp'] = timestampSent
                    latencyObjEcho['value'] = latencyLinkEcho * 1000
                    self.data_map[dpidRec][dpidSent]['latencyEcho'].append(latencyObjEcho)

                if (MEASUREMENTTYPE == 'PORTSTATS') or (MEASUREMENTTYPE == 'ALL'):
                    # for port stats
                    if dpidRec in self.rtt_portStats_to_dpid.keys():
                        latencyLinkPortStatsRTT = timeDifference - (float(self.rtt_portStats_to_dpid[dpidSent]) / 2) - (
                        float(self.rtt_portStats_to_dpid[dpidRec]) / 2)
                        # latency object RTT Ports
                        latencyObjPort = {}
                        latencyObjPort['timestamp'] = timestampSent
                        latencyObjPort['value'] = latencyLinkPortStatsRTT * 1000
                        self.data_map[dpidRec][dpidSent]['latencyPortStats'].append(latencyObjPort)
                # overlapped packeges thrown away
                self.lastArrivedPackage[dpidRec][dpidSent] = time.time()

                # starting the statsrequest (BW)
                # self._request_stats(self.dpidToDatapath[dpidRec], in_port)

                return
            else:
                self.logger.info("ONE ARRIVED EARLIER")
        buol = True
        if src not in self.hosts:
            for host in self.hosts:
                print("hosts: {}".format(host))
                dpid = host[0]
                print("dpid: {} = dpidRec: {}".format(dpid, dpidRec))
                if dpid == dpidRec:
                    buol=False
            if buol:
                self.hosts[src] = (dpidRec, in_port)

        

        out_port = ofproto.OFPP_FLOOD

        if arp_pkt:
            # print dpid, pkt
            src_ip = arp_pkt.src_ip
            dst_ip = arp_pkt.dst_ip
            if arp_pkt.opcode == arp.ARP_REPLY:
                print("ARP reply in {} from {} in port: {}".format(dpidRec, src_ip, in_port))
                self.arp_table[src_ip] = src
                h1 = self.hosts[src]
                h2 = self.hosts[dst]               
                #out_port = self.install_paths(h1[0], h1[1], h2[0], h2[1], src_ip, dst_ip)
                #self.install_paths(h2[0], h2[1], h1[0], h1[1], dst_ip, src_ip) # reverse
                
            elif arp_pkt.opcode == arp.ARP_REQUEST:
                if dst_ip in self.arp_table:
                    print("ARP request in {} from {} in port: {}".format(dpidRec, src_ip, in_port))
                    self.arp_table[src_ip] = src
                    dst_mac = self.arp_table[dst_ip]
                    h1 = self.hosts[src]
                    h2 = self.hosts[dst_mac]
                    #out_port = self.install_paths(h1[0], h1[1], h2[0], h2[1], src_ip, dst_ip)
                    #self.install_paths(h2[0], h2[1], h1[0], h1[1], dst_ip, src_ip) # reverse
                    

        actions = [parser.OFPActionOutput(out_port)]
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    # for one port
    '''
    def _request_stats(self, datapath, portNumber):

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPPortStatsRequest(datapath, 0, portNumber)

        datapath.send_msg(req)
    '''

    # saving the Bw in Map
    def saveBwInMap(self, dpidRec, in_port, bw, ts_before):
        for keysDpidSent in self.data_map[dpidRec].keys():
            # matching the portNumber
            if self.data_map[dpidRec][keysDpidSent]['in_port'] == in_port:
                # bw object
                bwObject = {}
                bwObject['timestamp'] = ts_before
                # in kb/s
                bwObject['value'] = bw / 1024
                self.data_map[dpidRec][keysDpidSent]['bw'].append(bwObject)
                break
    
    # Creation of the measurement packet
    def create_packet(self, dpid):
        pkt = packet.Packet()
        timeNow = datetime.datetime.now()
        pkt.add_protocol(ethernet.ethernet(ethertype=0x07c3,
                                           dst='ff:ff:ff:ff:ff:ff',
                                           src='00:00:00:00:00:01'))
        wholeData = str(time.time()) + '#' + str(dpid) + '#'
        pkt.add_protocol(bytes(wholeData,"utf-8"))
        pkt.serialize()
        return pkt

    # ----------------------------#
    # -----routing functions------#
    # ----------------------------#
    # If switch connection is interrupted
    @set_ev_cls(event.EventSwitchLeave, MAIN_DISPATCHER)
    def switch_leave_handler(self, ev):
        print (ev)
        switch = ev.switch.dp.id
        if switch in self.switches:
            self.logger.info("Switch  {} left".format(switch.id))
            self.switches.remove(switch)
            del self.datapath_list[switch]
            del self.adjacency[switch]

    # If new switch is detected by LLDP
    @set_ev_cls(event.EventSwitchEnter)
    def switch_enter_handler(self, ev):
        switch = ev.switch.dp
        ofp_parser = switch.ofproto_parser

        if switch.id not in self.switches:
            self.switches.append(switch.id)
            self.datapath_list[switch.id] = switch
            self.logger.info("Switch  {} entered".format(switch.id))
            # Request port/link descriptions, useful for obtaining bandwidth
            req = ofp_parser.OFPPortDescStatsRequest(switch)
            switch.send_msg(req)
        if len(self.switches)>1:
            #static route add   src, first_port, dst, last_port, ip_src, ip_dst
            out_port_eth = 1
            out_port_host = 4294967294
            actions_eth = [ofp_parser.OFPActionOutput(out_port_eth)]
            actions_host = [ofp_parser.OFPActionOutput(out_port_host)]
            dp_1 = self.datapath_list[158445886737823] 
            dp_2 = self.datapath_list[158445886737812] 
            type_ip = 'ipv4'
            type_arp = 'arp'
            print( "!!!!!!!!!!!!!!!!!!ADDING FLOWS!!!!!!!!!!!!!!!!!!!!!")
            # 2x eth           
            self.add_flow(dp_1, self.get_priority(type_ip), self.get_match(type_ip, ofp_parser, '10.0.0.1', '10.0.0.2'), actions_eth)
            self.add_flow(dp_2, self.get_priority(type_ip), self.get_match(type_ip, ofp_parser, '10.0.0.2', '10.0.0.1'), actions_eth)
            self.add_flow(dp_1, self.get_priority(type_arp), self.get_match(type_arp, ofp_parser, '10.0.0.1', '10.0.0.2'), actions_eth)
            self.add_flow(dp_2, self.get_priority(type_arp), self.get_match(type_arp, ofp_parser, '10.0.0.2', '10.0.0.1'), actions_eth)
            # 2x host
            self.add_flow(dp_1, self.get_priority(type_ip), self.get_match(type_ip, ofp_parser, '10.0.0.2', '10.0.0.1'), actions_host)
            self.add_flow(dp_2, self.get_priority(type_ip), self.get_match(type_ip, ofp_parser, '10.0.0.1', '10.0.0.2'), actions_host)
            self.add_flow(dp_1, self.get_priority(type_arp), self.get_match(type_arp, ofp_parser, '10.0.0.2', '10.0.0.1'), actions_host)
            self.add_flow(dp_2, self.get_priority(type_arp), self.get_match(type_arp, ofp_parser, '10.0.0.1', '10.0.0.2'), actions_host)

    # If new link is detected by LLDP
    @set_ev_cls(event.EventLinkAdd, MAIN_DISPATCHER)
    def link_add_handler(self, ev):
        s1 = ev.link.src
        s2 = ev.link.dst
        self.adjacency[s1.dpid][s2.dpid] = s1.port_no
        self.adjacency[s2.dpid][s1.dpid] = s2.port_no

    # If link connection is deleted
    @set_ev_cls(event.EventLinkDelete, MAIN_DISPATCHER)
    def link_delete_handler(self, ev):
        s1 = ev.link.src
        s2 = ev.link.dst
        # Exception handling if switch already deleted
        try:
            del self.adjacency[s1.dpid][s2.dpid]
            del self.adjacency[s2.dpid][s1.dpid]
        except KeyError:
            pass

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_stats_reply_handler(self, ev):
        switch = ev.msg.datapath
        #if(switch.id in self.dpid_to_mac)
        for p in ev.msg.body:
            self.bandwidths[switch.id][p.port_no] = p.curr_speed

    def get_paths(self, src, dst):
        '''
        Get all paths from src to dst using DFS algorithm
        '''
        if src == dst:
            # host target is on the same switch
            return [[src]]
        paths = []
        stack = [(src, [src])]
        while stack:
            (node, path) = stack.pop()
            for next in set(self.adjacency[node].keys()) - set(path):
                if next is dst:
                    paths.append(path + [next])
                else:
                    stack.append((next, path + [next]))
        print ("Available paths from ", src, " to ", dst, " : ", paths)
        return paths

    def get_link_cost(self, s1, s2):
        #Get the link cost between two switches
        e1 = self.adjacency[s1][s2]
        e2 = self.adjacency[s2][s1]
        bl = min(self.bandwidths[s1][e1], self.bandwidths[s2][e2])
        ew = REFERENCE_BW/bl
        self.logger.info("COST BW: {}".format(ew))
        return ew

    def get_path_cost(self, path):
        '''
        Get the path cost
        '''
        cost = 0
        for i in range(len(path) - 1):
            cost += self.get_link_cost(path[i], path[i+1])
        return cost

    def get_optimal_paths(self, src, dst):
        '''
        Get the n-most optimal paths according to MAX_PATHS
        '''
        paths = self.get_paths(src, dst)
        paths_count = len(paths) if len(
            paths) < MAX_PATHS else MAX_PATHS
        return sorted(paths, key=lambda x: self.get_path_cost(x))[0:(paths_count)]

    def add_ports_to_paths(self, paths, first_port, last_port):
        '''
        Add the ports that connects the switches for all paths
        '''
        paths_p = []
        for path in paths:
            p = {}
            in_port = first_port
            for s1, s2 in zip(path[:-1], path[1:]):
                out_port = self.adjacency[s1][s2]
                p[s1] = (in_port, out_port)
                in_port = self.adjacency[s2][s1]
            p[path[-1]] = (in_port, last_port)
            paths_p.append(p)
        return paths_p

    def generate_openflow_gid(self):
        '''
        Returns a random OpenFlow group id
        '''
        n = random.randint(0, 2**32)
        while n in self.group_ids:
            n = random.randint(0, 2**32)
        return n


    def install_paths(self, src, first_port, dst, last_port, ip_src, ip_dst):

        # printing out
        self.logger.info("----------------------------------------")
        self.logger.info("topology app: {}".format(self.topology_api_app))
        self.logger.info("datapath_list: {}".format(self.datapath_list))
        self.logger.info("arp_table: {}".format(self.arp_table))
        self.logger.info("switches: {}".format(self.switches))
        self.logger.info("hosts: {}".format(self.hosts))
        self.logger.info("multipath_group_ids: {}".format(self.multipath_group_ids))
        self.logger.info("group_ids: {}".format(self.group_ids))
        self.logger.info("adjacency: {}".format(self.adjacency))
        self.logger.info("----------------------------------------")

        computation_start = time.time()
        paths = self.get_optimal_paths(src, dst)
        pw = []
        for path in paths:
            pw.append(self.get_path_cost(path))
            print (path, "cost = ", pw[len(pw) - 1])
        sum_of_pw = sum(pw) * 1.0
        paths_with_ports = self.add_ports_to_paths(paths, first_port, last_port)
        switches_in_paths = set().union(*paths)

        self.logger.info("paths: {}, switches: {}".format(paths, switches_in_paths))

        for node in switches_in_paths:

            dp = self.datapath_list[node]
            ofp = dp.ofproto
            ofp_parser = dp.ofproto_parser

            ports = defaultdict(list)
            actions = []
            i = 0

            for path in paths_with_ports:
                if node in path:
                    in_port = path[node][0]
                    out_port = path[node][1]
                    if (out_port, pw[i]) not in ports[in_port]:
                        ports[in_port].append((out_port, pw[i]))
                i += 1

            for in_port in ports:
                match_ip = ofp_parser.OFPMatch(
                    eth_type=0x0800,
                    ipv4_src=ip_src,
                    ipv4_dst=ip_dst
                )
                match_arp = ofp_parser.OFPMatch(
                    eth_type=0x0806,
                    arp_spa=ip_src,
                    arp_tpa=ip_dst
                )
                out_ports = ports[in_port]
                # print out_ports
                if len(out_ports) > 1:
                    group_id = None
                    group_new = False

                    if (node, src, dst) not in self.multipath_group_ids:
                        group_new = True
                        self.multipath_group_ids[
                            node, src, dst] = self.generate_openflow_gid()
                    group_id = self.multipath_group_ids[node, src, dst]

                    buckets = []
                    # print "node at ",node," out ports : ",out_ports
                    for port, weight in out_ports:
                        bucket_weight = int(round((1 - weight/sum_of_pw) * 10))
                        bucket_action = [ofp_parser.OFPActionOutput(port)]
                        buckets.append(
                            ofp_parser.OFPBucket(
                                weight=bucket_weight,
                                watch_port=port,
                                watch_group=ofp.OFPG_ANY,
                                actions=bucket_action
                            )
                        )
                    if group_new:
                        req = ofp_parser.OFPGroupMod(
                            dp, ofp.OFPGC_ADD, ofp.OFPGT_SELECT, group_id,
                            buckets
                        )
                        dp.send_msg(req)
                    else:
                        req = ofp_parser.OFPGroupMod(
                            dp, ofp.OFPGC_MODIFY, ofp.OFPGT_SELECT,
                            group_id, buckets)
                        dp.send_msg(req)

                    actions = [ofp_parser.OFPActionGroup(group_id)]
                    print("added flow LP1+ @dp: {} to {} ort: {}".format(match_ip, match_arp, out_ports[0][0]))
                    self.add_flow(dp, 32768, match_ip, actions)
                    self.add_flow(dp, 1, match_arp, actions)

                elif len(out_ports) == 1:
                    actions = [ofp_parser.OFPActionOutput(out_ports[0][0])]
                    print("added flow LP1 @dp: {} to {} Port: {}".format(match_ip, match_arp, out_ports[0][0]))
                    self.add_flow(dp, 32768, match_ip, actions)
                    self.add_flow(dp, 1, match_arp, actions)
        print ("Path installation finished in ", time.time() - computation_start)
        return paths_with_ports[0][src][1]

    def handleDataForPlotting(self):
        # saving timestamp
        #self.data_map['startingtime'] = self.startingTime
        if (MININET == True):
            self.logger.info("Plotting Ping Mininet")

            while (self.ping_ready[LOOPBACK_IP] == False):
                # if empty
                self.logger.info("no ping value loppback - waiting 1 sec")
                time.sleep(1)
            try:
                print(self.output)
                loopbackData = self.create_ping_map(self.output[LOOPBACK_IP][0].decode("utf-8").splitlines())
                dt = datetime.datetime.now()
                timeStampStr = dt.strftime('%m_%d_%Y_%H_%M') + '_{}_{}'.format(TESTTYPE, MEASUREMENTTYPE)
                dir = 'data/{}'.format(timeStampStr)
                print("01")
                if not os.path.exists(dir):
                    os.makedirs(dir)
                print("02")
                with open('data/{}/whole_data.json'.format(timeStampStr), 'w') as the_file2:
                    the_file2.write(json.dumps(self.data_map))
                print("03")

                # RTTs
                if (MEASUREMENTTYPE == 'RTT' or  MEASUREMENTTYPE == 'ALL'):

                    print("1")
                    with open('data/{}/RTT.json'.format(timeStampStr), 'w') as the_file11:
                        the_file11.write(json.dumps(self.saved_rtt_to_dpid))
                if (MEASUREMENTTYPE == 'ECHO' or MEASUREMENTTYPE == 'ALL'):
                    print("2")
                    with open('data/{}/RTT_Echo.json'.format(timeStampStr), 'w') as the_file12:
                        the_file12.write(json.dumps(self.saved_echo_rtt_to_dpid))
                    print("2")
                    with open('data/{}/Sw2Con.json'.format(timeStampStr), 'w') as the_file13:
                        the_file13.write(json.dumps(self.saved_echo_timeToSw))
                    print("2")
                    with open('data/{}/Con2Sw.json'.format(timeStampStr), 'w') as the_file14:
                        the_file14.write(json.dumps(self.saved_echo_timeToC))
                if (MEASUREMENTTYPE == 'PORTSTATS'or  MEASUREMENTTYPE == 'ALL'):
                    print("3")
                    with open('data/{}/Port_Stats.json'.format(timeStampStr), 'w') as the_file15:
                        the_file15.write(json.dumps(self.saved_rtt_to_dpid_portStats))
            except Exception as e:
                self.logger.info("EXCEPTION Output: {}, {}".format(self.output.keys(), self.data_map.keys()))
                self.logger.info("EXCEPTION Mininet: {}".format(e))

            #matrix_np.plot(self.data_map, self.startingTime, self.saved_rtt_to_dpid,
            #               self.saved_echo_rtt_to_dpid, self.saved_echo_timeToSw, self.saved_echo_timeToC,
            #               loopbackData, loopbackData)
        else:
            self.logger.info("Plotting Ping Rasperry")

            # saving the data

            while (self.ping_ready[SWITCH_IP_1] == False) or (self.ping_ready[SWITCH_IP_2] == False):
                # if empty
                self.logger.info("ping_ready map: {}".format(self.ping_ready))
                self.logger.info("no ping value rasp- waiting 1 sec")
                time.sleep(1)
            try:
                dt = datetime.datetime.now()
                timeStampStr = dt.strftime('%m_%d_%Y_%H_%M')+ '_{}_{}'.format(TESTTYPE, MEASUREMENTTYPE)
                dir = 'data/{}'.format(timeStampStr)

                if not os.path.exists(dir):
                    os.makedirs(dir)

                # saving data
                # with open('output_ping_whole.txt', 'a') as the_file:
                #    the_file.write(json.dumps(self.output))
                with open('data/{}/whole_data.json'.format(timeStampStr), 'w') as the_file2:
                    the_file2.write(json.dumps(self.data_map))

                print("Writing ping data")
                sw1data = self.create_ping_map(self.output[SWITCH_IP_1][0].decode("utf-8").splitlines())
                sw2data = self.create_ping_map(self.output[SWITCH_IP_2][0].decode("utf-8").splitlines())

                # saving data
                with open('data/{}/output_ping_1.json'.format(timeStampStr), 'w') as the_file3:
                    the_file3.write(json.dumps(sw1data))
                with open('data/{}/output_ping_2.json'.format(timeStampStr), 'w') as the_file4:
                    the_file4.write(json.dumps(sw2data))
                #matrix_np.plot(self.data_map, self.startingTime, self.saved_rtt_to_dpid,
                #               self.saved_echo_rtt_to_dpid, self.saved_echo_timeToSw,
                #               self.saved_echo_timeToC,
                #               sw1data, sw2data)
            except Exception as e:
                with open('data/{}/whole_data_output.json'.format(timeStampStr), 'w') as the_file1:
                    the_file1.write(str(self.output))
                self.logger.info("EXCEPTION Output: {}".format(self.output.keys()))
                self.logger.info("EXCEPTION Rasperry: {}".format(e))
                
            # for the ping between the switches
            if (SWITCH_IP_1_inBetween in self.ping_ready.keys()) and (SWITCH_IP_2_inBetween in self.ping_ready.keys()):
                while (self.ping_ready[SWITCH_IP_1_inBetween] == False)  or (self.ping_ready[SWITCH_IP_2_inBetween] == False):
                    # if empty                    
                    self.logger.info("no ping value in between- waiting 1 sec: {}".format(self.ping_ready))
                    time.sleep(1)
                try:
                    sw1_in_between_data = self.create_ping_map(self.output[SWITCH_IP_1_inBetween])
                    sw2_in_between_data = self.create_ping_map(self.output[SWITCH_IP_2_inBetween])
                    print("Got data ping in between")
                    # saving data
                    with open('data/{}/output_ping_1_inBetween.json'.format(timeStampStr), 'w') as the_file5:
                        the_file5.write(json.dumps(sw1_in_between_data))
                    with open('data/{}/output_ping_2_inBetween.json'.format(timeStampStr), 'w') as the_file6:
                        the_file6.write(json.dumps(sw2_in_between_data))
                    print("Wrote data ping in between")
                except Exception as e:
                    #with open('whole_data.txt', 'w') as the_file1:
                    #    the_file1.write(str(self.output))
                    self.logger.info("EXCEPTION Output In between: {}".format(self.output.keys()))
                    self.logger.info("EXCEPTION len1 In between: {}".format(len(self.output[SWITCH_IP_1_inBetween])))
                    self.logger.info("EXCEPTION len2 In between: {}".format(len(self.output[SWITCH_IP_2_inBetween])))
                    self.logger.info("EXCEPTION Full In between: {}".format(e))

            # TODO: kick out socket
            #while self.socketReady[SWITCH_IP_1] == False or self.socketReady[SWITCH_IP_2] == False:
            #    # if empty
            #    self.logger.info("no ping value - waiting 1 sec")
            #    time.sleep(1)
            #self.logger.info("In Socket !!!!!!!!!!!!!!!!")
            #try:
            #    if(len(self.socket_output.keys())>0):
            #        with open('data/{}/output_socket_1.txt'.format(timeStampStr), 'w') as the_file7:
            #            the_file7.write(json.dumps(self.socket_output[SWITCH_IP_1]))
            #        with open('data/{}/output_socket_2.txt'.format(timeStampStr), 'w') as the_file8:
            #            the_file8.write(json.dumps(self.socket_output[SWITCH_IP_2]))
            #except Exception as e:
            #    self.logger.info("EXCEPTION Socket: {}".format(e))
            # if lantencchanging - pings should be ready
            
            if TESTTYPE == 'CHANGINGLAT' or TESTTYPE == 'CHANGINGLATTOSHOWDIFFERENCE' or TESTTYPE == 'ONELONGTIME' or TESTTYPE == 'CHANGINGLATCONTROLLER':
                try:
                    with open('data/{}/output_changingLat_1.txt'.format(timeStampStr), 'w') as the_file9:
                        the_file9.write(json.dumps(self.changingLatMap[SWITCH_IP_1_2]))
                    with open('data/{}/output_changingLat_2.txt'.format(timeStampStr), 'w') as the_file10:
                        the_file10.write(json.dumps(self.changingLatMap[SWITCH_IP_2_2]))
                except Exception as e:
                    self.logger.info("EXCEPTION Socket: {}".format(e))

            if(TESTTYPE == 'IPERF' and len(list(self.backlog.keys()))>0):
                try:
                    with open('data/{}/output_backlog_1.txt'.format(timeStampStr), 'w') as the_fileab1:
                        the_fileab1.write(json.dumps(self.backlog[SWITCH_IP_1_2]))
                    with open('data/{}/output_backlog_2.txt'.format(timeStampStr), 'w') as the_fileab2:
                        the_fileab2.write(json.dumps(self.backlog[SWITCH_IP_2_2]))
                except Exception as e:
                    self.logger.info("EXCEPTION Backlock: {}".format(e))
                try:
                    with open('data/{}/output_dropped_1.txt'.format(timeStampStr), 'w') as the_fileabc1:
                        the_fileabc1.write(json.dumps(self.packets_drop[SWITCH_IP_1_2]))
                    with open('data/{}/output_dropped_2.txt'.format(timeStampStr), 'w') as the_fileabc2:
                        the_fileabc2.write(json.dumps(self.packets_drop[SWITCH_IP_2_2]))
                except Exception as e:
                    self.logger.info("EXCEPTION dropped: {}".format(e))

            # RTTs
            if (MEASUREMENTTYPE == 'RTT' or MEASUREMENTTYPE == 'ALL' ):
                with open('data/{}/RTT.txt'.format(timeStampStr), 'w') as the_file11:
                    the_file11.write(json.dumps(self.saved_rtt_to_dpid))
            if(MEASUREMENTTYPE == 'ECHO' or MEASUREMENTTYPE == 'ALL'):
                with open('data/{}/RTT_Echo.txt'.format(timeStampStr), 'w') as the_file12:
                    the_file12.write(json.dumps(self.saved_echo_rtt_to_dpid))

                with open('data/{}/Sw2Con.txt'.format(timeStampStr), 'w') as the_file13:
                    the_file13.write(json.dumps(self.saved_echo_timeToSw))

                with open('data/{}/Con2Sw.txt'.format(timeStampStr), 'w') as the_file14:
                    the_file14.write(json.dumps(self.saved_echo_timeToC))
            if(MEASUREMENTTYPE == 'PORTSTATS' or MEASUREMENTTYPE == 'ALL' ):
                with open('data/{}/Port_Stats.txt'.format(timeStampStr), 'w') as the_file15:
                    the_file15.write(json.dumps(self.saved_rtt_to_dpid_portStats))

        print("Finished printing plot data")
        self.allreadyPlotted = True

# Kick out
    def monitor_sockets(self):
        if MININET == False:
            self.logger.info("monitoring socket started 1")
            # maybe kick out
            # installing server over safe timesync conn
            hub.spawn(self.installTcpSocketServer, SWITCH_IP_1_2)
            hub.spawn(self.installTcpSocketServer, SWITCH_IP_2_2)
            #time.sleep(1)
            hub.spawn(self.installTcpSocketClient, SWITCH_IP_1)
            hub.spawn(self.installTcpSocketClient, SWITCH_IP_2)
    def installTcpSocketServer(self, hostIP):
            # new ssh client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostIP, username='pi', password='gameover')
            ssh.exec_command("sudo python ts.py ")
    def installTcpSocketClient(self, host):
        time.sleep(ADDITIONAL_WAITING_TIME)
        s = socket.socket()  # Create a socket object
        port = 12345  # Reserve a port for your service.
        self.socket_output[host] = []
        t_monitoring = 0.5
        socketSteps = int((self.timeTillPlot) / t_monitoring - 2)
        self.socketReady[host] = False
        self.logger.info("monitoring socket client started")
        s.connect((host, port))
        for i in range(socketSteps):
            t1 = time.time()
            s.send('ts'.encode("utf-8"))
            t = float(s.recv(1024))
            t2 = time.time()
            # in ms
            totalRTT = (t2 - t1) * 1000
            TC2Sw = (t - t1) * 1000
            TSw2C = (t2 - t) * 1000
            time.sleep(t_monitoring)

            socketElement = {}
            socketElement['Ts'] = t1
            socketElement['TC2Sw'] = TC2Sw
            socketElement['TSw2C'] = TC2Sw
            self.socket_output[host].append(socketElement)

        s.close()  # Close the socket when done
        self.socketReady[host] = True

        def install_path(self, controller, chosenPath, first_port, last_port, ip_src, ip_dst, type):

            path = self.add_ports_to_path(controller, chosenPath, first_port, last_port)
            #switches_in_paths = set().union(*chosenPath)

            for node in chosenPath:
                dp = controller.dpidToDatapath[node]
                ofp = dp.ofproto
                ofp_parser = dp.ofproto_parser
                ports = defaultdict(list)
                actions = []

                if node in path:
                    in_port = path[node][0]
                    out_port = path[node][1]
                    if out_port not in ports[in_port]:
                        ports[in_port].append(out_port)

                for in_port in ports:
                    out_ports = ports[in_port]
                    actions = [ofp_parser.OFPActionOutput(out_ports[0])]
                    controller.add_flow(dp, self.get_priority(type), self.get_match(type, ofp_parser, ip_src, ip_dst), actions)

    def get_match(self, type, ofp_parser, ip_src, ip_dst):
        if type == 'ipv4':
            match_ip = ofp_parser.OFPMatch(
                eth_type=0x0800,
                ipv4_src=ip_src,
                ipv4_dst=ip_dst
            )
            return match_ip
        if type == 'arp':
            match_arp = ofp_parser.OFPMatch(
                eth_type=0x0806,
                arp_spa=ip_src,
                arp_tpa=ip_dst
            )
            return match_arp

    def get_priority(self, type):
        if type == 'ipv4':
            return 1
        if type == 'arp':
            return 32768
        return 32768