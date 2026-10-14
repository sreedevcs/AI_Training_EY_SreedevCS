##1
with open('wildlife_report.txt') as f:
    data=f.read()
print(data)

##2
words=data.split()
print(words)

##3
if "elephant" in data.lower():
    print("The word \'elephant\' is present")
else:
    print("The word \'elephant\' is not present")

##4
print("Count of the word \'elephant\'= ",data.count("elephant"))

##5
print("Lines containing \'trail\' are:")
# count=0
for item in data.splitlines():
    if "trail" in item.lower():
        print(item)
#        count=count+1
# print(count)

##6
print("Lines containing \'animal\' are:")
for item in data.splitlines():
    if "animal" in item:
        print(item)