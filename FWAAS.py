import os
import sys
import sqlite3
import time
import paramiko
import json
import yaml
import iptc

def is_tenant_already_exists(tenant_name):

    with open("VPC_Database.txt","r") as fwrite:
        #print(fwrite.readline())
        temp=fwrite.readlines()

    if len(temp)==0:
        return(False)

    for tenants in temp:
        tenants=tenants.split(" ")
        if (tenants[0] == tenant_name):
            return(True)
    return(False)

def custom_rule(tenant_name,subnet):
    fname = tenant_name + "-" +str(subnet)+ "-FW.txt"
    val = 'custom'
    if(val == 'custom'):
	num = int(raw_input("Enter the number of rules you want to enter"))
        for i in range(0,num):
                pro = raw_input("Choose a protocol tcp/udp: ")

                port = raw_input("Choose a valid port number: ")

                source = raw_input("Enter a source address network: ")

                dest = raw_input("Enter a destination address network: ")

                rul = raw_input("Choose a action ACCEPT/DROP : ")
                r = "iptables -I INPUT"
                rule = iptc.Rule()
                rule.protocol = pro
                if(port != "0"):
                        rule.dport=port
                        r += " " + "--dport "+port
                if(source != "0"):
                        rule.src = source
                        r += " " + "-s " + source
                if(dest != "0"):
                        rule.dst = dest
                        r += " " + "-d " + dest
                if(rul != "0"):
                        rule.target = iptc.Target(rule, rul)
                        r += " " + "-j " + rul
                chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "INPUT")
                #print(rule)
                #print(r)
                with open(fname,"a") as f:
                        f.write(r)
                        f.write("\n")

def configFW(tenant_name,tenant_id,subnet_no,rule):

    global host_bit
    if host_bit==1:
        hostname="192.168.125.217"
    else:
        hostname="192.168.125.171"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username='host', password='root')
    channel = client.invoke_shell()
    time.sleep(1)
    channel.recv(9999)
    channel.send("\n")
    time.sleep(1)

    FW_name1=str(tenant_id)+"-S-"+str(subnet_no)+"-FW1"
    FW_name2=str(tenant_id)+"-S-"+str(subnet_no)+"-FW2"

    if rule=='d':
        with open('defaultRules.txt','r') as rule:
            rules=rule.readlines()
            for i in rules:
                command="sudo docker exec "+FW_name1+"  " + i
                channel.send(command + "\n")
                while not channel.recv_ready():
                    time.sleep(0.1)
                output = channel.recv(9999)
                time.sleep(0.1)
                channel.send("root" + "\n")

                command="sudo docker exec "+FW_name2+"  " + i
                channel.send(command + "\n")
                while not channel.recv_ready():
                    time.sleep(0.1)
                output = channel.recv(9999)
                time.sleep(0.1)
                channel.send("root" + "\n")

    elif rule=='s':
        with open('secureRules.txt','r') as rule:
            rules=rule.readlines()
            for i in rules:
                command="sudo docker exec "+FW_name1+"  " + i
                channel.send(command + "\n")
                while not channel.recv_ready():
                    time.sleep(0.1)
                output = channel.recv(9999)
                time.sleep(0.1)
                channel.send("root" + "\n")

                command="sudo docker exec "+FW_name2+"  " + i
                channel.send(command + "\n")
                while not channel.recv_ready():
                    time.sleep(0.1)
                output = channel.recv(9999)
                time.sleep(0.1)
                channel.send("root" + "\n")

    elif rule=='c':
        file_name=tenant_name+"-"+str(subnet_no)+"-FW.txt"
        with open(file_name,'r') as rule:
            rules=rule.readlines()
            for i in rules:
                command="sudo docker exec "+FW_name1+"  " + i
                channel.send(command + "\n")
                while not channel.recv_ready():
                    time.sleep(0.1)
                output = channel.recv(9999)
                time.sleep(0.1)
                channel.send("root" + "\n")

                command="sudo docker exec "+FW_name2+"  " + i
                channel.send(command + "\n")
                while not channel.recv_ready():
                    time.sleep(0.1)
                output = channel.recv(9999)
                time.sleep(0.1)
                channel.send("root" + "\n")


