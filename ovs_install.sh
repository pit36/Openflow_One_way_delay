# OpenvSwitch installation from source
rm -r /home/$USER/openvswitch*
wget http://openvswitch.org/releases/openvswitch-2.9.0.tar.gz -O /home/$USER/Downloads/openvswitch-2.9.0.tar.gz
tar -xzf /home/$USER/Downloads/openvswitch-2.9.0.tar.gz -C /home/$USER/
cd /home/$USER/
mv openvswitch-2.9.0 openvswitch
rm openvswitch-2.9.0
cd /home/$USER/openvswitch/
./boot.sh
./configure --with-linux=/lib/modules/$(uname -r)/build
make -j 4
