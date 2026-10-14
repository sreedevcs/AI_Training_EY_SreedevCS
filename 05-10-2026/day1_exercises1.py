import pandas as pd
from matplotlib import pyplot as plt

data = {
    "Employee": ["Aisha", "Rahul", "Neha", "Omar", "Priya", "Karan", "Fatima", "Vikram"],
    "Department": ["HR", "IT", "Finance", "IT", "HR", "Finance", "IT", "HR"],
    "Training_Hours": [12, 18, 10, 22, 15, 8, 20, 14],
    "Assessment_Score": [78, 88, 72, 91, 84, 69, 95, 80],
    "Completed": ["Yes", "Yes", "No", "Yes", "Yes", "No", "Yes", "Yes"]
}
df = pd.DataFrame(data)
##1
# print(df)
##2
# print(df[:4])
##3
# print(df[["Employee","Assessment_Score"]])
##4
# print(df[df["Department"]=="IT"]["Employee"])
##5
# print(df[df["Assessment_Score"]>80]["Employee"])
##6
# print(df[df["Completed"]=="Yes"])
##7
# print(df[(df["Department"]=="IT") & (df["Assessment_Score"]>85)])

###8
# def check(score):
#     if score>=75:
#         return "Yes"
#     else:
#         return "No"
# df["Passed"]=df["Assessment_Score"].apply(check)
# print(df)

# ###9
# import numpy as np
# print(np.mean(df["Assessment_Score"]))
# print(df["Assessment_Score"].mean())
#
# ###10
# print(df["Assessment_Score"].max())
# print(df["Assessment_Score"].min())
#
# ###11
# print(df["Training_Hours"].mean())
#
# ###12
# print(df.sort_values("Assessment_Score", ascending=False))
#
# ###13
# print(df.groupby("Department")["Assessment_Score"].mean())
#
# ###14
# print(df.groupby("Department")["Training_Hours"].sum())

# # ###15
# print(df.groupby("Department")["Employee"].count())
#
# ###16
# print((df["Completed"]=="Yes").sum())

###17
# import numpy as np
# scores=df["Assessment_Score"].to_numpy()
# print(scores)
# print(np.mean(scores))
# print(np.max(scores))
# print(np.min(scores))
# print(np.std(scores))

###18
# import matplotlib.pyplot as plt
# avgscorebydept=df.groupby("Department")["Assessment_Score"].mean()
# print(avgscorebydept)
# avgscorebydept.plot(kind="bar")
# plt.xlabel("Department")
# plt.ylabel("Average Assessment Score")
# plt.show()

###19
# totaltrainhours=df.groupby("Department")["Training_Hours"].sum()
# print(totaltrainhours)
# totaltrainhours.plot(kind="bar")
# plt.xlabel("Department")
# plt.ylabel("Total Training Hours")
# plt.show()

###20

# import seaborn as sns
# sns.barplot(data=df,x="Department",y="Assessment_Score")
# plt.show()