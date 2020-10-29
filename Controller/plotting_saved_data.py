import plotting
import json

################## getting data ##################################
path = "data/10_29_2020_18_44_IPERF_ECHORTT/"
mininet = False
pingdata1 = {}
pingdata2 = {}
pingdata_inbetween1 = {}
pingdata_inbetween2 = {}
socketdata1 = {}
socketdata2 = {}
datamap = {}
saved_rtt_to_dpid={}
saved_echo_rtt_to_dpid={}
saved_echo_timeToSw={}
saved_echo_timeToC={}
saved_port_stats={}
datamap={}

saved_backlog1 = {}
saved_backlog2 = {}

saved_dropped1 = {}
saved_dropped2 = {}

if(mininet == False):
    # open ping data
    #pingdata in between
    with open(path + "output_ping_1_inBetween.json","r") as f3:
        pingdata_inbetween1 = json.load(f3)
        #print(pingdata_inbetween1)
    f3.close()
    with open(path + "output_ping_2_inBetween.json","r") as f4:
        pingdata_inbetween2 = json.load(f4)
        #print(pingdata_inbetween2)
    f4.close()
    # TODO: kick out - socketdata
    #with open(path + "output_socket_1.txt", "r") as f5:
    #    socketdata1 = json.load(f5)
    #    # print(socketdata1)
    #f5.close()
    #with open(path + "output_socket_2.txt", "r") as f6:
    #    socketdata2 = json.load(f6)
    #    # print(socketdata2)
    #f6.close()
    if 'IPERF' in path:
        with open(path + "output_backlog_1.json", "r") as f15:
            saved_backlog1 = json.load(f15)
        f15.close()
        with open(path + "output_backlog_2.json", "r") as f16:
            saved_backlog2 = json.load(f16)
        f16.close()
        with open(path + "output_dropped_1.json", "r") as f17:
            saved_dropped1 = json.load(f17)
        f17.close()
        with open(path + "output_dropped_2.json", "r") as f18:
            saved_dropped2 = json.load(f18)
        f18.close()
    # latency changing rasperry pi
with open(path + "output_ping_1.json","r") as f1:
    pingdata1 = json.load(f1)
    #print(pingdata1)
f1.close()
with open(path + "output_ping_2.json","r") as f2:
    pingdata2 = json.load(f2)
    #print(pingdata2)
f2.close()
#if(True==False):
if  'ALL' in path:
    # RTTimes
    with open(path + "RTT.json", "r") as f10:
        saved_rtt_to_dpid = json.load(f10)
        # print(saved_rtt_to_dpid)
    f10.close()
if ('ECHO' in path and 'RTT' not in path) or 'ALL' in path:
    with open(path + "RTT_Echo.json", "r") as f11:
        saved_echo_rtt_to_dpid = json.load(f11)
        # print(saved_echo_rtt_to_dpid)
    f11.close()
    with open(path + "Sw2Con.json", "r") as f12:
        saved_echo_timeToSw = json.load(f12)
        # print(saved_echo_timeToSw)
    f12.close()
    with open(path + "Con2Sw.json", "r") as f13:
        saved_echo_timeToC = json.load(f13)
        # print(saved_echo_timeToC)
    f13.close()
if 'PORT' in path or 'ALL' in path:
    with open(path + "Port_Stats.json", "r") as f14:
        saved_port_stats = json.load(f14)
        # print(saved_echo_timeToC)
    f14.close()


#if(True==False):
# latencyMap
#if(False==True):
with open(path + "whole_data.json","r") as fx:
    datamap = json.load(fx)
fx.close()
# startingtime
if(mininet == False):
    # get first key
    key1 = list(datamap.keys())[0]
    key2 = list(datamap[key1].keys())[0]
    startingtime = datamap[key1][key2]['latencyEchoRTT'][0]["timestamp"]
else:
    startingtime = float(str(pingdata1[list(pingdata1.keys())[0]]))

# Changing latency controller !!!
#plotting.plotLatencyChangeCONTROLLERRaspi(datamap,startingtime,pingdata_inbetween1,pingdata_inbetween2, saved_echo_timeToC, saved_echo_timeToSw, saved_echo_rtt_to_dpid, pingdata1, pingdata2)

# FUNCTIONS - adding BW with backlog
plotting.plotLatencyRisingBandwithRaspi(datamap,startingtime, pingdata_inbetween1, pingdata_inbetween2, saved_backlog1, saved_backlog2, saved_dropped1, saved_dropped2)

# difference diagram
#plotting.plotDifferenceEchoRTT(saved_rtt_to_dpid,saved_echo_rtt_to_dpid,startingtime)

# NORMAL!:
#plotting.plotLatComp(datamap, startingtime, pingdata_inbetween1, pingdata_inbetween2)

# one measuremnt
#plotting.plotLatencyChangeStatsOne_withping(datamap,startingtime,'latencyEchoRTT',pingdata_inbetween1,pingdata_inbetween2)

# else:
#     first = datamap[list(datamap.keys())[0]]
#     second = first[list(first.keys())[0]]
#     bwVal = second['bw'][0]
#     startingtime = bwVal['timestamp']
# print(startingtime)
#startingtime = float(str(pingdata1[list(pingdata1.keys())[0]]))
#print(saved_rtt_to_dpid)
##############################Plotting##########################
# boxplot difference RTT, RTTEcho, Ping
# difference diagram
#plotting.plotDifferenceEchoRTT(saved_rtt_to_dpid,saved_echo_rtt_to_dpid,startingtime)
# compare balkendiagramm
# showing plot
#plotting.plotLatencyChangeAllRaspi(datamap,startingtime)
# one measuremnt
#plotting.plotLatencyChangeStatsOne_withping(datamap,startingtime,'latencyEchoRTT',pingdata_inbetween1,pingdata_inbetween2)
# mininet latency change

#print("STARTINGTIME: {}".format(startingtime))


#plotting.plotLatencyChangeAllRaspi(datamap,startingtime)

# FUNCTIONS - 
# FUNCTIONS - mininet_changing_Lat
#plotting.plotLatencyChangeAllMininet(datamap,startingtime, path)


# Bi functions - compare Socket with echo
#plotting.timeToSwCCompare(saved_echo_rtt_to_dpid, saved_echo_rtt_to_dpid, saved_echo_timeToSw, saved_echo_timeToC, socketdata1, socketdata2,pingdata1, pingdata2)
# Bi functions - compare RTT, RTTEcho, Ping, Socket response times
#plotting.plotRTTComp(datamap, startingtime, saved_rtt_to_dpid, saved_echo_rtt_to_dpid, pingdata1, pingdata2, socketdata1, socketdata2)

# Between 2 raspies long time
# plotting.plotLatencyChangeStatsOne_withping(datamap,startingtime,'latencyEcho',pingdata_inbetween1,pingdata_inbetween2)
#plotting.oneLongTimeMininet(datamap,startingtime, path)

#plotting.plotRTTCompMininet(datamap, startingtime, saved_rtt_to_dpid, saved_echo_rtt_to_dpid, pingdata1, pingdata2)

# NORMAL!:
#plotting.plotLatComp(datamap, startingtime, pingdata_inbetween1, pingdata_inbetween2)
#plotting.plotLatCompMininet(datamap, startingtime, path)

#plotting.getAdjMatrix(datamap)
