import pandas as pd
##1
df=pd.read_csv('renewable_energy.csv')
# print(df)

##2
# print(df[(df['Energy_Type']=="Solar") | (df['Energy_Type']=="Wind")])

##3
df["Efficiency_Percent"]=(df["Actual_Output_MW"]/df["Capacity_MW"])*100
# df.to_csv('renewable_energy_updated.csv',index=False)
# print(df)

df=pd.read_csv('renewable_energy_updated.csv')

##4
# print(df[df["Efficiency_Percent"]>85][['Plant_ID','Plant_Name']])

##5
# print(df.groupby('Energy_Type')['Efficiency_Percent'].mean())

##6
# print(df.groupby('Energy_Type')['Maintenance_Cost'].sum())

##7
# print(df[df['Actual_Output_MW']==df['Actual_Output_MW'].max()][['Plant_ID','Plant_Name']])

#8
# df['Cost_Per_MW']=df['Maintenance_Cost']/df['Actual_Output_MW']
# df.to_csv('renewable_energy_updated_2.csv',index=False)


df=pd.read_csv('renewable_energy_updated_2.csv')
# print(df)

##9
# print(df.sort_values('Cost_Per_MW',ascending=True))

#10
# print(df[(df["Efficiency_Percent"]>80)&(df["Maintenance_Cost"]<70000)][['Plant_ID','Plant_Name']])

#Extra

import matplotlib.pyplot as plt
plt.bar(df["Plant_Name"],df["Efficiency_Percent"])
plt.xlabel('Plant Name')
plt.ylabel('Efficiency %')
plt.show()