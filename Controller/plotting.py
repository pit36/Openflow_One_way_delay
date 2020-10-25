import matplotlib.pyplot as plt
import numpy as np
import json
import collections
import style
import matplotlib.ticker as ticker
from matplotlib.font_manager import FontProperties
from scipy.stats import t

def getxyArrayLatency(xArray, yArray, dataLatency, timeTillStart):
    #print('datalat: {}'.format(dataLatency))
    for i in dataLatency:

        timeDiff = i['timestamp'] - timeTillStart
        if (timeDiff < 0):
            timeDiff = 0.00000001
        xArray.append(timeDiff)
        yArray.append(i['value'])

def getxyArrayLatency2(xArray, yArray, dataLatency, timeTillStart):
    #print('datalat: {}'.format(dataLatency))
    for i in dataLatency:

        timeDiff = i['ts'] - timeTillStart
        if (timeDiff < 0):
            timeDiff = 0.00000001
        xArray.append(timeDiff)
        yArray.append(i['value'])

def getxyArrayLatencyNoTs(xArray, yArray, dataLatency, timeTillStart, divide=False):
    #print('datalat: {}'.format(dataLatency))
    for i in dataLatency:
        x = list(i.keys())[0]
        xdiff = float(x)-timeTillStart
        if (xdiff > 0):
            xArray.append(xdiff)
            if(divide):
                yArray.append((float(i[x]) * 1000)/2)
            else:
                yArray.append(float(i[x])*1000)

def plotLatencyChangeRTT(dataMap, timeTillStart):

    fig1 = plt.figure()
    ax11 = fig1.add_subplot(211)
    ax12 = fig1.add_subplot(212)

    # labels
    ax11.set_xlabel('time (s)')
    ax11.set_ylabel('latency (ms)')
    ax12.set_xlabel('time (s)')
    ax11.set_ylabel('(delta) latency (ms)')

    fig2 = plt.figure()
    ax21 = fig2.add_subplot(211)
    ax22 = fig2.add_subplot(212)

    # labels
    ax12.set_xlabel('time (s)')
    ax12.set_ylabel('latency (ms)')
    ax22.set_xlabel('time (s)')
    ax22.set_ylabel('(delta) latency (ms)')

    ax11.title.set_text('Latency from 1 to 2')
    ax21.title.set_text('Latency from 2 to 1')

    array1to2 = []
    array2to1 = []

    # get measured latency values
    xArray1 = []
    yArray1 = []
    xArray2 = []
    yArray2 = []

    getxyArrayLatency(xArray1,yArray1,dataMap[1][2]['latency'], timeTillStart)
    getxyArrayLatency(xArray2,yArray2,dataMap[2][1]['latency'], timeTillStart)

    ax11.plot(xArray1, yArray1, 'r', label = 'Measured Latency')
    ax21.plot(xArray2, yArray2, 'r', label = 'Measured Latency')

    # reference values
    data = json.load(open('log_latency_change.json'))
    # print(data)
    for d in data:
        timestamp = d['time']
        if (timestamp < timeTillStart):
            timestamp = timeTillStart
        for dd in d['data']:
            # from 1 to 2
            #print(dd)
            if "s1" in dd['interface']:
                objChange = {}
                objChange['time'] = timestamp - timeTillStart
                if (objChange['time'] < 0):
                    print('LOWER THEN 0')
                    objChange['time'] = 0.000000000000000001
                objChange['value'] = dd['latency']
                array2to1.append(objChange)

            elif "s2" in dd['interface']:
                objChange = {}
                objChange['time'] = timestamp - timeTillStart
                if (objChange['time'] < 0):
                    objChange['time'] = 0.000000000000000001
                objChange['value'] = dd['latency']
                array1to2.append(objChange)

    xArrayChange1To2 = []
    yArrayChange1To2 = []
    xArrayChange2To1 = []
    yArrayChange2To1 = []

    # changes to xarray/yarray
    for oneToTwo in range(len(array1to2)):
        if (oneToTwo > 0):
            xArrayChange1To2.append(array1to2[oneToTwo]['time'])
            yArrayChange1To2.append(array1to2[oneToTwo - 1]['value'])
        xArrayChange1To2.append(array1to2[oneToTwo]['time'])
        yArrayChange1To2.append(array1to2[oneToTwo]['value'])

    xArrayChange1To2.append(xArray1[-1])
    yArrayChange1To2.append(array1to2[-1]['value'])

    ax11.plot(xArrayChange1To2, yArrayChange1To2, 'b', label = 'Set latency')

    for twoToOne in range(len(array2to1)):
        if (twoToOne > 0):
            xArrayChange2To1.append(array2to1[twoToOne]['time'])
            yArrayChange2To1.append(array2to1[twoToOne-1]['value'])
        xArrayChange2To1.append(array2to1[twoToOne]['time'])
        yArrayChange2To1.append(array2to1[twoToOne]['value'])

    xArrayChange2To1.append(xArray2[-1])
    yArrayChange2To1.append(array2to1[-1]['value'])

    ax21.plot(xArrayChange2To1, yArrayChange2To1, 'b', label = 'Set latency')

    # plot ping latency
    xPing1To2 = []
    xPing2To1 = []
    yPing1To2 = []
    yPing2To1 = []

    # open the files
    with open('ping_h1_h2.csv') as f:
        lines1To2 = f.readlines()
    with open('ping_h2_h1.csv') as f:
        lines2To1 = f.readlines()

    # fill axises
    for oneToTwo in lines1To2:
        splittedString = oneToTwo.split(";")
        latencyValue = splittedString[0]
        timestamp = float(splittedString[1]) - timeTillStart
        if (timestamp < 0):
            timestamp = 0
        xPing1To2.append(timestamp)
        yPing1To2.append(float(latencyValue) / 2)

    for twoToOne in lines2To1:
        splittedString = twoToOne.split(";")
        latencyValue = splittedString[0]
        timestamp = float(splittedString[1]) - timeTillStart
        if (timestamp < 0):
            timestamp = 0
        xPing2To1.append(timestamp)
        yPing2To1.append(float(latencyValue) / 2)

    ax11.plot(xPing1To2, yPing1To2, 'g', label='Ping')
    ax21.plot(xPing2To1, yPing2To1, 'g', label='Ping')

    y1Diff = []
    x1Diff = []
    y2Diff = []
    x2Diff = []

    #add difference
    for i1 in range(len(yArray1)):
        xValue = xArray1[i1]
        for j1 in range(len(xArrayChange1To2)):
            # in which reference interval
            if(xValue > xArrayChange1To2[j1] and xValue < xArrayChange1To2[j1+1]):
                # relative difference
                y1Diff.append(yArray1[i1] - yArrayChange1To2 [j1])
                x1Diff.append(xValue)
        # check to which reference
    for i2 in range(len(yArray2)):
        xValue = xArray2[i2]
        for j2 in range(len(xArrayChange2To1)):
            # in which reference interval
            if (xValue > xArrayChange2To1[j2] and xValue < xArrayChange2To1[j2 + 1]):
                # relative difference
                y2Diff.append(yArray2[i2] - yArrayChange2To1[j2])
                x2Diff.append(xValue)
        #yValue = xArray2[i2]
        # check to which refer

    ax11.grid()
    ax21.grid()

    ax12.plot(x1Diff, y1Diff)
    ax22.plot(x2Diff, y2Diff)

    ax12.grid()
    ax22.grid()

    # check if data time is in intervall
    fig1.savefig("first.svg")
    fig2.savefig("second.svg")
    plt.show()

def plotLatencyRisingBandwith(dataMap, timeTillStart):

    key1 = list(dataMap.keys())[0]
    key2 = list(dataMap.keys())[1]

    fig1 = plt.figure()
    ax11 = fig1.add_subplot(211)
    ax12 = fig1.add_subplot(212)

    fig2 = plt.figure()
    ax21 = fig2.add_subplot(211)
    ax22 = fig2.add_subplot(212)

    ax11.title.set_text('Latency from 1 to 2')
    ax21.title.set_text('Latency from 2 to 1')

    array1to2 = []
    array2to1 = []

    # get measured latency values
    # dataLatency =dataMap[1][2]['latency']
    xArray1 = []
    yArray1 = []
    xArray2 = []
    yArray2 = []

    if (len(dataMap[key1][key2]['latency']) > 0):
        getxyArrayLatency(xArray1, yArray1, dataMap[key1][key2]['latency'], timeTillStart)
        getxyArrayLatency(xArray2, yArray2, dataMap[key2][key1]['latency'], timeTillStart)
    else:
        getxyArrayLatency(xArray1, yArray1, dataMap[key1][key2]['latencyEcho'], timeTillStart)
        getxyArrayLatency(xArray2, yArray2, dataMap[key2][key1]['latencyEcho'], timeTillStart)

    ax11.plot(xArray1, yArray1, 'r')
    ax21.plot(xArray2, yArray2, 'r')

    # plot ping latency
    xPing1To2 = []
    xPing2To1 = []
    yPing1To2 = []
    yPing2To1 = []

    # open the files
    with open('ping_h1_h2.csv') as f:
        lines1To2 = f.readlines()
    with open('ping_h2_h1.csv') as f:
        lines2To1 = f.readlines()

    # fill axises
    for oneToTwo in lines1To2:
        splittedString = oneToTwo.split(";")
        latencyValue = splittedString[0]
        timestamp = float(splittedString[1]) - timeTillStart
        if (timestamp < 0):
            timestamp = 0
        xPing1To2.append(timestamp)
        yPing1To2.append(float(latencyValue) / 2)

    for twoToOne in lines2To1:
        splittedString = twoToOne.split(";")
        latencyValue = splittedString[0]
        timestamp = float(splittedString[1]) - timeTillStart
        if (timestamp < 0):
            timestamp = 0
        xPing2To1.append(timestamp)
        yPing2To1.append(float(latencyValue) / 2)

    ax11.plot(xPing1To2, yPing1To2, 'g')
    ax21.plot(xPing2To1, yPing2To1, 'g')

    # Bandwith plotting
    xArrayBw1 = []
    yArrayBw1 = []
    xArrayBw2 = []
    yArrayBw2 = []
    getxyArrayLatency(xArrayBw1, yArrayBw1, dataMap[1][2]['bw'], timeTillStart)
    getxyArrayLatency(xArrayBw2, yArrayBw2, dataMap[2][1]['bw'], timeTillStart)
    ax12.plot(xArrayBw1, yArrayBw1, 'r')
    ax22.plot(xArrayBw2, yArrayBw2, 'r')

    ax11.grid()
    ax21.grid()
    ax12.grid()
    ax22.grid()

    # check if data time is in intervall
    fig1.savefig("first.svg")
    fig2.savefig("second.svg")
    plt.show()

