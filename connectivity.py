from math import *
import subprocess
import os
import yaml
import sys
import time


def get_pid(device):

  output = subprocess.Popen("sudo docker inspect -f '{{.State.Pid}}' "+ device, stdout=subprocess.PIPE, shell=True)
  (out, err) = output.communicate()
  return(out.strip())


file_name=str(sys.argv[1]) +"_device_inventory.yml"

inventory_list = open(file_name, "r")
inventory=yaml.load(inventory_list)

VM_list=inventory['VMcontainer_names']
#print(VM_list)

pid_list=[]

## Get process ID of all the VMs ##
for VMs in VM_list:
  output = subprocess.Popen("sudo docker inspect -f '{{.State.Pid}}' "+ VMs, stdout=subprocess.PIPE, shell=True)
  (out, err) = output.communicate()
  temp=[VMs,out.strip()]
  pid_list.append(temp)

#print(pid_list)

## Make connection from VM to bridges###
for VMs in pid_list:
  veth_pair="sudo ip link add vm_veth1 type veth peer name "+ VMs[0]
  vm_veth_attach="sudo ip link set vm_veth1 netns "+ VMs[1]
  ovs_veth_attach="sudo ovs-vsctl add-port "+str(VMs[0][:5])+"-Br "+VMs[0]
  os.system(veth_pair)
  os.system(vm_veth_attach)
  os.system(ovs_veth_attach)


## set all the links up ##

for VMs in pid_list:
  set_veth_up="sudo ip link set "+VMs[0]+"  up"
  set_bridge_up="sudo ip link set "+str(VMs[:5])+"-Br up"
  set_vm_veth_up="sudo docker exec "+VMs[0]+" ip link set vm_veth1 up"
  set_ip="sudo docker exec "+VMs[0]+" ip addr add 10.0."+VMs[0][4]+"."+VMs[0][8]+ "/24 dev vm_veth1"
  set_route="sudo docker exec "+VMs[0]+ " ip route add default via 10.0."+VMs[0][4]+".254 dev vm_veth1"
  os.system(set_veth_up)
  os.system(set_bridge_up)
  os.system(set_vm_veth_up)
  os.system(set_ip)
  os.system(set_route)


## Connect Subnet-Bridge to Subnet south namespace ##

NS_list=inventory['Namespace_names']
No_subnet=len(NS_list)-2
tenantNO=NS_list[0][0]
for i in range(No_subnet):
  subNO=i+1
  Base_name=str(tenantNO)+"-S-"+str(subNO)
  veth_pair="sudo ip link add "+Base_name+"-sub1 type veth peer name "+Base_name+"-sub2"
  veth_attach="sudo ip link set "+Base_name+"-sub1 netns "+Base_name+"-S"
  ovs_veth_attach="sudo ovs-vsctl add-port "+Base_name+"-Br "+Base_name+"-sub2"
  add_ip="sudo ip netns exec "+Base_name+"-S ip addr add 10.0."+str(subNO)+".254/24 dev "+Base_name+"-sub1"
  set_linkUP="sudo ip netns exec "+Base_name+"-S ip link set dev "+Base_name+"-sub1 up"
  set_ovslinkUP="sudo ip link set dev "+Base_name+"-sub2 up"
  os.system(veth_pair)
  os.system(veth_attach)
  os.system(ovs_veth_attach)
  os.system(add_ip)
  os.system(set_linkUP)
  os.system(set_ovslinkUP)


########################### END ######################################

########################## Subnet south namespace to southBr connection##################
NS_list=inventory['Namespace_names']
No_subnet=len(NS_list)-2
tenantNO=NS_list[0][0]
for i in range(No_subnet):
  subNO=i+1
  Base_name=str(tenantNO)+"-S-"+str(subNO)
  veth_pair="sudo ip link add "+Base_name+"-S-sub1 type veth peer name "+Base_name+"-S-sub2"
  veth_attach="sudo ip link set "+Base_name+"-S-sub1 netns "+Base_name+"-S"
  ovs_veth_attach="sudo ovs-vsctl add-port "+Base_name+"-southBr "+Base_name+"-S-sub2"
  add_ip="sudo ip netns exec "+Base_name+"-S ip addr add 172.17."+str(subNO)+".1/24 dev "+Base_name+"-S-sub1"
  command="sudo ip netns exec "+Base_name+"-S ip route add default via 172.17."+str(subNO)+".2 dev "+Base_name+"-S-sub1"
  loopback="sudo ip netns exec "+Base_name+"-S ip addr add 127.0.0.1/24 dev lo "
  loopbackUP="sudo ip netns exec "+Base_name+"-S ip link set lo up"
  set_linkUP="sudo ip netns exec "+Base_name+"-S ip link set dev "+Base_name+"-S-sub1 up"
  set_ovslinkUP="sudo ip link set dev "+Base_name+"-S-sub2 up"
  os.system(veth_pair)
  os.system(veth_attach)
  os.system(ovs_veth_attach)
  os.system(add_ip)
  os.system(set_linkUP)
  os.system(set_ovslinkUP)
  os.system(loopback)
  os.system(loopbackUP)
  os.system(command)




