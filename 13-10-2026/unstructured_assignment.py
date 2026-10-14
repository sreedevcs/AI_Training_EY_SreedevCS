##1
with open('unstructured_data.txt') as f:
    data=f.read()
# print(data)

##2
# a=data.split()
# print("Total Number of Words = ",len(a))

#3
# b=data.splitlines()
# print("Total Number of lines = ",len(b))

#4
# if 'maintenance' in data.lower():
#     print("\'maintenance\' appears")
# else:
#     print("\'maintenance\' not appears")

#5
# print("Count of \'conveyor\' = ",data.lower().count('conveyor'))

#6
# b=data.splitlines()
# for it in b:
#     if 'team' in it.lower():
#         print(it)

#7
# b=data.splitlines()
# for it in b:
#     if 'incident' in it.lower():
#         print(it)

#8
# b=data.splitlines()
# for it in b:
#     if 'damaged' in it.lower():
#         print(it)

#9
# datanew=data.lower()
# print(datanew)
# with open('lowercase_report.txt',"w") as f:
#     f.write(datanew)

#10
# b=data.splitlines()
# m=0
# i=0
# ins=0
# r=0
# o=0
# for it in b:
#     if "maintenance" in it.lower():
#         m=1
#     if "injuries" in it.lower():
#         i=1
#     if "inspection" in it.lower():
#         ins=1
#     if "replacement" in it.lower():
#         r=1
#     if "operations" in it.lower():
#         o=1
# if m==1:
#     print("maintenance : Found")
# elif m==0:
#     print("maintenance : Not Found")
#
# if i==1:
#     print("injuries : Found")
# elif i==0:
#     print("injuries : Not Found")
#
# if ins==1:
#     print("inspection : Found")
# elif ins==0:
#     print("inspection : Not Found")
# if r==1:
#     print("replacement : Found")
# elif r==0:
#     print("replacement : Not Found")
#
# if o==1:
#     print("operations : Found")
# elif o==0:
#     print("operations : Not Found")


keywords = ["maintenance", "injuries", "inspection", "replacement", "operations"]

for k in keywords:
    print(f"{k} : {'Found' if k in data.lower() else 'Not Found'}")