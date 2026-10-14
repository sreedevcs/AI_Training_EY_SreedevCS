import pandas as pd
df=pd.read_csv('day1_data.csv')
print(df)
print(df.columns)
print(df.head())
print(df.shape)
print(df[["Station","kWh","Amount"]])