####################  END  #######################################################

########################## connect FW to 2 bridges ##############################

NS_list=inventory['Namespace_names']
No_subnet=len(NS_list)-2
tenantNO=NS_list[0][0]
for i in range(No_subnet):
  subNO=i+1
  Base_name=str(tenantNO)+"-S-"+str(subNO)
  FW1_PID=get_pid(Base_name+"-FW1")
  FW2_PID=get_pid(Base_name+"-FW2")
  command="sudo ip link add EFWens4 type veth peer name "+Base_name+"-FW1-sub2"
  os.system(command)
  command="sudo ip link set EFWens4 netns "+FW1_PID
  os.system(command)
  command="sudo ip link add EFWens4 type veth peer name "+Base_name+"-FW2-sub2"
  os.system(command)
  command="sudo ip link set EFWens4 netns "+FW2_PID
  os.system(command)
  command="sudo ovs-vsctl add-port "+Base_name+"-southBr "+Base_name+"-FW1-sub2"
  os.system(command)
  command="sudo ovs-vsctl add-port "+Base_name+"-southBr "+Base_name+"-FW2-sub2"
  os.system(command)
  command="sudo docker exec "+Base_name+"-FW1 ip addr add 172.17."+str(subNO)+".2/24 dev EFWens4"
  os.system(command)
  command="sudo docker exec "+Base_name+"-FW2 ip addr add 172.17."+str(subNO)+".3/24 dev EFWens4"
  os.system(command)
  command="sudo docker exec "+Base_name+"-FW1 ip link set dev EFWens4 up"
  os.system(command)
  command="sudo docker exec "+Base_name+"-FW2 ip link set dev EFWens4 up"
  os.system(command)
  command="sudo ip link set dev "+Base_name+"-FW1-sub2 up"
  os.system(command)
  command="sudo ip link set dev "+Base_name+"-FW2-sub2 up"
  os.system(command)

  command="sudo ip link add EFWens3 type veth peer name "+Base_name+"-FW1-sub4"
  os.system(command)
  command="sudo ip link set EFWens3 netns "+FW1_PID
  os.system(command)
  command="sudo ip link add EFWens3 type veth peer name "+Base_name+"-FW2-sub4"
  os.system(command)
  command="sudo ip link set EFWens3 netns "+FW2_PID
  os.system(command)
  command="sudo ovs-vsctl add-port "+Base_name+"-northBr "+Base_name+"-FW1-sub4"
  os.system(command)
  command="sudo ovs-vsctl add-port "+Base_name+"-northBr "+Base_name+"-FW2-sub4"
  os.system(command)
  command="sudo docker exec "+Base_name+"-FW1 ip addr add 172.16."+str(subNO)+".2/24 dev EFWens3"
  os.system(command)
  command="sudo docker exec "+Base_name+"-FW2 ip addr add 172.16."+str(subNO)+".3/24 dev EFWens3"
  os.system(command)
  command="sudo docker exec "+Base_name+"-FW1 ip link set dev EFWens3 up"
  os.system(command)
  command="sudo docker exec "+Base_name+"-FW2 ip link set dev EFWens3 up"
  os.system(command)
  command="sudo ip link set dev "+Base_name+"-FW1-sub4 up"
  os.system(command)
  command="sudo ip link set dev "+Base_name+"-FW2-sub4 up"
  os.system(command)
  command="sudo docker exec "+Base_name+"-FW1 ip route add default via 172.16."+str(subNO)+".1 dev EFWens3"
  os.system(command)
  command="sudo docker exec "+Base_name+"-FW2 ip route add default via 172.16."+str(subNO)+".1 dev EFWens3"
  os.system(command)
  command="sudo docker exec "+Base_name+"-FW1 ip route add 10.0."+str(subNO)+".0/24 via 172.17."+str(subNO)+".1 dev EFWens4"
  os.system(command)
  command="sudo docker exec "+Base_name+"-FW2 ip route add 10.0."+str(subNO)+".0/24 via 172.17."+str(subNO)+".1 dev EFWens4"
  os.system(command)
  