def plotLatencyRisingBandwithRaspi(dataMap, timeTillStart, pingData1, pingData2,saved_backlog1,saved_backlog2, saved_dropped1,saved_dropped2):

    key1 = list(dataMap.keys())[0]
    key2 = list(dataMap.keys())[1]

    #fig1 = plt.figure()
    #ax11 = fig1.add_subplot(311)
    #ax12 = fig1.add_subplot(312)
    #ax13 = fig1.add_subplot(313)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    fig2 = plt.figure()

    ax21 = fig2.add_subplot(311)
    ax22 = fig2.add_subplot(312)
    ax23 = fig2.add_subplot(313)

    # get ping values
    # get ping values
    xArrayPing1 = []
    yArrayPing1 = []
    xArrayPing2 = []
    yArrayPing2 = []
    print(pingData1)
    getPingValues(xArrayPing1, yArrayPing1, pingData1, timeTillStart, False)
    getPingValues(xArrayPing2, yArrayPing2, pingData2, timeTillStart, False)

    ax21.plot(xArrayPing2, yArrayPing2, '+',color='royalblue', label='Measured Ping')

    # get queue lenght
    xArrayQueue1 = []
    yArrayQueue1 = []
    getxyArrayLatency2(xArrayQueue1, yArrayQueue1, saved_backlog1, timeTillStart)
    ax23.plot(xArrayQueue1, yArrayQueue1, 'x-',color= 'royalblue', label='Queue Lenght')

    # get dropped lenght
    xArrayDropped1 = []
    yArrayDropped1 = []
    getxyArrayLatency2(xArrayDropped1, yArrayDropped1, saved_dropped1, timeTillStart)
    #ax23a = ax23.twinx()
    ax23.plot(xArrayDropped1, yArrayDropped1, '+-',color='tomato', label='Dropped Packets')

    # get measured latency values
    # dataLatency =dataMap[1][2]['latency']
    xArray1 = []
    yArray1 = []
    xArray2 = []
    yArray2 = []

    if (len(dataMap[key1][key2]['latency']) > 0):
        getxyArrayLatency(xArray1, yArray1, dataMap[key1][key2]['latency'], timeTillStart)
        getxyArrayLatency(xArray2, yArray2, dataMap[key2][key1]['latency'], timeTillStart)
    else:
        getxyArrayLatency(xArray1, yArray1, dataMap[key1][key2]['latencyEcho'], timeTillStart)
        getxyArrayLatency(xArray2, yArray2, dataMap[key2][key1]['latencyEcho'], timeTillStart)

    #ax11.plot(xArray1, yArray1, label = 'Measured Latency')
    ax21.plot(xArray2, yArray2,'x-', color= 'tomato', label = 'Measured Latency')

    # plot ping latency
    xPing1To2 = []
    xPing2To1 = []
    yPing1To2 = []
    yPing2To1 = []

    # Bandwith plotting
    xArrayBw1 = []
    yArrayBw1 = []
    xArrayBw2 = []
    yArrayBw2 = []

    getxyArrayLatency(xArrayBw1, yArrayBw1, dataMap[key1][key2]['bw'], timeTillStart)
    getxyArrayLatency(xArrayBw2, yArrayBw2, dataMap[key2][key1]['bw'], timeTillStart)

    # Umrechnung in byte
    yArrayBw11 = map(lambda x: (x * 8)/(1024), yArrayBw1)
    yArrayBw21 = map(lambda x: (x * 8)/(1024), yArrayBw2)

    ax22.plot(xArrayBw1, yArrayBw11, 'x-',color= 'royalblue', label = 'Bandwith')

    ax21.grid()
    ax22.grid()
    ax23.grid()
    tick_spacing = 10
    ax21.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

    # labels
    ax21.set_ylabel(r'Latency [ms]', fontsize = 18)
    ax22.set_ylabel(r'Traffic [Mbit/s]', fontsize = 18)
    ax23.set_ylabel(r'Packets', fontsize = 18)
    ax23.set_xlabel(r'Time [s]', fontsize = 18)

    ax21.set_xlim(12, 63)
    ax22.set_xlim(12, 63)
    ax23.set_xlim(12, 63)

    ax22.set_ylim(0, 100)
    #style.setup3()
    legend1 = ax23.legend(loc='upper left', fontsize = 20)
    legend2 = ax21.legend(loc='upper left', fontsize = 20)

    # check if data time is in intervall
    #fig1.savefig("first.svg")
    #fig2.savefig("bw_raising_1.pdf", format='pdf', bbox_inches='tight')
    plt.show()

def plotDifferenceEchoRTT(saved_rtt_to_dpid, saved_echo_rtt_to_dpid, timeTillStart):
    fig1 = plt.figure()
    ax11 = fig1.add_subplot(211)
    ax12 = fig1.add_subplot(212)

    fig2 = plt.figure()
    ax21 = fig2.add_subplot(211)
    ax22 = fig2.add_subplot(212)

    ax11.title.set_text('xxx from 1 to 2')
    ax21.title.set_text('xxx from 2 to 1')

    ax12.set_xlabel('time (s)')

    xArray  = []
    yArray1 = []
    yArray2 = []
    yArray3 = []
    #print(saved_rtt_to_dpid)
    for i in range(len(saved_rtt_to_dpid[list(saved_rtt_to_dpid.keys())[0]])):

        elementRTT = saved_rtt_to_dpid[list(saved_rtt_to_dpid.keys())[0]][i-1]
        elementEcho = saved_echo_rtt_to_dpid[list(saved_echo_rtt_to_dpid.keys())[0]][i-1]

        timeDiff = float(list(elementRTT.keys())[0]) - timeTillStart
        #print(elementRTT.keys())
        if (timeDiff < 0):
            timeDiff = 0.00000001
        xArray.append(timeDiff)
        rttValue= list(elementRTT.values())[0]*1000
        echoValue = list(elementEcho.values())[0]*1000
        yArray1.append(rttValue)
        yArray2.append(echoValue)
        yArray3.append(rttValue - echoValue)

    # get average y
    avg = np.average(yArray3)
    yAvgArray = [avg, avg]
    xAvgArray = [0, xArray[-1]]

    ax11.plot(xArray, yArray1, 'r', label='RTT')
    ax11.plot(xArray, yArray2, 'b', label='Echo RTT')
    ax12.plot(xArray, yArray3, 'g')
    ax12.plot(xAvgArray,yAvgArray,  'r')
    xxArray = []
    yyArray1 = []
    yyArray2 = []
    yyArray3 = []

    for i in range(len(saved_rtt_to_dpid[list(saved_rtt_to_dpid.keys())[1]])):

        elementRTT = saved_rtt_to_dpid[list(saved_rtt_to_dpid.keys())[1]][i]
        elementEcho = saved_echo_rtt_to_dpid[list(saved_echo_rtt_to_dpid.keys())[1]][i]

        timeDiff = float(list(elementRTT.keys())[0]) - timeTillStart
        #print(elementRTT.keys())
        if (timeDiff < 0):
            timeDiff = 0.00000001
        xxArray.append(timeDiff)
        rttValue= list(elementRTT.values())[0]*1000
        echoValue = list(elementEcho.values())[0]*1000
        yyArray1.append(rttValue)
        yyArray2.append(echoValue)
        yyArray3.append(rttValue - echoValue)

    # get average y
    avg = np.average(yyArray3)
    yyAvgArray = [avg, avg]
    xxAvgArray = [0,xxArray[-1]]

    ax21.plot(xxArray, yyArray1, 'r', label='RTT')
    ax21.plot(xxArray, yyArray2, 'b', label='Echo RTT')
    ax22.plot(xxArray, yyArray3, 'g')
    ax22.plot(xxAvgArray, yyAvgArray, 'r')
    legend = ax11.legend(loc='best', shadow=True)
    legend2 = ax21.legend(loc='best', shadow=True)

    plt.show()

