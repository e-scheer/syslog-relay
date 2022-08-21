import matplotlib.pyplot as plt
import numpy as np

DOWNTIME_DURATION=3000

def sum_int(i):
    if i == 0:
        return 0
    else:
        return sum_int(i-1) + ((i/10) + 1) * 30

xpoints = []
ypoints = []
for i in range(50):
    ypoints.append(i)
    xpoints.append(sum_int(i))
    if xpoints[i] > DOWNTIME_DURATION:
        break

plt.plot(xpoints, ypoints, 'o')
plt.xlabel(f'Downtime of {DOWNTIME_DURATION} seconds')
plt.ylabel('Number of attempts')
plt.annotate(str((xpoints[-1], ypoints[-1])), xy=(xpoints[-1], ypoints[-1]) )
plt.annotate(str((xpoints[-2], ypoints[-2])), xy=(xpoints[-2], ypoints[-2]) )
plt.savefig('sum_resume_interval')

print(f"Average difference: {str(sum(np.diff(xpoints)) / len(np.diff(xpoints)))} second(s)")