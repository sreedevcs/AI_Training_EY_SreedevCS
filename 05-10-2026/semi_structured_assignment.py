import json
import pandas as pd

##1
with open('festival_events.json') as f:
    data=json.load(f)
print(data)

##2
for item in data:
    print(item['name'])

##3
for item in data:
    print(item['name']," : ",item['location']['city'])

##4
for item in data:
    if item['visitors']>700:
        print("Event Name : ",item['name']," Visitors : ",item['visitors'])

##5
for item in data:
    print(item["name"]," - ",item.get("features","No features listed"))

##6
df=pd.json_normalize(data)
print(df)