def creat_new_subnet():

    fromFile = json.load(open('VPC_details.json'))
    Tenant_name=raw_input("Please enter the name of the Tenant\n")
    subnet_name=raw_input("please enter the name of subnet\n")
    No_vm= input("Please enter the number of VM required in the subnet\n")
    need_internalFW=raw_input("Do you need internal FW for this subnet? \n press Y for YES \n press N for NO \n ")
    if need_internalFW =='y':
    	firewallType =raw_input("Please choose the firewall type : Custom (C) , Default (D), Secure (S)")
    for start in fromFile:
      arr=fromFile[start]
      print(len(arr))
      #print('Array : ',arr)
      for m in range(len(arr)):
        #print(arr[m])
        for elem in arr[m] :
            if(elem == 'tenantName'):
		 nameOfTenant = fromFile['VPC'][m]['tenantName']
		 if nameOfTenant==Tenant_name:
                    fromFile['VPC'][m]['noOfSubnets']=fromFile['VPC'][m]['noOfSubnets']+1
                    for d in fromFile['VPC'][m]:
                        if d =='internalDetails':
                            for q in fromFile['VPC'][m]['internalDetails']:
                                #print( q )
                                array =[q]
                                newDetails = {}
                                #subnet_name=raw_input("please enter the name of subnet\n")
				newDetails['subnetName'] = subnet_name
                        	#No_vm= input("Please enter the number of VM required in the subnet\n")
                        	#for i in range(1,No_vm+1):
                            		#dct_str['VMcontainer_names'].append(tenantNumber+'-S-'+sub_no+'-V-'+str(i))
                        	newDetails['noOfVMs'] = No_vm
                        	#need_internalFW=raw_input("Do you need internal FW for this subnet? \n press Y for YES \n press N for NO\n")
                        	newDetails['internalFirewallNeeded'] = need_internalFW
                        	if need_internalFW =='y':
                                	#firewallType =raw_input("Please choose the firewall type : Custom (C) , Default (D), Secure (S) \n")
                                	#newDetails['firewallType'] = firewallType
                                	FW_fileName = "FW_"+Tenant_name+"_"+subnet_name+".txt"
                                	newDetails['FW_fileName'] = FW_fileName
                        	array.append(newDetails)
                		#newDetails['internalDetails'] = array
                		fromFile['VPC'][m]['internalDetails']= array
        print('---------------------')
	file = open('VPC_details.json', 'r+')
	file.truncate()

        with open('VPC_details.json', 'w') as outfile:
    			json.dump(fromFile, outfile)
                #inventoryFile = str(Tenant_name)+"_device_inventory.yml"
                #with open(inventoryFile, 'a+') as out_file:
                #        yaml.safe_dump(dct_str, out_file, indent=4,default_flow_style=False)





