import requests
import json
import time
from datetime import datetime

artifactory_uri = "http://ARTIFACTORY SERVER URL /artifactory"
artifactory_repo = "REPO NAME"
user = 'API USER'
passwd = 'PASSWORD'
build_type = "BUILD-TYPE"
array_web = [], array_web_branch_properties = [], array_artifact_properties = [], result = [], export_json = []
ignore_api_storage = "/api/storage"

# set createSince parameter in days
create_since_days = 60


# init artifact object
class artifact(object):
    def __init__(self, url, art_timestamp, branch_name, build_type):
        self.url = url
        self.art_timestamp = art_timestamp
        self.branch_name = branch_name
        self.build_type = build_type


# This function converts milliseconds to a date
def convert_milli_to_date(milliseconds):
    return str(datetime.fromtimestamp(int((str(milliseconds))[0:-3])).strftime('%d/%m/%Y %H:%M:%S'))


# needed period of time to sort
def sort_specific_date():
    current_time = int(round(time.time() * 1000))
    day_epoch = 86400000
    return int(current_time - create_since_days * day_epoch)


# api get request
content_web = requests.get(artifactory_uri + "/api/search/prop?build_type=" + build_type + "&repos=" + artifactory_repo,
                           auth=requests.auth.HTTPBasicAuth(user, passwd))
content_web = content_web.json()
# add data to array_web
for i in content_web["results"]:
    array_web.append(str(i["uri"]))

# In this loop, it'schecked that branch name! = Release and the result is written to the array
# array_web_branch_properties
for i in array_web:
    content_web_branch_properties = requests.get(i + "?properties=branch_name",
                                                 auth=requests.auth.HTTPBasicAuth(user, passwd))
    content_web_branch_properties = content_web_branch_properties.json()
    for i in content_web_branch_properties["properties"]["branch_name"]:
        if i.find("release") == -1:
            array_web_branch_properties.append(content_web_branch_properties["uri"])
        else:
            pass

# In this loop, I collect additional parameters of a specific artifact and add them to the object in
# array_artifact_properties
for i in array_web_branch_properties:
    content_web_properties = requests.get(i + "?properties", auth=requests.auth.HTTPBasicAuth(user, passwd))
    content_web_properties = content_web_properties.json()
    url = content_web_properties["uri"]
    create_date = str(content_web_properties["properties"]["build.timestamp"])[2:-2]
    branch = str(content_web_properties["properties"]["branch_name"])[2:-2]
    build = str(content_web_properties["properties"]["build_type"])[2:-2]
    array_artifact_properties.append(artifact(url, create_date, branch, build))

# In this array, I sort the artifacts by date
for i in array_artifact_properties:
    if int(i.art_timestamp) <= sort_specific_date():
        i.art_timestamp = convert_milli_to_date(i.art_timestamp)
        i.url = str(i.url).replace(ignore_api_storage, "")
        result.append(i)
    else:
        pass

# export to json
for i in result:
    content = {"uri": i.url, "branch_name": i.branch_name, "build_type": i.build_type, "date": i.art_timestamp}
    export_json.append(content)
with open('results.json', 'w') as outfile:
    json.dump(export_json, outfile, indent=1)
