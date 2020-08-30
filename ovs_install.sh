# OpenvSwitch installation from source
rm -r /home/$USER/Programs/openvswitch*
wget http://openvswitch.org/releases/openvswitch-2.9.0.tar.gz -O /home/$USER/Downloads/openvswitch-2.9.0.tar.gz
tar -xzf /home/$USER/Downloads/openvswitch-2.9.0.tar.gz -C /home/$USER/Programs/
cd /home/$USER/Programs/
mv openvswitch-2.9.0 openvswitch
rm openvswitch-2.9.0
cd /home/$USER/Programs/openvswitch/
./boot.sh
./configure --with-linux=/lib/modules/$(uname -r)/build
make -j 4
make install
make modules_install
/sbin/modprobe openvswitch
/sbin/modprobe openvswitch
export PATH=$PATH:/usr/local/share/openvswitch/scripts
ovs-ctl start
mkdir -p /usr/local/etc/openvswitch
ovsdb-tool create /usr/local/etc/openvswitch/conf.db vswitchd/vswitch.ovsschema
mkdir -p /usr/local/var/run/openvswitch
ovsdb-server --remote=punix:/usr/local/var/run/openvswitch/db.sock \
    --remote=db:Open_vSwitch,Open_vSwitch,manager_options \
    --private-key=db:Open_vSwitch,SSL,private_key \
    --certificate=db:Open_vSwitch,SSL,certificate \
    --bootstrap-ca-cert=db:Open_vSwitch,SSL,ca_cert \
    --pidfile --detach --log-file