def plotLatencyChangeAllMininet(dataMap, timeTillStart, path):
    print("TIMETILLSTART: {}".format(timeTillStart))

    fig1 = plt.figure(figsize=(15, 5))
    ax11 = fig1.subplots()
    # = fig1.add_subplot(211)
    fig2  = plt.figure(figsize=(15, 5))
    ax21 = fig2.subplots()
    # = fig2.add_subplot(211)
    array1to2 = []
    array2to1 = []
    style.setup()
    #get keys
    key1 = list(dataMap.keys())[0]
    key2 = list(dataMap.keys())[1]
    # if rtt measured!
    lastvalueLat = 10000.0
    if(len(dataMap[key1][key2]['latency'])>0):
        # get measured latency values RTT
        xArrayRtt1 = []
        yArrayRtt1 = []
        xArrayRtt2 = []
        yArrayRtt2 = []
        # get RTT values
        getxyArrayLatency(xArrayRtt1, yArrayRtt1, dataMap[key1][key2]['latency'], timeTillStart)
        getxyArrayLatency(xArrayRtt2, yArrayRtt2, dataMap[key2][key1]['latency'], timeTillStart)
        lastvalueLat = xArrayRtt1[-1]
        # plot RTT values
        ax11.plot(xArrayRtt1, yArrayRtt1,  label='Measured Latency RTT')
        ax21.plot(xArrayRtt2, yArrayRtt2,  label='Measured Latency RTT')
    else:
        # get measured latency values Echo Rtt
        xArrayEchoRtt1 = []
        yArrayEchoRtt1 = []
        xArrayEchoRtt2 = []
        yArrayEchoRtt2 = []
        # get Echo RTT values
        getxyArrayLatency(xArrayEchoRtt1, yArrayEchoRtt1, dataMap[key1][key2]['latencyEchoRTT'], timeTillStart)
        getxyArrayLatency(xArrayEchoRtt2, yArrayEchoRtt2, dataMap[key2][key1]['latencyEchoRTT'], timeTillStart)
        # plot Echo RTT values
        ax11.plot(xArrayEchoRtt1, yArrayEchoRtt1, color= 'royalblue',label='Measured Latency')
        ax21.plot(xArrayEchoRtt2, yArrayEchoRtt2, color= 'royalblue',label='Measured Latency')

        # get measured latency values Echo
        xArrayEcho1 = []
        yArrayEcho1 = []
        xArrayEcho2 = []
        yArrayEcho2 = []
        # get Echo values
        getxyArrayLatency(xArrayEcho1, yArrayEcho1, dataMap[key1][key2]['latencyEcho'], timeTillStart)
        getxyArrayLatency(xArrayEcho2, yArrayEcho2, dataMap[key2][key1]['latencyEcho'], timeTillStart)
        lastvalueLat = xArrayEcho1[-1]
        # plot Echo values
        #ax11.plot(xArrayEcho1, yArrayEcho1,  label='Measured Latency Echo')
        #ax21.plot(xArrayEcho2, yArrayEcho2,  label='Measured Latency Echo')

    ######## only in Mininet ###########
    # reference values
    data = json.load(open(path + 'log_latency_change.json'))
    for d in data:
        timestamp = d['time']
        if (timestamp < timeTillStart):
            timestamp = timeTillStart
        for dd in d['data']:
            # from 1 to 2
            #print(dd)
            if "s1" in dd['interface']:
                objChange = {}
                objChange['time'] = timestamp - timeTillStart
                # if ping is before last value
                if(objChange['time'] < lastvalueLat):
                    if (objChange['time'] < 0):
                        print('LOWER THEN 0')
                        objChange['time'] = 0.000000000000000001
                    objChange['value'] = dd['latency']
                    array2to1.append(objChange)

            elif "s2" in dd['interface']:
                objChange = {}
                objChange['time'] = timestamp - timeTillStart
                # if ping is before last value
                if (objChange['time'] < lastvalueLat):
                    if (objChange['time'] < 0):
                        objChange['time'] = 0.000000000000000001
                    objChange['value'] = dd['latency']
                    array1to2.append(objChange)

    xArrayChange1To2 = []
    yArrayChange1To2 = []
    xArrayChange2To1 = []
    yArrayChange2To1 = []

    # changes to xarray/yarray
    for oneToTwo in range(len(array1to2)):
        if (oneToTwo > 0):
            xArrayChange1To2.append(array1to2[oneToTwo]['time'])
            yArrayChange1To2.append(array1to2[oneToTwo - 1]['value'])
        xArrayChange1To2.append(array1to2[oneToTwo]['time'])
        yArrayChange1To2.append(array1to2[oneToTwo]['value'])
    if(len(dataMap[key1][key2]['latency'])>0):
        xArrayChange1To2.append(xArrayRtt1[-1])
    elif(len(dataMap[key1][key2]['latencyEcho'])>0):
        #print(xArrayEcho1)
        xArrayChange1To2.append(xArrayEcho1[-1])

    yArrayChange1To2.append(array1to2[-1]['value'])

    for twoToOne in range(len(array2to1)):
        if (twoToOne > 0):
            xArrayChange2To1.append(array2to1[twoToOne]['time'])
            yArrayChange2To1.append(array2to1[twoToOne-1]['value'])
        xArrayChange2To1.append(array2to1[twoToOne]['time'])
        yArrayChange2To1.append(array2to1[twoToOne]['value'])

    if (len(dataMap[key1][key2]['latency'])>0):
        xArrayChange2To1.append(xArrayRtt2[-1]-timeTillStart)
    elif (len(dataMap[key1][key2]['latencyEcho'])>0):
        print("added time: {}".format(xArrayEcho2[-1]))
        xArrayChange2To1.append(xArrayEcho2[-1])

    #xArrayChange2To1.append(xArrayRtt2[-1])
    yArrayChange2To1.append(array2to1[-1]['value'])

    ax11.plot(xArrayChange1To2, yArrayChange1To2, '--', color='tomato', label='Set Latency')
    ax21.plot(xArrayChange2To1, yArrayChange2To1,'--',  color='tomato', label = 'Set Latency')

    ############### plot ping latency ##########################
    xPing1To2 = []
    xPing2To1 = []
    yPing1To2 = []
    yPing2To1 = []

    # open the files
    with open(path + 'ping_h1_h2.csv') as f:
        lines1To2 = f.readlines()
    with open(path + 'ping_h2_h1.csv') as f:
        lines2To1 = f.readlines()
    print("Add3")
    # fill axises
    for oneToTwo in lines1To2:
        splittedString = oneToTwo.split(";")
        latencyValue = splittedString[0]
        timestamp = float(splittedString[1]) - timeTillStart
        #if (timestamp < 0):
        #    timestamp = 0
        #    print("timestamp smaller 1")
        if(timestamp < lastvalueLat and timestamp > 0):
            xPing1To2.append(timestamp)
            yPing1To2.append(float(latencyValue) / 2)

    for twoToOne in lines2To1:
        splittedString = twoToOne.split(";")
        latencyValue = splittedString[0]
        timestamp = float(splittedString[1]) - timeTillStart
        #if (timestamp < 0):
        #    timestamp = 0
        #    print("timestamp smaller 2" )
        if (timestamp < lastvalueLat and timestamp > 0):
            xPing2To1.append(timestamp)
            yPing2To1.append(float(latencyValue) / 2)

    ax11.plot(xPing1To2, yPing1To2, '+-', color='seagreen', label='Ping')
    ax21.plot(xPing2To1, yPing2To1,'+-',  color='seagreen',label='Ping')

    # grid
    ax11.grid()
    ax21.grid()

    ax11.legend(loc='lower right')
    ax21.legend(loc='lower right')

    tick_spacing = 10
    ax11.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    ax21.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    ax11.set_xlim(-0.1,100)
    ax21.set_xlim(-0.1,100)
    ax11.set_ylim(-0.1, 60)
    ax21.set_ylim(-0.1, 60)

    # labels
    ax11.set_xlabel(r'Time [s]')
    ax11.set_ylabel(r'Latency [ms]')
    # labels
    ax21.set_xlabel(r'Time [s]')
    #ax21.set_xlabel(r'Time (s)', fontsize=9)
    ax21.set_ylabel(r'Latency [ms]')

    print("Add5")
    fig1.savefig("latency_1_2.pdf", format='pdf', bbox_inches='tight')
    fig2.savefig("latency_2_1.pdf",format='pdf', bbox_inches='tight')

    plt.show()

