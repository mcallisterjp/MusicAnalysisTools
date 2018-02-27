import numpy as np
import matplotlib.pyplot as plt

def histogramOfIntervals(intervalList, xLabel=None, yLabel=None, title=None):
    '''
    Plotting shortcut for case of interval list.
    '''
    if xLabel is None:
        xLabel = 'Interval number'
    if yLabel is None:
        yLabel = 'Frequency of usage'
    if title is None:
        title = 'Usage of Intervals'

    #intervalListPlot = np.asarray(intervalList, np.float64)
    bins = max(intervalList) + 1 - min(intervalList)
    # bins = bins.astype(np.float64) - 0.5

    plt.figure(figsize=(15, 6))
    plt.hist(intervalList,
        bins=bins,
        width=0.95,
        range=(min(intervalList), max(intervalList) + 1),
        align='left',
        )
    plt.title(title, fontsize=20, family='serif')
    plt.xlabel(xLabel, fontsize=14, family='serif')
    plt.ylabel(yLabel, fontsize=14, family='serif')
    plt.xticks(np.arange(min(intervalList), max(intervalList) + 1, 1),)

    plt.show()
