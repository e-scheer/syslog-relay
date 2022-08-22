import matplotlib.pyplot as plt
import numpy as np
import json
from dateutil.parser import parse

DOWNTIME_DURATION=3000

def sum_int(i):
    if i == 0:
        return 0
    else:
        return sum_int(i-1) + ((i/10) + 1) * 30

xpoints = []
dates = []
with open('rsyslog-logs.log') as file:
    for i, line in enumerate(file):
        js = json.loads(str(line.lstrip()))
        date = parse(js['time'])

        if i == 0:
            xpoints.append(0)
        else:
            xpoints.append(xpoints[i-1] + (date - dates[i-1]).total_seconds())

        dates.append(date)

ypoints = range(len(xpoints))

plt.plot(xpoints, ypoints)
plt.xlabel(f'Downtime of ~{round(xpoints[-1])} seconds')
plt.ylabel('Number of attempts')
plt.savefig('downtime_retry_rsyslog')

print(f"Average difference: {str(sum(np.diff(xpoints)) / len(np.diff(xpoints)))} second(s)")