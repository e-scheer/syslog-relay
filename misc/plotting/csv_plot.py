from ast import arg
from fileinput import filename
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import argparse
from cycler import cycler
import os

def tofloat(x):
    if type(x) == str:
        if '.' in x:
            return float(x.replace(',', ''))
        else:
            return int(x.replace(',', ''))
    else:
        return x

def interpolate_gaps(values, limit=None):
    """
    See: https://stackoverflow.com/questions/36455083/how-to-plot-and-work-with-nan-values-in-matplotlib
    Fill gaps using linear interpolation, optionally only fill gaps up to a
    size of `limit`.
    """
    values = np.asarray(values)
    i = np.arange(values.size)
    valid = np.isfinite(values)
    filled = np.interp(i, i[valid], values[valid])

    if limit is not None:
        invalid = ~valid
        for n in range(1, limit+1):
            invalid[:-n] &= invalid[n:]
        filled[invalid] = np.nan

    return filled

parser = argparse.ArgumentParser()
parser.add_argument('--rm-column', default=None, type=str)
parser.add_argument('-a', '--area', action='store_true')
parser.add_argument('-l', '--legend-outside', action='store_true')
parser.add_argument('--two-yaxis', action='store_true')

args = parser.parse_args()

monochrome = (cycler('color', ['k']) * cycler('marker', ['', '.']) * cycler('linestyle', ['-', '--', ':', '-.']))
#monochrome = (cycler('color', ['k']) * cycler('linestyle', ['-', '--', ':', '-.']) * cycler('marker', ['^',',', '.']))

bar_cycle = (cycler('hatch', ['///', '--', '...','\///', 'xxx', '\\\\']) * cycler('zorder', [10]))
styles = bar_cycle()

plt.rcParams["figure.figsize"] = [7.00, 3.50]
plt.rcParams["figure.autolayout"] = True
plt.rcParams['axes.prop_cycle'] = monochrome

fig, ax = plt.subplots(1,1)
ax.grid()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

ax_ylabel = None

interval = 0
ax2 = ax.twinx() if args.two_yaxis else None

files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.csv')]
if len(files) == 0:
    print('No file found')
    exit(0)

for f in files:
    df = pd.read_csv(f)

    # loop on columns name
    blacklist_keywords = ['Filters', 'keyword'] 
    if args.rm_column:
        blacklist_keywords += [str(args.rm_column)]

    timestamp_index = 0
    xaxis = None
    for i, column in enumerate(df):
        if True in [keyword in column for keyword in blacklist_keywords]:
            continue
        
        if 'timestamp' in column:
            timestamp_index = i
            if df[column][0].count(':') == 1:
                xaxis = pd.to_datetime(df[column], format="%H:%M")
            else:
                xaxis = pd.to_datetime(df[column], format="%H:%M:%S")
            xaxis = pd.to_timedelta(xaxis.dt.time.astype(str)).dt.total_seconds()

            # shift if timestamp during 00h00
            for delta in xaxis:
                if delta == 0:
                    xaxis = (xaxis + np.full(len(xaxis), 86400 - xaxis[0])) % 86400
                    break

            xaxis -= np.full(len(xaxis), xaxis[0])
            interval = xaxis[1] - xaxis[0]
        else:
            subax = ax

            if xaxis is None:
                print('Could not find timestamp column')
                exit(0)

            if ax_ylabel is None:
                if args.two_yaxis:
                    ax_ylabel = column
                else:
                    ax_ylabel = 'Number of messages'

            if args.two_yaxis:
                if i == timestamp_index + 2:
                    subax = ax2
                    subax.set_ylabel(column)
                    ax.plot([], []) # cycle style
                else:
                    ax2.plot([], []) # cycle style

            yaxis = interpolate_gaps([tofloat(x) for x in df[column]])
            print(f"Statistics of {column}: avg={np.mean(yaxis)}, max={np.max(yaxis)}, min={np.min(yaxis)}")
            if args.area:
                subax.fill_between(xaxis, yaxis, label=column, color= 'none', edgecolor="black", **next(styles))
            else:
                subax.plot(xaxis, yaxis, label=column)

# adds up both yaxis
h1, l1 = ax.get_legend_handles_labels()
if args.two_yaxis:
    h2, l2 = ax2.get_legend_handles_labels()
    h1 += h2
    l1 += l2

if args.legend_outside:
    plt.legend(h1, l1, bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
                    mode="expand")
else:
    plt.legend(h1, l1)
    
ax.set_xlabel(f'Timestamp per {round(interval, 4):g} seconds')
ax.set_ylabel(ax_ylabel)

plt.tight_layout()

plt.savefig(files[0].split('.')[0], dpi=300)