# README #

Latency and bandwith monitoring in different setups
Routing via DFS (not Dijkstra)
## How do I get set up? ##

### Setting up ovs:
sudo ovs-vsctl add-br br0
sudo ovs-vsctl add-port br0 eth0
sudo ovs-vsctl set-controller br0 tcp:<Controller_IP>:6633

## For the ping measurement, give the OVS brige br0 an IP:
ip addr add 10.0.0.1/24 dev br0
ip link set br0 up

#### Necessary  
* installed mininet
     * http://mininet.org/download/  
* installed ryu
     * https://osrg.github.io/ryu/  
* OpenFlow
* Python libaries:
    * flask (flask.pocoo.org)
    * flask_sqlalchemy
    * flask_marshmallow
    * numpy

### How to deploy:  
* clone repository
* install required modules
* into folder topo_x_switches -> python console 
    * "from restDB import db"
    * db.create_all() 
* run "python topo_two_switches.py"

### Summary of set up:
+ Setup 2 Switches:
    + Two Switches connected with link
    + if requeired: two hosts for iperf
    + With the ping measurements between the two switches, run: "python topo_two_switches.py --observe-links"
+ Arbitrary:
    + defining in topology.py

### Database configuration:
* for discovering the database: sqlitebrowser recommeded
* keys: IDRec, IDSender
* data  latency, bandwith

### Website:
* Built with HTML5, chartJS (plots) and sigmaJS (graphs)
* Data requested by RestAPI
* run "general.html" in Browser

## TODO:
* Configuration
* How to run tests
* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###
If you have any comments or need help, write an issue or send me an E-Mail:
peter.sossalla[at]tu-dresden.de

![You get it!](https://media1.tenor.com/images/d67770820288f00f71027c287a75e708/tenor.gif?itemid=7957769 "Happy")  