def CreateNewVPC():

    #conn = sqlite3.connect('Tenant_DB.db')
    #cur = conn.cursor()
    #arpita
    data = json.load(open('VPC_details.json'))
    for elem in data:
    	if elem == 'VPC':
		noOfTenants = len(data[elem])
        	print('Number of tenants ',noOfTenants)
                tenantNumber= str(noOfTenants+1)
        	dataToBeStored = {}
                dataToBeStored['tenantID'] = tenantNumber
    		Tenant_name=raw_input("Please enter the name of the tenant\n")
    		dataToBeStored['tenantName'] = Tenant_name
    		No_subnet= int(raw_input("How many subnets do you want in your VPC\n"))
    		dataToBeStored['noOfSubnets'] =  No_subnet
                array = []
                dct_str = {'FWcontainer_names':[tenantNumber+'-FW1',tenantNumber+'-FW2'],
			    'VMcontainer_names':[], 'OVSbridge_names': [tenantNumber+'-OVS-n', tenantNumber+'-OVS-s'],
                             'Namespace_names':[tenantNumber+'-north', tenantNumber+'-south']	}
    		for sub_no in range(1,No_subnet+1):
                        sub_no =str(sub_no)
        		subnet_name=raw_input("please enter the name of subnet\n")
                        dct_str['OVSbridge_names'].append(tenantNumber+'-S-'+sub_no+'-southBr')
                        dct_str['OVSbridge_names'].append(tenantNumber+'-S-'+sub_no+'-northBr')
                        dct_str['OVSbridge_names'].append(tenantNumber+'-S-'+sub_no+'-Br')
                        dct_str['Namespace_names'].append(tenantNumber+'-S-'+sub_no+'-S')
                        #Creating FW containers
                        dct_str['FWcontainer_names'].append(tenantNumber+'-S-'+sub_no+'-FW1')
                        dct_str['FWcontainer_names'].append(tenantNumber+'-S-'+sub_no+'-FW2')

			internalDetails = {}
                        internalDetails['subnetName'] = subnet_name
                        internalDetails['subnetID'] = sub_no
                        No_vm= input("Please enter the number of VM required in the subnet\n")
                        for i in range(1,No_vm+1):
			    dct_str['VMcontainer_names'].append(tenantNumber+'-S-'+sub_no+'-V-'+str(i))
                        internalDetails['noOfVMs'] = No_vm
                        need_internalFW=raw_input("Do you need internal FW for this subnet? \n press Y for YES \n press N for NO\n")
                        internalDetails['internalFirewallNeeded'] = need_internalFW
                        if need_internalFW.lower() =='y':
                                firewallType =raw_input("Please choose the firewall type : Custom (C) , Default (D), Secure (S) \n")
                                internalDetails['firewallType'] = firewallType
                                FW_fileName = "FW_"+Tenant_name+"_"+subnet_name+".txt"
                                internalDetails['FW_fileName'] = FW_fileName
        		array.append(internalDetails)
     		dataToBeStored['internalDetails'] = array
     		data['VPC'].append(dataToBeStored)
    		file = open('VPC_details.json', 'r+')
    		file.truncate()

    	       	with open('VPC_details.json', 'w') as outfile:
    			json.dump(data, outfile)
	       	print("----")
               	inventoryFile = str(Tenant_name)+"_device_inventory.yml"
               	with open(inventoryFile, 'a+') as out_file:
    			yaml.safe_dump(dct_str, out_file, indent=4,default_flow_style=False)
	        command = "sudo ansible-playbook Make_network.yml --extra-vars \"tenant_name="+Tenant_name+"\""
                os.system(command)
                print('--------Executed Ansible script--------------')
                readFWChoice(Tenant_name)
		print("---------Creating firewall file-----------")
                fname = Tenant_name +"-FW.txt"
                with open(fname,"a") as f:
                        #f.write(r)
                        f.write("\n")



def readFWChoice(tenantName):
    print('-------------------Entering firewall rules--------------------------')
    fromFile = json.load(open('VPC_details.json'))
    print('=========')
    for start in fromFile:
        arr =fromFile[start]
        for m in range(len(arr)):
            for elem in arr[m]:
                if(elem == 'tenantName'):
                    nameOfTenant = fromFile['VPC'][m]['tenantName']
                    if nameOfTenant==tenantName:
                        internalDetails = fromFile['VPC'][m]['internalDetails']
                        for i in range(0,len(internalDetails)):
                             fwType= internalDetails[i]['firewallType']
                             if(fwType != None):
                                 fwType = fwType.lower()
                             else:
                                 continue

                             if(fwType =='c'):
                                 print("----Calling custom rule----")
                                 custom_rule(tenantName,internalDetails[i]['subnetID'])
                                 print('--------Pushing FW rules---------------')
                                 configFW(tenantName,fromFile['VPC'][m]['tenantID'],internalDetails[i]['subnetID'],fwType)
                             if(fwType =='d'):
                                 print('--------Pushing FW rules---------------')
                                 configFW(tenantName,fromFile['VPC'][m]['tenantID'],internalDetails[i]['subnetID'],fwType)
                             if(fwType =='s'):
                                 print('--------Pushing FW rules---------------')
                                 configFW(tenantName,fromFile['VPC'][m]['tenantID'],internalDetails[i]['subnetID'],fwType)





