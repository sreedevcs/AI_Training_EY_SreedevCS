#1
from pandas.core.ops.missing import mask_zero_div_zero

with open('airport_operations_report.txt') as f:
    data=f.read()

# print(data)

#2

# a=data.splitlines()
# b=data.split()
# print("Total words : ",len(b))
# print("Total lines : ",len(a))
# print("Total characters : ",len(data))

#3

# print("Count of \'flight\' : ",data.lower().count('flight'))
# print("Count of \'runway\' : ",data.lower().count('runway'))
# print("Count of \'operations\' : ",data.lower().count('operations'))
# print("Count of \'reported\' : ",data.lower().count('reported'))

#4

# for it in data.splitlines():
#     if "runway" in it.lower():
#         print(it)

#5
# for it in data.splitlines():
#     if "delay" in it.lower() or "delayed" in it.lower() or "delays" in it.lower():
#         print(it)

#6
# for it in data.splitlines():
#     if "reported" in it.lower():
#         print(it)
#7

# words=['emergency','inspection','weather','passengers','maintenance']
# for it in words:
#     if it in data.lower():
#         print(it," : Found")
#     else:
#         print(it," : Not Found")


#8
# countdata={}
# words=['flight','runway','operations']
# for it in words:
#     countdata[it]=data.lower().count(it)
# print(countdata)

#9

l=data.splitlines()
maxline=""
for it in l:
    if len(it)>len(maxline):
        maxline=it
print(maxline)

#10

for it in data.splitlines():
    if "delays" in it or "weather" in it:
        with open("filtered_airport_report.txt","a") as f:
            f.write(it)

