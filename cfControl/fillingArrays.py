
import numpy as np



xs = np.linspace(1,3,3)


ys = xs

mult = np.empty([len(xs),len(ys)])


# a = np.array([]).reshape((len(xs),len(ys)))
# print(a)
for i in range(0,len(xs)):
    for j in range(0,len(ys)):
        mult[i][j] = xs[i]*ys[j]




print(mult)