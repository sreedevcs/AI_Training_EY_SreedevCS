import pandas as pd

###1
df=pd.read_csv('library_loans.csv')
print(df)

###2
print(df[["Member_Name","Book_Category","Fine"]])

###3
print(df[df["Fine"]>50])

###4

def statusfunction(fine):
    if fine==0:
        return "No Fine"
    else:
        return "Fine Due"
df["Status"]=df["Fine"].apply(statusfunction)
print(df)




##5
print(df["Days_Borrowed"].mean())

##6
print(df.groupby("Book_Category")["Fine"].sum())

def hugefine(fine):
    if fine>50:
        return "Huge Fine"
    else:
        return "Not Huge Fine"

df["Fine Heavyness"]=df["Fine"].apply(hugefine)
print(df)