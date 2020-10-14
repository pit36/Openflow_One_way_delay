sudo apt-get install autoconf libtool gcc make python openssl
rm -r ovs
git clone --single-branch --branch branch-2.9 https://github.com/openvswitch/ovs.git
# Overwrite the echo request 
cp ofp-util.c ovs/lib/ofp-util.c
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