########################################################## END #################################################


############################################### northBr to -south namespace ####################################


NS_list=inventory['Namespace_names']
No_subnet=len(NS_list)-2
tenantNO=NS_list[0][0]
for i in range(No_subnet):
  subNO=i+1
  bridge_name=str(tenantNO)+"-S-"+str(subNO)+"-northBr"
  NS_name=str(tenantNO)+"-south"

  veth_pair="sudo ip link add "+bridge_name+"-1 type veth peer name "+bridge_name+"-2"
  veth_attach="sudo ip link set "+bridge_name+"-1 netns "+NS_name
  ovs_veth_attach="sudo ovs-vsctl add-port "+bridge_name+" "+bridge_name+"-2"
  add_ip="sudo ip netns exec "+NS_name+" ip addr add 172.16."+str(subNO)+".1/24 dev "+bridge_name+"-1"
  set_linkUP="sudo ip netns exec "+NS_name+" ip link set dev "+bridge_name+"-1 up"
  set_ovslinkUP="sudo ip link set dev "+bridge_name+"-2 up"
  os.system(veth_pair)
  os.system(veth_attach)
  os.system(ovs_veth_attach)
  os.system(add_ip)
  os.system(set_linkUP)
  os.system(set_ovslinkUP)
  command="sudo ip netns exec "+NS_name+" ip route add 10.0."+str(subNO)+".0/24 via 172.16."+str(subNO)+".2 dev "+bridge_name+"-1"
  os.system(command)
  command="sudo ip netns exec "+NS_name+" ip route add 172.17."+str(subNO)+".0/24 via 172.16."+str(subNO)+".2 dev "+bridge_name+"-1"
  os.system(command)

############################################### END ###########################################################

############################################### South namespace to OVS-s ########################################

NS_list=inventory['Namespace_names']
tenantNO=NS_list[0][0]
bridge_name=str(tenantNO)+"-OVS-s"
NS_name=str(tenantNO)+"-south"

veth_pair="sudo ip link add "+bridge_name+"-veth1 type veth peer name "+bridge_name+"-veth2"
veth_attach="sudo ip link set "+bridge_name+"-veth1 netns "+NS_name
ovs_veth_attach="sudo ovs-vsctl add-port "+bridge_name+" "+bridge_name+"-veth2"
add_ip="sudo ip netns exec "+NS_name+" ip addr add 192.168.2.1/24 dev "+bridge_name+"-veth1"
set_linkUP="sudo ip netns exec "+NS_name+" ip link set dev "+bridge_name+"-veth1 up"
set_ovslinkUP="sudo ip link set dev "+bridge_name+"-veth2 up"
loopback="sudo ip netns exec "+NS_name+" ip addr add 127.0.0.1/24 dev lo "
loopbackUP="sudo ip netns exec "+NS_name+" ip link set lo up"
os.system(veth_pair)
os.system(veth_attach)
os.system(ovs_veth_attach)
os.system(add_ip)
os.system(set_linkUP)
os.system(set_ovslinkUP)
os.system(loopback)
os.system(loopbackUP)
command="sudo ip netns exec "+NS_name+" ip route add default via 192.168.2.200 dev "+bridge_name+"-veth1"
os.system(command)


#################################### END ######################################################################

NS_list=inventory['Namespace_names']
tenantNO=NS_list[0][0]
bridge_name=str(tenantNO)+"-OVS-s"
bridge1_name=str(tenantNO)+"-OVS-n"
FW1_name=str(tenantNO)+"-FW1"
FW2_name=str(tenantNO)+"-FW2"
FW1_pid=get_pid(FW1_name)
FW2_pid=get_pid(FW2_name)


