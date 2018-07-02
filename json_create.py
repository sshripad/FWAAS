import json

mainDictionary = { 'VPC' : []}

with open('VPC_details.json', 'w') as outfile:
    json.dump(mainDictionary, outfile)