def EditIPtables():
    print("-------------Please enter the correct values only , no exception handling is done---------------- ")
    choice = input('Where do you want to enter the firewall rule ? '
               '1 : Exterior '
               '2 : Interior\n');
    #print(choice)
    global host_bit
    if host_bit==1:
        hostname="192.168.125.217"
    else:
        hostname="192.168.125.171"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username='host', password='root')
    channel = client.invoke_shell()
    time.sleep(1)
    channel.recv(9999)
    channel.send("\n")
    time.sleep(1)

    if choice==1:
        hostname=raw_input("Enter the tenant name where you want to implement the rule")
        rule=raw_input("Enter the rule to be implemented. Please enter the exact rule WITHOUT SUDO : \n")
        tenant_id= fetchTenantID(hostname)
       	if tenant_id == "none":
                print("Invalid tenant name")
                return
       	FW_name1=str(tenant_id)+"-FW1"
       	FW_name2=str(tenant_id)+"-FW2"
       	command="sudo docker exec "+FW_name1+"  " + rule
        channel.send(command + "\n")
        while not channel.recv_ready():
            time.sleep(0.1)
        output = channel.recv(9999)
        time.sleep(0.1)
        channel.send("root" + "\n")
       	command="sudo docker exec "+FW_name2+"  " + rule
       	channel.send(command + "\n")
        while not channel.recv_ready():
            time.sleep(0.1)
        output = channel.recv(9999)
        time.sleep(0.1)
        channel.send("root" + "\n")


	print("***************EXECUTED SUCCESSFULLY**************************")
        print("********STORING THE STATE****************")
        fname = hostname +"-FW.txt"
        with open(fname,"a") as f:
                  f.write(rule)
                  f.write("\n")

    elif choice==2:
        tenantNumberEntered = raw_input("Enter the tenant number where rule needs to be implemented : ")
        subnetNumberEntered = raw_input("Enter the subnet number of the tenant where rule needs to be implemented : ")
        rule=raw_input("Enter the rule to be implemented. Please enter the exact rule WITHOUT SUDO : \n")
        #Work in progress
	print("***************EXECUTED SUCCESSFULLY**************************")
	print("********STORING THE STATE****************")








def ExternalFWrule(hostname,rule):

    commands = [rule]
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username='root', password='root')
    channel = client.invoke_shell()

    # clear welcome message and send newline
    time.sleep(1)
    channel.recv(9999)
    channel.send("\n")
    time.sleep(1)

    for command in commands:
        channel.send(command + "\n")
        while not channel.recv_ready(): #Wait for the server to read and respond
            time.sleep(0.1)
        time.sleep(0.1) #wait enough for writing
        output = channel.recv(9999) #read
        time.sleep(0.1)
        channel.send("root" + "\n")
    channel.close()
    return()




def deleteTenant():
        fromFile = json.load(open('VPC_details.json'))
        #print('Existing tenants',fromFile)
	#print(fromFile)
	print('=========')
        toDelete = raw_input("Please enter the name of the tenant to delete \n")
	for start in fromFile:
    		arr =fromFile[start]
    		for m in range(0,len(arr)):
        		for elem in arr[m] :
            			if(elem == 'tenantName'):
                			nameOfTenant = fromFile['VPC'][m]['tenantName']
                			if nameOfTenant==toDelete :
                    				del fromFile['VPC'][m]
                    				print("Deleted tenant : " +nameOfTenant)

	#print('data left is', fromFile)

						file = open('VPC_details.json', 'r+')
						file.truncate()

						with open('VPC_details.json', 'w') as outfile:
    							json.dump(fromFile, outfile)

						command = "sudo ansible-playbook deleteTenant.yml --extra-vars \"tenant_name="+toDelete+"\""
        					os.system(command)
        					command2= "sudo rm "+toDelete+"_device_inventory.yml"
						os.system(command2)
					  #else:
					#	print('---Tenant not found-----')

def viewTenantDetails() :
    fromFile = json.load(open('VPC_details.json'))
    print('=========')
    for start in fromFile:
        arr =fromFile[start]
        for m in range(len(arr)):
            for elem in arr[m] :
                if(elem == 'tenantName'):
                    nameOfTenant = fromFile['VPC'][m]['tenantName']
                    tenantID = fromFile['VPC'][m]['tenantID']
                    print("Tenant name : " +nameOfTenant+ " , Tenant ID : " + tenantID)

def fetchTenantID(tenantName):
	fromFile = json.load(open('VPC_details.json'))
	print('=========')
	for start in fromFile:
    	 	arr =fromFile[start]
    		for m in range(len(arr)):
        		for elem in arr[m] :
            			if(elem == 'tenantName'):
                			nameOfTenant = fromFile['VPC'][m]['tenantName']
                			if nameOfTenant==tenantName:
                                                #print(tenantName)
				     		return fromFile['VPC'][m]['tenantID']
	return "none"
def get_alertlogs():

    tenant_name=raw_input("Enter the tenant name \n")
    tenant_no=fetchTenantID(tenant_name)
    command="sudo docker exec "+str(tenant_no)+"-FW1 cat /var/logs/alertLogs"
    global host_bit
    if host_bit==1:
        hostname="192.168.125.217"
    else:
        hostname="192.168.125.171"

    tenant_no=1
    subnet_no=1
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username='host', password='root')
    stdin, stdout, stderr = client.exec_command(command)
    stdout=stdout.readlines()
    client.close()

    for line in stdout:
        output=output+line
        if output!="":
            print output
        else:
            print "There was no output for this command"


