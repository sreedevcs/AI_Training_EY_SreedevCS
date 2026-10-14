import json
with open('support_tickets.json') as f:
    data=json.load(f)
# print(data)
# print(data[0])
# print(data[0]["ticket_id"])
# print(data[0]["customer"]["name"])
# for tickets in data:
#     print(tickets["ticket_id"],tickets["issue"])

#print(data[0]["priority"])
# print(data[0].get("priority","NO DATA AVAILABLE"))

# for tickets in data:
#     print(tickets.get("priority","NO DATA AVAILABLE"))

import pandas as pd
df=pd.json_normalize(data)
print(df)