def plotLatencyChangeCONTROLLERRaspi(dataMap, timeTillStart,pingData1,pingData2, Sw2Con,Con2Sw, saved_echo_rtt_to_dpid, pingVal1, pingVal2):
    plt.rc('xtick', labelsize=14)
    plt.rc('ytick', labelsize=14)
    plt.rc('axes', titlesize=14)
    plt.rc('axes', labelsize=14)
    fig1 = plt.figure()
    ax11 = fig1.add_subplot(211)
    ax12 = fig1.add_subplot(212)
    fig2 = plt.figure()
    ax21 = fig2.add_subplot(211)
    ax22 = fig2.add_subplot(212)


    # labels
    ax12.set_xlabel('Time [s]')
    ax12.set_ylabel('Latency [ms]')
    ax11.set_ylabel('Latency [ms]')
    ax22.set_xlabel('Time [s]')
    ax21.set_ylabel('Latency [ms]')
    ax22.set_ylabel('Latency [ms]')
    # get keys
    key1 = list(dataMap.keys())[0]
    key2 = list(dataMap.keys())[1]
    ax11.set_title(label='Connection Switch 1 - Switch 2', fontsize=17)
    ax12.set_title(label='Connection Controller - Switch 2', fontsize=17)
    # get measured latency values Echo Rtt
    xArrayEchoRtt1 = []
    yArrayEchoRtt1 = []
    xArrayEchoRtt2 = []
    yArrayEchoRtt2 = []
    # get Echo RTT values
    getxyArrayLatency(xArrayEchoRtt1, yArrayEchoRtt1, dataMap[key1][key2]['latencyEchoRTT'], timeTillStart)
    getxyArrayLatency(xArrayEchoRtt2, yArrayEchoRtt2, dataMap[key2][key1]['latencyEchoRTT'], timeTillStart)
    print("EchoRTT {}".format(yArrayEchoRtt1))
    # plot Echo RTT values
    ax11.plot(xArrayEchoRtt1, yArrayEchoRtt1 , color='r', label=r'Derived from Controller - Switch RTT')
    ax21.plot(xArrayEchoRtt2, yArrayEchoRtt2, color='g', label='L_{S2} Derived from RTT')

    # get measured latency values Echo
    xArrayEcho1 = []
    yArrayEcho1 = []
    xArrayEcho2 = []
    yArrayEcho2 = []
    # get Echo values
    getxyArrayLatency(xArrayEcho1, yArrayEcho1, dataMap[key1][key2]['latencyEcho'], timeTillStart)
    getxyArrayLatency(xArrayEcho2, yArrayEcho2, dataMap[key2][key1]['latencyEcho'], timeTillStart)
    # plot Echo values
    ax11.plot(xArrayEcho1, yArrayEcho1, color='g', label='Asymmetry Detection')
    ax21.plot(xArrayEcho2, yArrayEcho2, '--', color='r', label='Asymmetry Detection')
    print("Echo {}".format(yArrayEcho1))
    # get ping values
    xArrayPing1 = []
    yArrayPing1 = []
    xArrayPing2 = []
    yArrayPing2 = []
    getPingValues(xArrayPing1, yArrayPing1, pingData1, timeTillStart)
    getPingValues(xArrayPing2, yArrayPing2, pingData2, timeTillStart)
    ax11.plot(xArrayPing1, yArrayPing1, '--',color= 'royalblue', label='Derived from Ping Switch 1 - Switch 2')
    ax21.plot(xArrayPing2, yArrayPing2, '+-',color= 'royalblue', label='Derived from Ping')

    # get C2Sw values
    xArray2Sw1 = []
    yArray2Sw1 = []
    xArray2Sw2 = []
    yArray2Sw2 = []
    getxyArrayLatencyNoTs(xArray2Sw1, yArray2Sw1, Con2Sw[key1], timeTillStart)
    getxyArrayLatencyNoTs(xArray2Sw2, yArray2Sw2, Con2Sw[key2], timeTillStart)
    ax12.plot(xArray2Sw1, yArray2Sw1, color='g', label='Controller to Switch 2')
    ax22.plot(xArray2Sw2, yArray2Sw2, 'g', label='Controller to Switch')

    # get EchoRTT values
    xArrayEcho1= []
    yArrayEcho1 = []
    xArrayEcho2 = []
    yArrayEcho2 = []
    getxyArrayLatencyNoTs(xArrayEcho1, yArrayEcho1, saved_echo_rtt_to_dpid[key1], timeTillStart, True)
    getxyArrayLatencyNoTs(xArrayEcho2, yArrayEcho2, saved_echo_rtt_to_dpid[key2], timeTillStart, True)
    print("EchoRTT Values: {}".format(yArrayEcho1))
    ax12.plot(xArrayEcho1, yArrayEcho1, 'r', label='Derived from RTT Controller - Switch 2')
    ax22.plot(xArrayEcho2, yArrayEcho2, 'r', label='Derived from')

    # get Sw2C values
    xArray2C1 = []
    yArray2C1 = []
    xArray2C2 = []
    yArray2C2 = []
    getxyArrayLatencyNoTs(xArray2C1, yArray2C1, Sw2Con[key1], timeTillStart)
    getxyArrayLatencyNoTs(xArray2C2, yArray2C2, Sw2Con[key2], timeTillStart)
    print("Sw2C Values: {}".format(yArray2C1))
    ax12.plot(xArray2C1, yArray2C1, 'y', label='Switch 2 to Controller')
    ax22.plot(xArray2C2, yArray2C2, 'y', label='Switch to Controller')

    # get ping C2Sw values
    xArrayPing1a = []
    yArrayPing1a = []
    xArrayPing2a = []
    yArrayPing2a = []
    getPingValues(xArrayPing1a, yArrayPing1a, pingVal1, timeTillStart)
    getPingValues(xArrayPing2a, yArrayPing2a, pingVal2, timeTillStart)
    print("Ping Values: {}".format(yArrayPing1a))
    ax12.plot(xArrayPing1a, yArrayPing1a, '--',color='royalblue', label='Derived from Ping Controller - Switch 2')
    ax22.plot(xArrayPing2a, yArrayPing2a,'--', color='royalblue', label='Ping')

    ax11.vlines(x=42.1,  ymin=70, ymax=100, color='dimgrey',lw=3, linestyle='--')
    #ax21.vlines(x=42.1, ymin=0, ymax=38, color='#E02DE0',lw=3, linestyle='--')
    ax21.vlines(x=42.1, ymin=0, ymax=38, color='dimgrey', lw=3, linestyle='--')
    ax21.vlines(x=63.5, ymin=0, ymax=38, color='dimgrey',lw=3, linestyle='--')
    #ax11.vlines(x=63.5, ymin=70, ymax=100, color='#E02DE0',lw=3, linestyle='--')
    ax11.vlines(x=63.5, ymin=70, ymax=100, color='#E02DE0', lw=3, linestyle='--')

    font0 = FontProperties()
    font = font0.copy()
    font.set_weight('bold')
    font.set_size(20)

    #ax11.text(42.5,75,'{1} Changing to asymmetric Latency C-S1',verticalalignment='center',fontproperties=font, color='dimgrey')
    #ax11.text(64, 75, '{2} Changing to symmetric Latency S1-S2', verticalalignment='center', fontproperties=font, color='#E02DE0')
    ax11.text(42.5,75,'{1}',verticalalignment='center',fontproperties=font, color='dimgrey')
    ax11.text(64, 75, '{2}', verticalalignment='center', fontproperties=font, color='#E02DE0')

    ax21.text(42.5, 35, '{1}', verticalalignment='center', fontproperties=font, color='dimgrey')
    ax21.text(64, 35, '{2}', verticalalignment='center', fontproperties=font, color='dimgrey')

    #style.setup3()
    ax11.set_xlim(19.9, 100.1)
    ax12.set_xlim(19.9, 100.1)
    ax21.set_xlim(19.9, 100.1)
    ax22.set_xlim(19.9, 100.1)

    ax11.set_ylim(29.9, 80.1)
    ax21.set_ylim(29.9, 80.1)

    ax11.legend(loc=r'lower right', fontsize=17)
    ax21.legend(loc=r'lower right', fontsize=16)
    ax12.legend(loc=r'lower right', fontsize=17)
    ax22.legend(loc=r'upper right', fontsize=18)

    plt.rcParams.update({'font.size': 22})

    # basic
    ax11.grid()
    ax21.grid()
    ax12.grid()
    ax22.grid()
    plt.show()

def plotLatencyChangeAllRaspi(dataMap, timeTillStart, latencyChange1, latencyChange2):

    fig1 = plt.figure()
    ax11 = fig1.add_subplot(211)
    ax12 = fig1.add_subplot(212)

    # labels
    ax11.set_xlabel('time [s]')
    ax11.set_ylabel('latency [ms]')
    ax11.title.set_text('Switch 1')
    ax12.set_xlabel('time [s]')
    ax12.set_ylabel('latency [ms]')
    ax12.title.set_text('Switch 2')

    #get keys
    key1 = list(dataMap.keys())[0]
    key2 = list(dataMap.keys())[1]
    if(len(dataMap[key1][key2]['latency']) > 0):
        # get measured latency values RTT
        xArrayRtt1 = []
        yArrayRtt1 = []
        xArrayRtt2 = []
        yArrayRtt2 = []
        # get RTT values
        getxyArrayLatency(xArrayRtt1, yArrayRtt1, dataMap[key1][key2]['latency'], timeTillStart)
        getxyArrayLatency(xArrayRtt2, yArrayRtt2, dataMap[key2][key1]['latency'], timeTillStart)
        # plot RTT values
        ax11.plot(xArrayRtt1, yArrayRtt1, 'r', label='Measured Latency RTT')
        ax12.plot(xArrayRtt2, yArrayRtt2, 'r', label='Measured Latency RTT')
    if (len(dataMap[key1][key2]['latencyEchoRTT']) > 0):
        # get measured latency values Echo Rtt
        xArrayEchoRtt1 = []
        yArrayEchoRtt1 = []
        xArrayEchoRtt2 = []
        yArrayEchoRtt2 = []
        # get Echo RTT values
        getxyArrayLatency(xArrayEchoRtt1, yArrayEchoRtt1, dataMap[key1][key2]['latencyEchoRTT'], timeTillStart)
        getxyArrayLatency(xArrayEchoRtt2, yArrayEchoRtt2, dataMap[key2][key1]['latencyEchoRTT'], timeTillStart)
        # plot Echo RTT values
        ax11.plot(xArrayEchoRtt1, yArrayEchoRtt1, 'y', label='Measured Latency EchoRTT')
        ax12.plot(xArrayEchoRtt2, yArrayEchoRtt2, 'y', label='Measured Latency EchoRTT')

        # get measured latency values Echo
        xArrayEcho1 = []
        yArrayEcho1 = []
        xArrayEcho2 = []
        yArrayEcho2 = []
        # get Echo values
        getxyArrayLatency(xArrayEcho1, yArrayEcho1, dataMap[key1][key2]['latencyEcho'], timeTillStart)
        getxyArrayLatency(xArrayEcho2, yArrayEcho2, dataMap[key2][key1]['latencyEcho'], timeTillStart)
        # plot Echo values
        ax11.plot(xArrayEcho1, yArrayEcho1, 'g', label='Measured Latency Echo')
        ax12.plot(xArrayEcho2, yArrayEcho2, 'g', label='Measured Latency Echo')

    # basic
    ax11.grid()
    ax12.grid()


    # check if data time is in intervall
    plt.show()

