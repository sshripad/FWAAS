import iptc
import sys
import os

#print("---------------------IP table Rules----------------------")
#print("\nSecurity groups: \n")
#print("Default group: TCP ports allowed are 80, 22, 443\n")
print("Secure group: TCP port allowed: 22 \n")
#val = raw_input("Choose a group: default/secure/custom group: ")
fname =  + "-subnet" + "-FW.txt"

if(val == 'custom'):
	num = int(raw_input("Enter the number of rules you want to enter"))
	for i in range(0,num):
		pro = raw_input("Choose a protocol tcp/udp: ")

		port = raw_input("Choose a valid port number: ")

		source = raw_input("Enter a source address network: ")

		dest = raw_input("Enter a destination address network: ")

		rul = raw_input("Choose a action ACCEPT/DROP : ")
		r = "sudo iptables -I INPUT"
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
