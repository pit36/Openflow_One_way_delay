sudo apt-get install autoconf libtool gcc make
git clone --single-branch --branch branch-2.9 https://github.com/openvswitch/ovs.git
#https://github.com/openvswitch/ovs.git
cd ovs
./boot.sh
./configure
make
make install
/sbin/modprobe openvswitch
#/sbin/lsmod | grep openvswitch
export PATH=$PATH:/usr/local/share/openvswitch/scripts
ovs-ctl start
