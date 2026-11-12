import json
##1
with open('smart_home_devices.json') as f:
    data=json.load(f)
# print(data)

##2
# for it in data:
#     print("Device ID : ",it['device_id'],"|| Device Type : ",it['device_type'],"|| Room : ",it['room'])

##3
# for it in data:
#     if it['status']=='Active':
#         print(it['device_id'])

##4
# for it in data:
#     if it['metrics']['battery']<60:
#         print(it['device_id'])

##5
# for it in data:
#     if 'temperature' in it['metrics']:
#         print(it['device_id']," : ",it['metrics']['temperature'])

##6
# for it in data:
#     if 'alerts' in it:
#         print(it['device_id']," : ",it['alerts'])

##7
# dcount={}
# for it in data:
#     devicetype=it['device_type']
#
#     if devicetype in dcount:
#         dcount[devicetype]+=1
#     else:
#         dcount[devicetype]=1
#
# for it in dcount.keys():
#     print(it," : ",dcount[it])

##8

# for it in data:
#     if it['metrics']['battery'] >= 70:
#         it['health'] = "Good"
#     elif (it['metrics']['battery'] >= 50) & (it['metrics']['battery'] <= 69):
#         it['health']="Moderate"
#     else:
#         it['health']="Low"
#
# print(data)

#9
# json.dump(data,open('device_health_report.json','w'))

#10
data=json.load(open('device_health_report.json'))
import pandas as pd
df=pd.json_normalize(data)
print(df[['device_id','device_type','room','status','metrics.battery','health']])

#Extra
print(df[(df['status']=='Active') & (df['metrics.battery']<70)][['device_id','device_type','status','metrics.battery']])