def plotLatencyChangeStatsOne_withping(dataMap, timeTillStart, key, pingData1, pingData2):

    ffig1, ax1 = plt.subplots()

    ax1.set_xlabel('time [s]')
    ax1.set_ylabel('latency [ms]')

    ffig2, ax2 = plt.subplots()

    ax2.title.set_text('Latency from 1 to 2')
    ax2.title.set_text('Latency from 2 to 1')

    array1to2 = []
    array2to1 = []

    #get keys
    key1 = list(dataMap.keys())[0]
    key2 = list(dataMap.keys())[1]

    # get measured latency values RTT
    xArrayRtt1 = []
    yArrayRtt1 = []
    xArrayRtt2 = []
    yArrayRtt2 = []
    # get values
    getxyArrayLatency(xArrayRtt1, yArrayRtt1, dataMap[key1][key2][key], timeTillStart)
    getxyArrayLatency(xArrayRtt2, yArrayRtt2, dataMap[key2][key1][key], timeTillStart)
    # plot values
    ax1.plot(xArrayRtt1, yArrayRtt1,'+-', color= 'tomato', label='Measured Latency')
    ax2.plot(xArrayRtt2, yArrayRtt2, 'r', label='Measured Latency')

    # get ping values
    xArrayPing1 = []
    yArrayPing1 = []
    xArrayPing2 = []
    yArrayPing2 = []

    getPingValues(xArrayPing1, yArrayPing1, pingData1, timeTillStart)
    getPingValues(xArrayPing2, yArrayPing2, pingData2, timeTillStart)
    ax1.plot(xArrayPing1, yArrayPing1, '--', color='royalblue', label='Measured Ping')
    ax2.plot(xArrayPing2, yArrayPing2, 'b', label='Measured Ping')

    # basic
    ax1.grid()
    ax2.grid()

    avg1 = np.average(yArrayRtt1)
    ax1.axhline(y=avg1, color= 'seagreen', label='Average Measured Latency')
    #avg2 = np.average(yArrayRtt1)
    ax1.set_xlim(19.9, 300)
    ax1.set_ylim(-0.001, 8.1)
    ax2.set_xlim(9.9, 300)
    tick_spacing = 20
    ax1.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    # check if data time is in intervall
    style.setup()
    legend = ax1.legend(loc='upper right', shadow=True)
    legend2 = ax2.legend(loc='upper right', shadow=True)
    plt.show()

def getPingValues(xArray, yArray, pingData, timeTillStart, divide=True):

    od = collections.OrderedDict(sorted(pingData.items()))

    for ts in od.keys():
        # difftime
        diffTime = float(ts)-timeTillStart
        if(diffTime > 40.0 and diffTime<60):
            print (ts)
        xArray.append(diffTime)
        if(divide):
            yArray.append(float(od[ts])/2)
        else:
            yArray.append(float(od[ts]))

def plotBandWith(dataMap, timeTillStart):

    xArray1 = []
    yArray1 = []
    xArray2 = []
    yArray2 = []
    getxyArrayLatency(xArray1, yArray1, dataMap[1][2]['bw'], timeTillStart)
    getxyArrayLatency(xArray2, yArray2, dataMap[2][1]['bw'], timeTillStart)

def plotRTTComp (dataMap, timeTillStart, saved_rtt_to_dpid, saved_echo_rtt_to_dpid,pingVal1, pingVal2,socketdata1,socketdata2):

    lRTT1 = []
    lRTT2 = []
    lEcho1 = []
    lEcho2 = []

    for i in range(len(saved_rtt_to_dpid[list(saved_rtt_to_dpid.keys())[0]])):
        elementRTT = saved_rtt_to_dpid[list(saved_rtt_to_dpid.keys())[0]][i]
        rttValue = list(elementRTT.values())[0] * 1000
        lRTT1.append(rttValue)

    for i in range(len(saved_echo_rtt_to_dpid[list(saved_echo_rtt_to_dpid.keys())[0]])):
        elementEcho = saved_echo_rtt_to_dpid[list(saved_echo_rtt_to_dpid.keys())[0]][i]
        echoValue = list(elementEcho.values())[0] * 1000
        lEcho1.append(echoValue)

    for i in range(len(saved_rtt_to_dpid[list(saved_rtt_to_dpid.keys())[1]])):
        elementRTT = saved_rtt_to_dpid[list(saved_rtt_to_dpid.keys())[1]][i]
        rttValue = list(elementRTT.values())[0] * 1000
        lRTT2.append(rttValue)

    for i in range(len(saved_echo_rtt_to_dpid[list(saved_echo_rtt_to_dpid.keys())[1]])):
        elementEcho = saved_echo_rtt_to_dpid[list(saved_echo_rtt_to_dpid.keys())[1]][i]
        echoValue = list(elementEcho.values())[0] * 1000
        lEcho2.append(echoValue)

    # get ping values
    pingValSw1 = [float(i) for i in (list(pingVal1.values()))]
    pingValSw2 = [float(i) for i in (list(pingVal2.values()))]

    lsocket1 = []
    lsocket2 = []
    # socket
    for elementS1 in socketdata1:
        c2SwValue = elementS1['TC2Sw']
        sw2C = elementS1['TSw2C']
        lsocket1.append(c2SwValue + sw2C)

    for elementS2 in socketdata2:
        c2SwValue = elementS2['TC2Sw']
        sw2C = elementS2['TSw2C']
        lsocket2.append(sw2C + c2SwValue)

    # median values
    medianRTT1 = np.median(lRTT1)
    medianEcho1 = np.median(lEcho1)

    medianRTT2 = np.median(lRTT2)
    medianEcho2 = np.median(lEcho2)

    medianPing1 = np.median(pingValSw1)
    medianPing2 = np.median(pingValSw2)

    medianSocket1 = np.median(lsocket1)
    medianSocket2 = np.median(lsocket2)

    avgRTT1 = np.average(lRTT1)
    avgEcho1 = np.average(lEcho1)
    avgPing1 = np.average(pingValSw1)

    stdRTT1 = np.std(lRTT1)
    stdEcho1 = np.std(lEcho1)
    stdPing1 = np.std(pingValSw1)

    avgRTT2 = np.average(lRTT2)
    avgEcho2 = np.average(lEcho2)
    avgPing2 = np.average(pingValSw2)

    stdRTT2 = np.std(lRTT2)
    stdEcho2 = np.std(lEcho2)
    stdPing2 = np.std(pingValSw2)
    print("avgRTT1: {}, avgEcho1: {},avgPing1:{}, stdRTT1:  {}stdEcho1 :{}stdPing1 {}".format(avgRTT1, avgEcho1, avgPing1, stdRTT1, stdEcho1, stdPing1))
    print("avgRTT2: {}, avgEcho2: {},avgPing2:{}, stdRTT2:  {}stdEcho2 :{}stdPing2 {}".format(avgRTT2, avgEcho2, avgPing2, stdRTT2, stdEcho2, stdPing2))
    print("Median RTT1: {} Echo1: {} Ping1: {}| RTT2: {} Echo2: {} Ping2: {} Socket1: {} Socket2: {}".format(medianRTT1,medianEcho1,medianPing1,medianRTT2,medianEcho2,medianPing2, medianSocket1,medianSocket2))

    #combine to sets
    set1 = [lRTT1, lEcho1, lsocket1, pingValSw1]
    set2 = [lRTT2, lEcho2, lsocket2, pingValSw2]

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(9, 4))

    bplot1 = axes[0].boxplot(set1,
                             vert=True,  # vertical box aligmnent
                             patch_artist=True,
                             whis = [5,95],
                             showfliers = False,
                             notch=True
                             )  # fill with color
    bplot2 = axes[1].boxplot(set2,
                             vert=True,  # vertical box aligmnent
                             patch_artist=True,
                             whis = [5,95],
                             showfliers = False,
                             notch=True
                             )  # fill with color
    #axes[0].set_ylim(0.49,5.5)
    #axes[1].set_ylim(0.49,5.5)
    colors = ['tomato', 'salmon', 'tomato', 'salmon']
    for patch, color in zip(bplot1['boxes'], colors):
        patch.set_facecolor(color)
    for element in ['medians']:
        plt.setp(bplot1[element], color='royalblue')
    for patch, color in zip(bplot2['boxes'], colors):
        patch.set_facecolor(color)
    for element in ['medians']:
        plt.setp(bplot2[element], color='royalblue')

    for ax in axes:
        ax.yaxis.grid(True)
        #ax.set_xticks([y + 1 for y in range(len(all_data))], )
        #ax.set_xlabel('xlabel')
        ax.set_ylabel('RTT [ms]',fontsize=20)
        ax.set_ylim(-0.00001, 6.0001)
    #style.setup()
    #plt.setp(axes, xticklabels=['', 'Echo ', 'Socket', 'Ping'])
    axes[0].set_xticklabels([r'Statistic R. $S_{1}$', r'Echo R. $S_{1}$',r'Socket $S_{1}$', r'Ping $S_{1}$'])

    axes[1].set_xticklabels([r'Statistic R. $S_{2}$', r'Echo R. $S_{2}$', r'Socket $S_{2}$', r'Ping $S_{2}$'])
    axes[0].tick_params(labelsize=20)
    axes[1].tick_params(labelsize=20)
    plt.show()