command="sudo ip link add EFWens4 type veth peer name "+bridge_name+"-veth4"
os.system(command)
command="sudo ip link set EFWens4 netns "+FW1_pid
os.system(command)
command="sudo ip link add EFWens4 type veth peer name "+bridge_name+"-veth6"
os.system(command)
command="sudo ip link set EFWens4 netns "+FW2_pid
os.system(command)
command="sudo ovs-vsctl add-port "+bridge_name+" "+bridge_name+"-veth4"
os.system(command)
command="sudo ovs-vsctl add-port "+bridge_name+" "+bridge_name+"-veth6"
os.system(command)
command="sudo docker exec "+FW1_name+" ip addr add 192.168.2.2/24 dev EFWens4"
os.system(command)
command="sudo docker exec "+FW2_name+" ip addr add 192.168.2.3/24 dev EFWens4"
os.system(command)
command="sudo docker exec "+FW1_name+" ip link set dev EFWens4 up"
os.system(command)
command="sudo docker exec "+FW2_name+" ip link set dev EFWens4 up"
os.system(command)
command="sudo ip link set dev "+bridge_name+"-veth4 up"
os.system(command)
command="sudo ip link set dev "+bridge_name+"-veth6 up"
os.system(command)


command="sudo ip link add EFWens3 type veth peer name "+bridge1_name+"-veth4"
os.system(command)
command="sudo ip link set EFWens3 netns "+FW1_pid
os.system(command)
command="sudo ip link add EFWens3 type veth peer name "+bridge1_name+"-veth6"
os.system(command)
command="sudo ip link set EFWens3 netns "+FW2_pid
os.system(command)
command="sudo ovs-vsctl add-port "+bridge1_name+" "+bridge1_name+"-veth4"
os.system(command)
command="sudo ovs-vsctl add-port "+bridge1_name+" "+bridge1_name+"-veth6"
os.system(command)
command="sudo docker exec "+FW1_name+" ip addr add 192.168.1.2/24 dev EFWens3"
os.system(command)
command="sudo docker exec "+FW2_name+" ip addr add 192.168.1.3/24 dev EFWens3"
os.system(command)
command="sudo docker exec "+FW1_name+" ip link set dev EFWens3 up"
os.system(command)
command="sudo docker exec "+FW2_name+" ip link set dev EFWens3 up"
os.system(command)
command="sudo ip link set dev "+bridge1_name+"-veth4 up"
os.system(command)
command="sudo ip link set dev "+bridge1_name+"-veth6 up"
os.system(command)

command="sudo docker exec "+FW1_name+" ip route add 10.0.0.0/16 via 192.168.2.1 dev EFWens4"
os.system(command)
command="sudo docker exec "+FW2_name+" ip route add 10.0.0.0/16 via 192.168.2.1 dev EFWens4"
os.system(command)

command="sudo docker exec "+FW1_name+" ip route add 172.16.0.0/15 via 192.168.2.1 dev EFWens4"
os.system(command)
command="sudo docker exec "+FW2_name+" ip route add 172.16.0.0/15 via 192.168.2.1 dev EFWens4"
os.system(command)


#########################################################################END ####################################



NS_list=inventory['Namespace_names']
tenantNO=NS_list[0][0]
bridge_name=str(tenantNO)+"-OVS-n"
NS_name=str(tenantNO)+"-north"

veth_pair="sudo ip link add "+bridge_name+"-veth1 type veth peer name "+bridge_name+"-veth2"
veth_attach="sudo ip link set "+bridge_name+"-veth1 netns "+NS_name
ovs_veth_attach="sudo ovs-vsctl add-port "+bridge_name+" "+bridge_name+"-veth2"
add_ip="sudo ip netns exec "+NS_name+" ip addr add 192.168.1.1/24 dev "+bridge_name+"-veth1"
set_linkUP="sudo ip netns exec "+NS_name+" ip link set dev "+bridge_name+"-veth1 up"
set_ovslinkUP="sudo ip link set dev "+bridge_name+"-veth2 up"
loopback="sudo ip netns exec "+NS_name+" ip addr add 127.0.0.1/24 dev lo "
loopbackUP="sudo ip netns exec "+NS_name+" ip link set lo up"
os.system(veth_pair)
os.system(veth_attach)
os.system(ovs_veth_attach)
os.system(add_ip)
os.system(set_linkUP)
os.system(set_ovslinkUP)
os.system(loopback)
os.system(loopbackUP)
ip_route1="sudo ip netns exec "+NS_name+" ip route add 192.168.2.0/24 via 192.168.1.200 dev "+bridge_name+"-veth1"
ip_route2="sudo ip netns exec "+NS_name+" ip route add 172.16.0.0/15 via 192.168.1.200 dev "+bridge_name+"-veth1"
ip_route3="sudo ip netns exec "+NS_name+" ip route add 10.0.0.0/16 via 192.168.1.200 dev "+bridge_name+"-veth1"

