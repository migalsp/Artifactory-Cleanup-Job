import requests
import json
import sys

user = "LOGIN"
passwd = "PASSWORD" 

# import json file
with open('results.json') as json_file:
    content_file = json.load(json_file)

# create log file
sys.stdout = open('DeletedArtifacts.txt'', 'w')

#delete artifacts
for i in content_file:
    print(i["uri"])
    print(requests.delete(i["uri"], auth=requests.auth.HTTPBasicAuth(user, passwd)))
