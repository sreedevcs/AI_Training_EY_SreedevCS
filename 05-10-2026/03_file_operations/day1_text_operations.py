with open('day1_textfile.txt') as f:
    data=f.read()
print(data)

words=data.split()
print("Total words = ",len(words))
print(words)
if "vibration" in data.lower():
    print("Vibration is found")

print("Count of word vibration = ",data.lower().count("vibration"))

for item in words:
    if item.lower()=="the":
        print("\'The\' is found")
        break

if "the" in data.lower():
    print("\'The\' is found using other way")
    print("Count of \'the\' is = ",data.lower().count("the"))