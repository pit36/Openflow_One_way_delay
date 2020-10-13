# README #

Latency and bandwith monitoring in different setups
Routing via DFS (not Dijkstra)
## How do I get set up? ##
#### Necessary  
* installed mininet
     * http://mininet.org/download/  
* installed ryu
     * https://osrg.github.io/ryu/  
* OpenFlow
* Python libaries:
    * flask (flask.pocoo.org)

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
![You get it!](https://media1.tenor.com/images/d67770820288f00f71027c287a75e708/tenor.gif?itemid=7957769 "Happy")  