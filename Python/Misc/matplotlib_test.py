import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

print('start')

x = np.arange(0, 7, 0.1);
y = np.sin(x)
plt.plot(x, y)
plt.show()
print('end')
