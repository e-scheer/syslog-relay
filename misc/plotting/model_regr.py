import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from itertools import cycle

lines = ["--","-.",":"]
linecycler = cycle(lines)

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

def plot_polymonial(x_data, poly_reg, regressor, figname, y_data=None, y_points=[]):
    plt.clf()

    if y_data:
        plt.scatter(x_data, y_data, color='red', label='Data')
    
    for point in y_points:
        plt.axhline(y=point, linestyle=next(linecycler), label=f'Line at y={point} msgs/s')

    plt.plot(x_data, regressor.predict(poly_reg.transform(x_data)), label='Quadratic regression')
    plt.xlabel('Number of messages per second')
    plt.ylabel('Main queue size')
    plt.legend()
    plt.savefig(figname, dpi=300)


def main():
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True

    df = pd.read_csv('predict_queue_size_rcv_msgs.csv')

    # https://www.youtube.com/watch?v=peBOquJ3fDo&t=683s

    raw_queue_size = [tofloat(x) for x in df.iloc[:, 1]]
    raw_msgs_rate = [tofloat(x) for x in df.iloc[:, 2]]

    REMOVE_PERIDOS = True
    queue_size = []
    msgs_rate = []

    # remove waiting periods
    if REMOVE_PERIDOS:
        prev_qs = 0
        for qs, ms in zip(raw_queue_size, raw_msgs_rate):
            if prev_qs <= qs:
                prev_qs = qs
                queue_size.append(qs)
                msgs_rate.append(ms)

        msgs_rate = np.array(msgs_rate) / 10  
    else:
        queue_size = raw_queue_size
        msgs_rate = np.array(raw_msgs_rate) / 10  

    x_data = np.array(msgs_rate).reshape(-1,1)
    y_data = queue_size

    poly_reg = PolynomialFeatures(degree=2)
    regressor = LinearRegression().fit(poly_reg.fit_transform(x_data), y_data)

    plot_polymonial(x_data, poly_reg, regressor, 'predict_queue_size_rcv_msgs_reg', y_data)

    x_pred = np.arange(0, 100000, 100).reshape(-1,1)
    plot_polymonial(x_pred, poly_reg, regressor, 'predict_queue_size_rcv_msgs_pred', y_points=[45600, 91200, 182400])
    

if __name__ == "__main__":
    main()