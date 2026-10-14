import json
#1
with open('semi_structured_data.json') as f:
    data=json.load(f)
# print(data)

#2
# for it in data:
#     print(it['incident_id'])

#3
# for it in data:
#     print(it['location']['city'])

#4
# for it in data:
#     if it['severity']=='High':
#         print(it['incident_id'])

#5
# for it in data:
#     if it['category']=='Safety':
#         print(it['incident_id'])

#6
# for it in data:
#     print(it['incident_id']," : ",it.get('actions','No actions recorded'))

#7

# counts={}
# for it in data:
#     severity=it['severity']
#     counts[severity]=counts.get(severity,0)+1
# for it in data:
#     print(it['severity']," : ",counts[it['severity']])
##8
# for it in data:
#     it['status']='Open'
# print(data)

##9
# with open('updated_incidents.json','w') as f:
#     json.dump(data,f)


#10

with open('updated_incidents.json') as f:
    updated_data=json.load(f)
    # print(updated_data)

import pandas as pd
df=pd.json_normalize(updated_data)
# print(df)
print(df[['incident_id','severity','category','location.city','location.site']])