# showing in stacked bar plot that
def timeToSwCCompare(saved_rtt_to_dpid, saved_echo_rtt_to_dpid, saved_echo_timeToSw, saved_echo_timeToC, output_socket_1, output_socket_2, ab, ac):

    lRTT1 = []
    lRTT2 = []
    lEcho1 = []
    lEcho2 = []

    lTimeSw2C1 = []
    lTimeSw2C2 = []
    lTimeC2Sw1 = []
    lTimeC2Sw2 = []

    lsocketC2Sw1 = []
    lsocketC2Sw2 = []
    lsocketSw2C1 = []
    lsocketSw2C2 = []

    # RTT
    for i in range(len(saved_rtt_to_dpid[list(saved_rtt_to_dpid.keys())[0]])):
        elementRTT = saved_rtt_to_dpid[list(saved_rtt_to_dpid.keys())[0]][i]
        rttValue = list(elementRTT.values())[0] * 1000
        lRTT1.append(rttValue)

    for i in range(len(saved_echo_rtt_to_dpid[list(saved_echo_rtt_to_dpid.keys())[0]])):
        elementEcho = saved_echo_rtt_to_dpid[list(saved_echo_rtt_to_dpid.keys())[0]][i]
        echoValue = list(elementEcho.values())[0] * 1000
        lEcho1.append(echoValue)

    # echo RTT
    for i in range(len(saved_rtt_to_dpid[list(saved_rtt_to_dpid.keys())[1]])):
        elementRTT = saved_rtt_to_dpid[list(saved_rtt_to_dpid.keys())[1]][i]
        rttValue = list(elementRTT.values())[0] * 1000
        lRTT2.append(rttValue)

    for i in range(len(saved_echo_rtt_to_dpid[list(saved_echo_rtt_to_dpid.keys())[1]])):
        elementEcho = saved_echo_rtt_to_dpid[list(saved_echo_rtt_to_dpid.keys())[1]][i]
        echoValue = list(elementEcho.values())[0] * 1000
        lEcho2.append(echoValue)

    # time 2 sw
    for i in range(len(saved_echo_timeToSw[list(saved_echo_timeToSw.keys())[0]])):
        element2Sw = saved_echo_timeToSw[list(saved_echo_timeToSw.keys())[0]][i]
        swValue = list(element2Sw.values())[0] * 1000
        lTimeC2Sw1.append(swValue)

    for i in range(len(saved_echo_timeToSw[list(saved_echo_timeToSw.keys())[1]])):
        element2Sw = saved_echo_timeToSw[list(saved_echo_timeToSw.keys())[1]][i]
        swValue = list(element2Sw.values())[0] * 1000
        lTimeC2Sw2.append(swValue)

    # time 2 C
    for i in range(len(saved_echo_timeToC[list(saved_echo_timeToC.keys())[0]])):
        element2C = saved_echo_timeToC[list(saved_echo_timeToC.keys())[0]][i]
        cValue = list(element2C.values())[0] * 1000
        lTimeSw2C1.append(cValue)

    for i in range(len(saved_echo_timeToC[list(saved_echo_timeToC.keys())[1]])):
        element2C = saved_echo_timeToC[list(saved_echo_timeToC.keys())[1]][i]
        cValue = list(element2C.values())[0] * 1000
        lTimeSw2C2.append(cValue)

    # socket
    for elementS1 in output_socket_1:
        c2SwValue = elementS1['TC2Sw']
        sw2C = elementS1['TSw2C']
        lsocketC2Sw1.append(c2SwValue)
        lsocketSw2C1.append(sw2C)
    for elementS2 in output_socket_2:
        c2SwValue = elementS2['TC2Sw']
        sw2C = elementS2['TSw2C']
        lsocketSw2C2.append(sw2C)
        lsocketC2Sw2.append(c2SwValue)

    N = 4
    sw2CMed = (np.median(lTimeSw2C1), np.median(lsocketSw2C1), np.median(lTimeSw2C2), np.median(lsocketSw2C2) )
    c2SwMed = (np.median(lTimeC2Sw1), np.median(lsocketC2Sw1), np.median(lTimeC2Sw2), np.median(lsocketC2Sw2) )

    sw2CAvg = (np.average(lTimeSw2C1), np.average(lsocketSw2C1), np.average(lTimeSw2C2), np.average(lsocketSw2C2))
    c2SwAvg = (np.average(lTimeC2Sw1), np.average(lsocketC2Sw1), np.average(lTimeC2Sw2), np.average(lsocketC2Sw2))

    sw2CStd = (np.std(lTimeSw2C1), np.std(lsocketSw2C1), np.std(lTimeSw2C2) , np.std(lsocketSw2C2))
    c2SwStd = (np.std(lTimeC2Sw1), np.std(lsocketC2Sw1), np.std(lTimeC2Sw2),  np.std(lsocketC2Sw2))

    ind = np.arange(N)  # the x locations for the groups
    width = 0.35  # the width of the bars: can also be len(x) sequence

    p1 = plt.bar(ind, sw2CAvg, width, color='tomato', yerr=sw2CStd, capsize=7)
    p2 = plt.bar(ind, c2SwAvg, width, color='seagreen', bottom=sw2CAvg, yerr=c2SwStd, capsize=7, hatch='/')

    plt.ylabel('Latency [ms]')
    #plt.title('Latency differences Socket OVS')
    plt.xticks(ind, ('Switch1 Echo', 'Switch1 Socket', 'Switch2 Echo','Switch2 Socket'))
    #plt.yticks(np.arange(0, 10, 1))

    plt.ylim(ymin = -0.01)
    style.setup()
    plt.legend((p1[0], p2[0]), ('Controller to Switch', 'Switch to Controller'), loc='upper right')
    plt.show()

def oneLongTimeMininet(dataMap, timeTillStart, path):
    print("TIMETILLSTART: {}".format(timeTillStart))

    fig1 = plt.figure(figsize=(15, 5))
    ax11 = fig1.subplots()
    # = fig1.add_subplot(211)
    fig2  = plt.figure(figsize=(15, 5))
    ax21 = fig2.subplots()
    # = fig2.add_subplot(211)
    array1to2 = []
    array2to1 = []
    style.setup()
    #get keys
    key1 = list(dataMap.keys())[0]
    key2 = list(dataMap.keys())[1]
    # if rtt measured!
    lastvalueLat = 10000.0
    if(len(dataMap[key1][key2]['latency'])>0 and lastvalueLat<0):
        # get measured latency values RTT
        xArrayRtt1 = []
        yArrayRtt1 = []
        xArrayRtt2 = []
        yArrayRtt2 = []
        # get RTT values
        getxyArrayLatency(xArrayRtt1, yArrayRtt1, dataMap[key1][key2]['latency'], timeTillStart)
        getxyArrayLatency(xArrayRtt2, yArrayRtt2, dataMap[key2][key1]['latency'], timeTillStart)
        lastvalueLat = xArrayRtt1[-1]
        # plot RTT values
        ax11.plot(xArrayRtt1, yArrayRtt1,  label='Measured Latency RTT')
        ax21.plot(xArrayRtt2, yArrayRtt2,  label='Measured Latency RTT')
    else:
        # get measured latency values Echo Rtt
        xArrayEchoRtt1 = []
        yArrayEchoRtt1 = []
        xArrayEchoRtt2 = []
        yArrayEchoRtt2 = []
        # get Echo RTT values
        getxyArrayLatency(xArrayEchoRtt1, yArrayEchoRtt1, dataMap[key1][key2]['latencyEchoRTT'], timeTillStart)
        getxyArrayLatency(xArrayEchoRtt2, yArrayEchoRtt2, dataMap[key2][key1]['latencyEchoRTT'], timeTillStart)
        # plot Echo RTT values
        ax11.plot(xArrayEchoRtt1, yArrayEchoRtt1,'+-', color= 'tomato',label='Measured Latency')
        ax21.plot(xArrayEchoRtt2, yArrayEchoRtt2,'+-', color= 'tomato',label='Measured Latency')

        # get measured latency values Echo
        xArrayEcho1 = []
        yArrayEcho1 = []
        xArrayEcho2 = []
        yArrayEcho2 = []
        # get Echo values
        getxyArrayLatency(xArrayEcho1, yArrayEcho1, dataMap[key1][key2]['latencyEcho'], timeTillStart)
        getxyArrayLatency(xArrayEcho2, yArrayEcho2, dataMap[key2][key1]['latencyEcho'], timeTillStart)
        lastvalueLat = xArrayEcho1[-1]
        # plot Echo values
        #ax11.plot(xArrayEcho1, yArrayEcho1,  label='Measured Latency Echo')
        #ax21.plot(xArrayEcho2, yArrayEcho2,  label='Measured Latency Echo')

    ######## only in Mininet ###########
    # reference values
    data = json.load(open(path + 'log_latency_change.json'))
    for d in data:
        timestamp = d['time']
        if (timestamp < timeTillStart):
            timestamp = timeTillStart
        for dd in d['data']:
            # from 1 to 2
            #print(dd)
            if "s1" in dd['interface']:
                objChange = {}
                objChange['time'] = timestamp - timeTillStart
                # if ping is before last value
                if(objChange['time'] < lastvalueLat):
                    if (objChange['time'] < 0):
                        print('LOWER THEN 0')
                        objChange['time'] = 0.000000000000000001
                    objChange['value'] = dd['latency']
                    array2to1.append(objChange)

            elif "s2" in dd['interface']:
                objChange = {}
                objChange['time'] = timestamp - timeTillStart
                # if ping is before last value
                if (objChange['time'] < lastvalueLat):
                    if (objChange['time'] < 0):
                        objChange['time'] = 0.000000000000000001
                    objChange['value'] = dd['latency']
                    array1to2.append(objChange)

    xArrayChange1To2 = []
    yArrayChange1To2 = []
    xArrayChange2To1 = []
    yArrayChange2To1 = []

    # changes to xarray/yarray
    for oneToTwo in range(len(array1to2)):
        if (oneToTwo > 0):
            xArrayChange1To2.append(array1to2[oneToTwo]['time'])
            yArrayChange1To2.append(array1to2[oneToTwo - 1]['value'])
        xArrayChange1To2.append(array1to2[oneToTwo]['time'])
        yArrayChange1To2.append(array1to2[oneToTwo]['value'])
    if(len(dataMap[key1][key2]['latency'])>0):pass
        #xArrayChange1To2.append(xArrayRtt1[-1])
    elif(len(dataMap[key1][key2]['latencyEcho'])>0):
        #print(xArrayEcho1)
        xArrayChange1To2.append(xArrayEcho1[-1])

    yArrayChange1To2.append(array1to2[-1]['value'])

    for twoToOne in range(len(array2to1)):
        if (twoToOne > 0):
            xArrayChange2To1.append(array2to1[twoToOne]['time'])
            yArrayChange2To1.append(array2to1[twoToOne-1]['value'])
        xArrayChange2To1.append(array2to1[twoToOne]['time'])
        yArrayChange2To1.append(array2to1[twoToOne]['value'])

    if (len(dataMap[key1][key2]['latency'])>0):
        pass
        #xArrayChange2To1.append(xArrayRtt2[-1]-timeTillStart)
    elif (len(dataMap[key1][key2]['latencyEcho'])>0):
        print("added time: {}".format(xArrayEcho2[-1]))
        xArrayChange2To1.append(xArrayEcho2[-1])

    #xArrayChange2To1.append(xArrayRtt2[-1])
    yArrayChange2To1.append(array2to1[-1]['value'])

    #ax11.plot(xArrayChange1To2, yArrayChange1To2, '--', color='tomato', label='Set Latency')
    #ax21.plot(xArrayChange2To1, yArrayChange2To1,'--',  color='tomato', label = 'Set Latency')

    ############### plot ping latency ##########################
    xPing1To2 = []
    xPing2To1 = []
    yPing1To2 = []
    yPing2To1 = []

    # open the files
    with open(path + 'ping_h1_h2.csv') as f:
        lines1To2 = f.readlines()
    with open(path + 'ping_h2_h1.csv') as f:
        lines2To1 = f.readlines()
    print("Add3")
    # fill axises
    for oneToTwo in lines1To2:
        splittedString = oneToTwo.split(";")
        latencyValue = splittedString[0]
        timestamp = float(splittedString[1]) - timeTillStart
        #if (timestamp < 0):
        #    timestamp = 0
        #    print("timestamp smaller 1")
        if(timestamp < lastvalueLat and timestamp > 0):
            xPing1To2.append(timestamp)
            yPing1To2.append(float(latencyValue) / 2)

    for twoToOne in lines2To1:
        splittedString = twoToOne.split(";")
        latencyValue = splittedString[0]
        timestamp = float(splittedString[1]) - timeTillStart
        #if (timestamp < 0):
        #    timestamp = 0
        #    print("timestamp smaller 2" )
        if (timestamp < lastvalueLat and timestamp > 0):
            xPing2To1.append(timestamp)
            yPing2To1.append(float(latencyValue) / 2)

    ax11.plot(xPing1To2, yPing1To2, '--', color='royalblue', label='Measured Ping')
    ax21.plot(xPing2To1, yPing2To1,'--',  color='royalblue',label='Measured Ping')

    #average
    avg1 = np.average(yArrayEchoRtt1)
    ax11.axhline(y=avg1, color='seagreen', label='Average Measured Latency')
    avg2 = np.average(yArrayEchoRtt2)
    ax21.axhline(y=avg1, color='seagreen', label='Average Measured Latency')
    # grid
    ax11.grid()
    ax21.grid()

    ax11.legend(loc='upper left')
    ax21.legend(loc='upper left')
    style.setup()
    tick_spacing = 10
    ax11.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    ax21.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    ax11.set_xlim(4.9,285.1)
    ax21.set_xlim(4.9,285.1)
    ax11.set_ylim(-1.5, 5)
    ax21.set_ylim(-1.5, 5)

    # labels
    ax11.set_xlabel(r'Time [s]')
    ax11.set_ylabel(r'Latency [ms]')
    # labels
    ax21.set_xlabel(r'Time [s]')
    #ax21.set_xlabel(r'Time (s)', fontsize=9)
    ax21.set_ylabel(r'Latency [ms]')

    print("Add5")
    plt.show()