command="sudo docker exec "+FW1_name+" ip route add default via 192.168.1.1 dev EFWens3"
os.system(command)
command="sudo docker exec "+FW2_name+" ip route add default via 192.168.1.1 dev EFWens3"
os.system(command)

os.system(ip_route1)
os.system(ip_route2)
os.system(ip_route3)

command="sudo docker cp ~/conntrackd1.conf "+FW1_name+":/etc/conntrackd/conntrackd.conf"
os.system(command)
command="sudo docker cp ~/conntrackd2.conf "+FW2_name+":/etc/conntrackd/conntrackd.conf"
os.system(command)
command="sudo docker cp ~/keepalivedm.conf "+FW1_name+":/etc/keepalived/keepalived.conf"
os.system(command)
command="sudo docker cp ~/keepaliveds.conf "+FW2_name+":/etc/keepalived/keepalived.conf"
os.system(command)
command="sudo docker cp ~/primary-backup.sh "+FW1_name+":/etc/keepalived/"
os.system(command)
command="sudo docker cp ~/primary-backup.sh "+FW2_name+":/etc/keepalived/"
os.system(command)
command="sudo docker cp ~/ulogd.conf "+FW1_name+":/etc/"
os.system(command)
command="sudo docker cp ~/ulogd.conf "+FW2_name+":/etc/"
os.system(command)
command="sudo docker exec "+FW1_name+" service conntrackd restart"
os.system(command)
command="sudo docker exec "+FW2_name+" service conntrackd restart"
os.system(command)
command="sudo docker exec "+FW1_name+" service keepalived restart"
os.system(command)
command="sudo docker exec "+FW2_name+" service keepalived restart"
os.system(command)
command="sudo docker exec "+FW1_name+" ulogd -d"
os.system(command)
command="sudo docker exec "+FW2_name+" ulogd -d"
os.system(command)


command="sudo ip link add "+str(tenantNO)+"-veth10 type veth peer name hveth1"
os.system(command)
command="sudo ip link set hveth1 netns "+str(tenantNO)+"-north"
os.system(command)
command="sudo ip addr add 10."+str(tenantNO)+".0.1/24 dev "+str(tenantNO)+"-veth10"
os.system(command)
command="sudo ip netns exec "+str(tenantNO)+"-north ip addr add 10."+str(tenantNO)+".0.2/24 dev hveth1"
os.system(command)
command="sudo ip link set dev "+str(tenantNO)+"-veth10 up"
os.system(command)
command="sudo ip netns exec "+str(tenantNO)+"-north ip link set dev hveth1 up"
os.system(command)
command="sudo ip netns exec "+str(tenantNO)+"-north ip route add default via 10."+str(tenantNO)+".0.1 dev hveth1"
os.system(command)
command="sudo ip netns exec "+str(tenantNO)+"-north ip route add default via 10."+str(tenantNO)+".0.1 dev hveth1"
os.system(command)


natrule1="sudo ip netns exec " + str(tenantNO)+"-north  iptables -t nat -A POSTROUTING  -o hveth1 ! -d 192.168.1.0/24 -s 192.168.1.0/24 " + " -j MASQUERADE "

natrule2="sudo ip netns exec " + str(tenantNO)+"-north iptables -t nat -A POSTROUTING  -o hveth1 ! -d 192.168.2.0/24 -s 192.168.2.0/24 " + " -j MASQUERADE "
natrule3="sudo ip netns exec " + str(tenantNO)+"-north iptables -t nat -A POSTROUTING  -o hveth1 -s 172.16.0.0/15 " + " -j MASQUERADE "

natrule4="sudo ip netns exec " + str(tenantNO)+"-north iptables -t nat -A POSTROUTING  -o hveth1 -s 10.0.0.0/8 " + " -j MASQUERADE "
natrule5="sudo iptables -t nat -A POSTROUTING  -o ens3  -s 10."+str(tenantNO)+".0.0/24 -j MASQUERADE "
os.system(natrule1)
os.system(natrule2)
os.system(natrule3)
os.system(natrule4)
os.system(natrule5)
