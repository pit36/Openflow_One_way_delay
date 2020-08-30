#!/bin/bash
rm -r /home/$USER/openvswitch*
wget https://www.openvswitch.org/releases/openvswitch-2.14.0.tar.gz -O /home/$USER/Downloads/openvswitch-2.14.0.tar.gz
tar -xzf /home/$USER/Downloads/openvswitch-2.14.0.tar.gz -C /home/$USER/
cd /home/$USER/
mv openvswitch-2.14.0 openvswitch
cd /home/$USER/openvswitch/
./boot.sh
./configure --with-linux=/lib/modules/$(uname -r)/build
make -j 4
