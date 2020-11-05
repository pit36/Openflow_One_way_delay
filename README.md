# README #

## Project to measure One-Way Delays in OpenFlow Networks

### Features
* Latency and throughput monitoring in different setups possible
* Routing with Dijkstra
* Demonstrating the throughput and OWD delays on a website

#### Necessary Software and libraries
* installed ryu
     * https://osrg.github.io/ryu/  
* Python3
* Python libaries (install with pip3):
    * flask (flask.pocoo.org)
    * flask_sqlalchemy
    * flask_marshmallow
    * numpy
    * matplotlib
    * scipy

#### Mininet
It is possible to use Mininet as Network Emulation. Therefor you have to change the mode in the controller to the Mininet option.

## How do I get set up? ##

### Set up Open vSwitch:
```
sudo ovs-vsctl add-br br0
sudo ovs-vsctl add-port br0 eth0
sudo ovs-vsctl set-controller br0 tcp:<Controller_IP>:6633
```

## For the ping measurement, give the OVS brige br0 an IP:
```
ip addr add 10.0.0.1/24 dev br0
ip link set br0 up
```

### How to deploy:  
* clone repository
* install required modules
* into folder Controller -> python console 
    * "from restDB import db"
    * db.create_all() 
* Change your IP adresses in `simple_remote_controller_demonstrate_withMac.py`
* run `ryu-manager simple_remote_controller_demonstrate_withMac.py --observe-links`

### Database configuration:
* for discovering the database: sqlitebrowser recommeded
* keys: IDRec, IDSender
* data  latency, bandwith

### Website:
* Built with HTML5, chartJS (plots) and sigmaJS (graphs)
* Data requested by RestAPI
* run "general.html" in Browser


### Who do I talk to? ###
If you have any comments or need help, write an issue or send me an E-Mail:
peter.sossalla[at]tu-dresden.de