def plotRTTCompMininet (dataMap, timeTillStart, saved_rtt_to_dpid, saved_echo_rtt_to_dpid,pingVal1,pingVal2):

    lRTT1 = []
    lRTT2 = []
    lEcho1 = []
    lEcho2 = []
    print(saved_rtt_to_dpid)
    for i in range(len(saved_rtt_to_dpid[list(saved_rtt_to_dpid.keys())[0]])):
        elementRTT = saved_rtt_to_dpid[list(saved_rtt_to_dpid.keys())[0]][i]
        rttValue = list(elementRTT.values())[0] * 1000
        lRTT1.append(rttValue)

    for i in range(len(saved_echo_rtt_to_dpid[list(saved_echo_rtt_to_dpid.keys())[0]])):
        elementEcho = saved_echo_rtt_to_dpid[list(saved_echo_rtt_to_dpid.keys())[0]][i]
        echoValue = list(elementEcho.values())[0] * 1000
        lEcho1.append(echoValue)

    for i in range(len(saved_rtt_to_dpid[list(saved_rtt_to_dpid.keys())[1]])):
        elementRTT = saved_rtt_to_dpid[list(saved_rtt_to_dpid.keys())[1]][i]
        rttValue = list(elementRTT.values())[0] * 1000
        lRTT2.append(rttValue)

    for i in range(len(saved_echo_rtt_to_dpid[list(saved_echo_rtt_to_dpid.keys())[1]])):
        elementEcho = saved_echo_rtt_to_dpid[list(saved_echo_rtt_to_dpid.keys())[1]][i]
        echoValue = list(elementEcho.values())[0] * 1000
        lEcho2.append(echoValue)

    # get ping values
    pingValSw1 = [float(i) for i in (list(pingVal1.values()))]
    pingValSw2 = [float(i) for i in (list(pingVal2.values()))]

    print(pingValSw1)

    # median values
    medianRTT1 = np.median(lRTT1)
    medianEcho1 = np.median(lEcho1)

    medianRTT2 = np.median(lRTT2)
    medianEcho2 = np.median(lEcho2)

    medianPing1 = np.median(pingValSw1)
    medianPing2 = np.median(pingValSw2)

    avgRTT1 = np.average(lRTT1)
    avgEcho1 = np.average(lEcho1)
    avgPing1 = np.average(pingValSw1)

    stdRTT1 = np.std(lRTT1)
    stdEcho1 = np.std(lEcho1)
    print(lEcho1)
    stdPing1 = np.std(pingValSw1)
    print("Median RTT1: {} Echo1: {} Ping1: {}| RTT2: {} Echo2: {} Ping2: {} ".format(medianRTT1,medianEcho1,medianPing1,medianRTT2,medianEcho2,medianPing2))
    print(
    "avg RTT1: {} avg Echo1: {} avg Ping1: {}| std RTT1: {} std Echo1: {} std Ping1: {} ".format(avgRTT1, avgEcho1, avgPing1,
                                                                                                 stdRTT1, stdEcho1, stdPing1))
    #combine to sets
    set1 = [lRTT1, lEcho1, pingValSw1]
    set2 = [lRTT2, lEcho2, pingValSw2]

    #fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(9, 4))
    mpl_fig = plt.figure()
    ax = mpl_fig.add_subplot(111)
    bplot1 = ax.boxplot(set1,
                             vert=True,  # vertical box aligmnent
                             patch_artist=True,
                             whis = [5,95],
                             showfliers = False,
                        notch=True
                             )  # fill with color
    colors = ['tomato', 'salmon', 'tomato']
    for patch, color in zip(bplot1['boxes'], colors):
        patch.set_facecolor(color)
    for element in ['medians']:
        plt.setp(bplot1[element], color='royalblue')
    #bplot2 = axes[1].boxplot(set2,
    #                         vert=True,  # vertical box aligmnent


    #                         patch_artist=True,
     #                        whis = [5,95],
     #                        showfliers = False
     #                        )  # fill with color

    #for ax in axes:
    ax.yaxis.grid(True)
    #ax.set_xticks([y + 1 for y in range(len(all_data))], )
    #ax.set_xlabel('xlabel')
    ax.set_ylabel('RTT [ms]', fontsize=20)
    ax.set_ylim(-0.00001, 6)
    ax.tick_params(labelsize=20)
    plt.setp(ax, xticklabels=['Statistic Request', 'Echo Request', 'Ping'])

    #style.setup()
    plt.show()

