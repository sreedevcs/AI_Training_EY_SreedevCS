import numpy as np
prices=np.array([60000,800,1500,60000,800])
print(prices)
print("Average: ",np.mean(prices))
print("Maximum: ",np.max(prices))
print("Minimum: ",np.min(prices))
print(np.ndim(prices))
b=prices*2
print(b)
c=np.array([1,2,3,4,5])
d=prices*c
print(d)
e=prices.dot(c)
print(e)
f=c.T
print(f)
g=np.random.rand(2,3)
print(g)
h=np.random.randint(100,size=10)
print(h)
i=np.random.choice([1,3,8],size=(3,4))
print(i)

k=np.array([[1,2,3],[4,5,6],[7,8,9]])
# np.random.shuffle(k)
# print(k)
l=np.random.permutation(k)
print(l)