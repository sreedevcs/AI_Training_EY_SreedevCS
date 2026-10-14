import pandas as pd
#1
df=pd.read_csv('structured_data.csv')
# print(df)

#2
# print(df[['Shipment_ID','Origin','Destination','Cost']])

#3
# print(df[df['Mode']=='Road'])

#4
# print(df[df['Weight_Kg']>150])

#5
# df['Cost_Per_Km']=df['Cost']/df['Distance_Km']
# print(df)

#6
# print("Average Cost = ",df['Cost'].mean())
# print("Maximum Cost = ",df['Cost'].max())
# print("Minimum Cost = ",df['Cost'].min())

#7
# print(df.groupby('Mode')['Cost'].sum())

#8
# print(df.groupby('Mode')['Weight_Kg'].mean())

#9
# print(df.sort_values('Cost',ascending=False))

#10
print(df[(df['Delivery_Days']<=1) & (df['Cost']<5000)])