def plotLatComp (dataMap, timeTillStart, pingVal1, pingVal2):

    # get keys
    #print(dataMap)
    key1 = list(dataMap.keys())[0]
    key2 = list(dataMap.keys())[1]
    if (len(dataMap[key1][key2]['latency']) > 0):
        # get measured latency values RTT
        xArrayRtt1 = []
        yArrayRtt1 = []
        xArrayRtt2 = []
        yArrayRtt2 = []
        # get RTT values
        getxyArrayLatency(xArrayRtt1, yArrayRtt1, dataMap[key1][key2]['latency'], timeTillStart)
        getxyArrayLatency(xArrayRtt2, yArrayRtt2, dataMap[key2][key1]['latency'], timeTillStart)
        # plot RTT values

    if (len(dataMap[key1][key2]['latencyEchoRTT']) > 0):
        # get measured latency values Echo Rtt
        xArrayEchoRtt1 = []
        yArrayEchoRtt1 = []
        xArrayEchoRtt2 = []
        yArrayEchoRtt2 = []
        # get Echo RTT values
        getxyArrayLatency(xArrayEchoRtt1, yArrayEchoRtt1, dataMap[key1][key2]['latencyEchoRTT'], timeTillStart)
        getxyArrayLatency(xArrayEchoRtt2, yArrayEchoRtt2, dataMap[key2][key1]['latencyEchoRTT'], timeTillStart)
        # get measured latency values Echo
        xArrayEcho1 = []
        yArrayEcho1 = []
        xArrayEcho2 = []
        yArrayEcho2 = []
        # get Echo values
        getxyArrayLatency(xArrayEcho1, yArrayEcho1, dataMap[key1][key2]['latencyEcho'], timeTillStart)
        getxyArrayLatency(xArrayEcho2, yArrayEcho2, dataMap[key2][key1]['latencyEcho'], timeTillStart)

    # get measured values
    mesVal1 = yArrayEchoRtt1#float(i) for i in (list(yArrayEchoRtt1))]
    mesVal2 = yArrayEchoRtt2#[float(i) for i in (list(yArrayEchoRtt2))]

    # get ping values
    pingValSw1 = [float(i) for i in (list(pingVal1.values()))]
    pingValSw2 = [float(i) for i in (list(pingVal2.values()))]

    medianPing1 = np.median(pingValSw1)
    medianPing2 = np.median(pingValSw2)

    median1 = np.median(mesVal1)
    median2 = np.median(mesVal2)

    avgMeas1 = np.average(mesVal1)
    avgPing1 = np.average(pingValSw1)

    stdMeas1 = np.std(mesVal1)
    stdPing1 = np.std(pingValSw1)

    avgMeas2 = np.average(mesVal2)
    avgPing2 = np.average(pingValSw2)

    stdMeas2 = np.std(mesVal2)
    stdPing2 = np.std(pingValSw2)

    print("med1: {} medPing1: {} avg1: {} avgPing1: {} std1: {} stdPing1: {}".format(median1,medianPing1,avgMeas1,avgPing1,stdMeas1,stdPing1))
    print( "med2: {} medPing2: {} avg2: {} avgPing2: {} std2: {} stdPing2: {}".format(median2, medianPing2, avgMeas2, avgPing2,
                                                                               stdMeas2, stdPing2))
    dof = len(mesVal1) - 1
    mean = np.mean(mesVal1)
    std = np.std(mesVal1, ddof=1)
    error = t.ppf(0.975, dof) * std / np.sqrt(dof + 1)
    print("Error: {}".format(error))
    #combine to sets
    set1 = [mesVal1, pingValSw1]
    set2 = [mesVal2, pingValSw2]

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(9, 4))

    bplot1 = axes[0].boxplot(set1,
                             vert=True,  # vertical box aligmnent
                             patch_artist=True,
                             whis = [5,95],
                             showfliers = False,
                             notch=True
                             )  # fill with color
    #print(pingValSw2)
    #print(bplot1)

    print(bplot1['medians'][0].get_xdata())
    bplot2 = axes[1].boxplot(set2,
                             vert=True,  # vertical box aligmnent
                             patch_artist=True,
                             whis = [5,95],
                             showfliers = False,
                             notch=True
                             )  # fill with color
    colors=['tomato', 'salmon']
    for patch, color in zip(bplot1['boxes'], colors):
        patch.set_facecolor(color)
    for element in ['medians']:
        plt.setp(bplot1[element], color='royalblue')
    for patch, color in zip(bplot2['boxes'], colors):
        patch.set_facecolor(color)
    for element in ['medians']:
        plt.setp(bplot2[element], color='royalblue')
    #axes[0].set_ylim(0.49,5.5)
    #axes[1].set_ylim(0.49,5.5)
    for ax in axes:
        ax.yaxis.grid(True)
        #ax.set_xticks([y + 1 for y in range(len(all_data))], )
        #ax.set_xlabel('xlabel')
        ax.set_ylabel('Latency [ms]',fontsize=20)
        ax.set_ylim(-0.5001, 6.0)

    print(axes[1])
    axes[0].set_xticklabels([r'Measured $S_{1}$ - $S_{2}$',  r'Derived from Ping $S_{1}$ - $S_{2}$'])
    plt.xticks(fontsize=30)
    axes[1].set_xticklabels([r'Measured $S_{2}$ - $S_{1}$',  r'Derived from Ping $S_{2}$ - $S_{1}$'])
    #style.setup()
    #style.setup()
    #plt.setp(axes, axes.titlesize=20)
    # plt.rc('font', size=30)
    # plt.rc('axes', titlesize=30)
    # plt.rc('axes', labelsize=30)
    # plt.rc('xtick', labelsize=30)
    # plt.rc('xtick', labelsize=30)
    #plt.rc('ytick', fontsize=30)
    axes[0].tick_params(labelsize=20)
    axes[1].tick_params(labelsize=20)

    #plt.xticks(fontsize=30)
    plt.show()

def plotLatCompMininet(dataMap, timeTillStart, path):

    lRTT1 = []
    lRTT2 = []
    lEcho1 = []
    lEcho2 = []

    # get keys
    key1 = list(dataMap.keys())[0]
    key2 = list(dataMap.keys())[1]
    if (len(dataMap[key1][key2]['latency']) > 0):
        # get measured latency values RTT
        xArrayRtt1 = []
        yArrayRtt1 = []
        xArrayRtt2 = []
        yArrayRtt2 = []
        # get RTT values
        getxyArrayLatency(xArrayRtt1, yArrayRtt1, dataMap[key1][key2]['latency'], timeTillStart)
        getxyArrayLatency(xArrayRtt2, yArrayRtt2, dataMap[key2][key1]['latency'], timeTillStart)
        # plot RTT values
        lastvalueLat = xArrayRtt1[-1]
    if (len(dataMap[key1][key2]['latencyEchoRTT']) > 0):
        # get measured latency values Echo Rtt
        xArrayEchoRtt1 = []
        yArrayEchoRtt1 = []
        xArrayEchoRtt2 = []
        yArrayEchoRtt2 = []
        # get Echo RTT values
        getxyArrayLatency(xArrayEchoRtt1, yArrayEchoRtt1, dataMap[key1][key2]['latencyEchoRTT'], timeTillStart)
        getxyArrayLatency(xArrayEchoRtt2, yArrayEchoRtt2, dataMap[key2][key1]['latencyEchoRTT'], timeTillStart)
        # get measured latency values Echo
        xArrayEcho1 = []
        yArrayEcho1 = []
        xArrayEcho2 = []
        yArrayEcho2 = []
        # get Echo values
        getxyArrayLatency(xArrayEcho1, yArrayEcho1, dataMap[key1][key2]['latencyEcho'], timeTillStart)
        getxyArrayLatency(xArrayEcho2, yArrayEcho2, dataMap[key2][key1]['latencyEcho'], timeTillStart)
        lastvalueLat = xArrayEcho1[-1]
    # get measured values
    mesVal1 = yArrayEchoRtt1  # float(i) for i in (list(yArrayEchoRtt1))]
    mesVal2 = yArrayEchoRtt2  # [float(i) for i in (list(yArrayEchoRtt2))]

    ############### plot ping latency ##########################
    xPing1To2 = []
    xPing2To1 = []
    yPing1To2 = []
    yPing2To1 = []
    # open the files
    with open(path + 'ping_h1_h2.csv') as f:
        lines1To2 = f.readlines()
    with open(path + 'ping_h2_h1.csv') as f:
        lines2To1 = f.readlines()
    print("Add3")
    # fill axises
    for oneToTwo in lines1To2:
        splittedString = oneToTwo.split(";")
        latencyValue = splittedString[0]
        timestamp = float(splittedString[1]) - timeTillStart
        # if (timestamp < 0):
        #    timestamp = 0
        #    print("timestamp smaller 1")
        if (timestamp < lastvalueLat and timestamp > 0):
            xPing1To2.append(timestamp)
            yPing1To2.append(float(latencyValue) / 2)

    for twoToOne in lines2To1:
        splittedString = twoToOne.split(";")
        latencyValue = splittedString[0]
        timestamp = float(splittedString[1]) - timeTillStart
        # if (timestamp < 0):
        #    timestamp = 0
        #    print("timestamp smaller 2" )
        if (timestamp < lastvalueLat and timestamp > 0):
            xPing2To1.append(timestamp)
            yPing2To1.append(float(latencyValue) / 2)

    pingValSw1 = yPing1To2
    pingValSw2 = yPing2To1

    medianPing1 = np.median(pingValSw1)
    medianPing2 = np.median(pingValSw2)

    median1 = np.median(mesVal1)
    median2 = np.median(mesVal2)

    std1 = np.std(mesVal1)
    stdping = np.std(pingValSw1)
    print(len(mesVal1))
    avg1 = np.average(mesVal1)
    avgPing = np.average(pingValSw1)

    print("Med1: {} Med2: {} Ping1: {} Ping2: {} Avg1: {} AvgPing1: {} std1: {} stdPing1: {}".format(median1,median2,medianPing1,medianPing2, avg1, avgPing,std1, stdping))

    # combine to sets
    set1 = [mesVal1, pingValSw1]
    set2 = [mesVal2, pingValSw2]

    mpl_fig = plt.figure()
    ax = mpl_fig.add_subplot(111)

    bplot1 = ax.boxplot(set1,
                             vert=True,  # vertical box aligmnent
                             patch_artist=True,
                             whis=[5, 95],
                             showfliers=False,
                        notch=True
                             )  # fill with color
    colors = ['tomato']
    colors2 = ['blue']
    for patch, color in zip(bplot1['boxes'], colors):
        patch.set_facecolor(color)
    for element in ['medians']:
        plt.setp(bplot1[element], color='royalblue')
    # axes[0].set_ylim(0.49,5.5)
    # axes[1].set_ylim(0.49,5.5)
    ax.yaxis.grid(True)
    # ax.set_xticks([y + 1 for y in range(len(all_data))], )
    # ax.set_xlabel('xlabel')
    ax.set_ylabel('Latency [ms]',fontsize=20)
    ax.set_ylim(-0.5001, 6.0)
    plt.tick_params(labelsize=20)
    #style.setup()
    plt.setp(ax, xticklabels=[r'Measured $S_{1}$ - $S_{2}$', 'Derived from Ping $S_{1}$ - $S_{2}$'])

    plt.show()

def getAdjMatrix(wholeData):
    latavg = {}
    for key1 in wholeData.keys():

        # conneted keys
        for key2 in list(wholeData[key1].keys()):
            if (key2 not in latavg.keys()):
                latavg[key2] = {}
            # get latencyvalAvg
            valueList = []
            for element in wholeData[key1][key2]['latencyEchoRTT']:
                valueList.append(element['value'])
            print(len(wholeData[key1][key2]['latencyEchoRTT']))
            latavg[key2][key1] = np.median(valueList)
    latavg2 = {}
    latavg2[key2] = {}
    latavg2[key2][key1] = latavg[key1][key2]
    print(latavg)