def alertLogging():
    print('alert')
    tenantName= raw_input("Enter the tenant name for applying alert logs \n")
    tenant_id = fetchTenantID(tenantName)
    if tenant_id == "none":
        print("Invalid tenant name")
        return
    sourceIP = raw_input("Please enter the source IP you want to track \n")
    global host_bit
    if host_bit==1:
        hostname="192.168.125.217"
    else:
        hostname="192.168.125.171"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username='host', password='root')
    channel = client.invoke_shell()
    time.sleep(1)
    channel.recv(9999)
    channel.send("\n")
    time.sleep(1)
    FW_name1=str(tenant_id)+"-FW1"
    FW_name2=str(tenant_id)+"-FW2"
    rule = "iptables -I FORWARD -s "+sourceIP +"  -j NFLOG --nflog-group 0 "
    command="sudo docker exec "+FW_name1+"  " + rule

    channel.send(command + "\n")
    while not channel.recv_ready():
        time.sleep(0.1)
    output = channel.recv(9999)
    time.sleep(0.1)
    channel.send("root" + "\n")

    command="sudo docker exec "+FW_name2+"  " + rule

    channel.send(command + "\n")
    while not channel.recv_ready():
        time.sleep(0.1)
    output = channel.recv(9999)
    time.sleep(0.1)
    channel.send("root" + "\n")

    print('***************Alert logs implemented**********************')

def DMZoption():

    global host_bit
    if host_bit==1:
        hostname="192.168.125.217"
    else:
        hostname="192.168.125.171"
    tenant_name=raw_input("Please enter the tenant name\n")
    tenant_no=fetchTenantID(tenant_name)
    subnet_no=int(raw_input("Enter the subnet number\n"))
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username='host', password='root')
    channel = client.invoke_shell()
    time.sleep(1)
    channel.recv(9999)
    channel.send("\n")
    time.sleep(1)

    command="sudo iptables -A PREROUTING -t nat -i ens3 -p tcp --dport 8"+str(subnet_no -1)+" -j DNAT --to 10."+str(tenant_no)+".0.2:8"+str(subnet_no)
    channel.send(command + "\n")
    while not channel.recv_ready():
        time.sleep(0.1)
    output = channel.recv(9999)
    time.sleep(0.1)

    command="sudo ip netns exec "+str(tenant_no)+"-north sudo iptables -A PREROUTING -t nat -i hveth1 -p tcp --dport 8"+str(subnet_no)+" -j DNAT --to 10.0."+str(subnet_no)+".1:80"
    channel.send(command + "\n")
    while not channel.recv_ready():
        time.sleep(0.1)
    output = channel.recv(9999)
    time.sleep(0.1)
    channel.send("root" + "\n")
    channel.close()

host_bit=1
def main():


    print("Welcome")


    print("")

    while True:
        a="""#####################################################################################################################
             #                                                                                                                   #
             #       Press 1: Create A new VPC                                                                                   #
             #       Press 2: Add a new Subnet to existing network                                                               #
             #       Press 3: Add VM to existing Subnet                                                                          #
             #       Press 4: Edit Firewall rules to Internal/External Firewall                                                  #                                                        #
             #       Press 5: Create DMZ environment                                                                          #
             #       Press 6: Get alert log                                                                      #                                                                                                     #
             #       Press 7: Delete a tenant                                                                                    #
             #       Press 8: To EXIT
	     #       Press 9: Use Alert logging feature
                     Press 10 : View Tenant names and ID                                                                             #
             #                                                                                                                   #
             #####################################################################################################################"""
        print("WELCOME........Please choose the Task\n\n\n")
        print(a)

        task_name=int(raw_input("\n\n\n\n\n\n\n"))

        if task_name==1:
            CreateNewVPC()
        elif task_name==2:
            creat_new_subnet()
        elif task_name==3:
            Create_new_VM()
        elif task_name==4:
            EditIPtables()
        elif task_name==5:
            DMZoption()
        elif task_name==6:
            get_alertlogs()
        elif task_name==7:
            deleteTenant()
        elif task_name==8:
            break
        elif task_name==9:
	    alertLogging()
        elif task_name==10:
             viewTenantDetails()
        else:
            print("INVALID ENTRY\n")
    return()


if __name__ == "__main__":
    main()
