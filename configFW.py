

def configFW(tenant_name,tenant_id,subnet_no,rule):
    FW_name1=str(tenant_id)+"-S-"+str(subnet_no)+"-FW1"
    FW_name1=str(tenant_id)+"-S-"+str(subnet_no)+"-FW2"
    if rule=='d':
        with open('defaultRules.txt','r') as rule:
            rules=rule.readlines()
            for i in rules:
                command="sudo docker exec "+FW_name1+"  " + i 
                os.system(command)
                command="sudo docker exec "+FW_name2+"  " + i
                os.system(command)
    elif rule=='s':
        with open('secureRules.txt','r') as rule:
            rules=rule.readlines()
            for i in rules:
                command="sudo docker exec "+FW_name1+"  " + i 
                os.system(command)
                command="sudo docker exec "+FW_name2+"  " + i
                os.system(command)
    
    elif rule=='c':
        file_name=tenant_name+"-"+str(subnet_no)+"-FW.txt"
        with open(file_name,'r') as rule:
            rules=rule.readlines()
            for i in rules:
                command="sudo docker exec "+FW_name1+"  " + i 
                os.system(command)
                command="sudo docker exec "+FW_name2+"  " + i
                os.system(command)



configFW('harsha',2,3,'d')
