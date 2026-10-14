from pylab import *
import numpy as np
import math
# x=np.arange(0,math.pi*2,0.05)
# plot(x,sin(x),label='sin')
# plot(x,cos(x),label='cos')
# show()

# a=np.array([20,30,40,50])
# pie(a)
# show()

import matplotlib.pyplot as plt
x_axis=[1,2,3,4]
y_axis=[2,4,6,8]
plt.bar(x_axis,y_axis)
plt.show()
plt.scatter(x_axis,y_axis)
plt.show()
plt.hist(x_axis)
plt.show()
plt.stem(x_axis,y_axis)
plt.show()