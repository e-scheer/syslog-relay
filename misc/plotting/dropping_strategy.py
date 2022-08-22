import numpy as np
from matplotlib import pyplot as plt

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

r = 5000
d = 0.8
s = 45600
p = 0.5

def queue(t):
    r = 5000
    d = 0.8
    s = 45600
    p = 0.5
    return min(r*t, d*s) + min(max(r*t - d*s, 0.0) * p, (1-d)*s)

def drop(t):
    qt = queue(t)
    if qt <= d*s:
        return 0
    elif d*s < qt < s:
        return r*p
    else:
        return r

x = np.arange(0, 20, 1)
plt.plot(x, [queue(t) for t in x], color='red', linestyle='--', label='Main queue size')
plt.plot(x, [drop(t) for t in x], color='blue', label='Discarded messages')

plt.xticks(x)

plt.legend()
plt.xlabel("Time t in seconds")
plt.ylabel("Number of messages")
plt.savefig('dropping_strategy', dpi=300)