import os
import paramiko
import sys
import time

def setforwarding(hostname,host_no):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username='host', password='root')
    channel = client.invoke_shell()

    # clear welcome message and send newline
    time.sleep(1)
    channel.recv(9999)
    channel.send("\n")
    time.sleep(1)

    if host_no==1:
        commands=['sudo ip addr add 192.168.200.1/24 dev ens4','sudo ip link set ens4 up', 'sudo ip link add vxlan0 type vxlan id 42 remote 192.168.200.2 dev ens4 dstport 4789','sudo ip link set vxlan0 up','sudo ovs-vsctl add-port 1-S-1-Br vxlan0','sudo ip link set vxlan0 up']
    else:
        commands=['sudo ip addr add 192.168.200.2/24 dev ens4','sudo ip link set ens4 up', 'sudo ip link add vxlan0 type vxlan id 42 remote 192.168.200.1 dev ens4 dstport 4789','sudo ip link set vxlan0 up','sudo ovs-vsctl add-port 1-S-1-Br vxlan0','sudo ip link set vxlan0 up']
    for command in commands:
        channel.send(command + "\n")
        while not channel.recv_ready():
            time.sleep(0.1)
        output = channel.recv(9999)
        time.sleep(0.1)
        channel.send("root" + "\n")
    channel.close()
    return()


hostname="192.168.125.217"
setforwarding(hostname,1)
hostname="192.168.125.171"
setforwarding(hostname,2)
