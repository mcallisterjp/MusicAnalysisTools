import numpy as np
import matplotlib.pyplot as plt

#------------------------------------------------------------------------------

#Linear
def linearFunc(x, a, b):
    return a*x+b

#Exponential
def expoFunc(x, a, b, c):
    return a*np.exp(-b*x)+c

#Polynomials:
def polyFunc(x, a, b, c, d):
    return a*x**3 + b*x**2 + c*x + d

#ArcTan
def arcTanFunc(x, a, b, c, d):
    return a*np.arctan(b*x + c) + d

#------------------------------------------------------------------------------

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

#------------------------------------------------------------------------------

def dateRages(corps):
    '''
    Takes a list of lists of the type [name, date start, date end] and
    returns a histograme for visualisation.
    '''

    size = len(corps) # No. of rows

    corpora = sorted(corps, key = lambda x: int(x[1]))

    plt.figure()#figsize=(5, 2))

    x_values = []
    y_values = []
    y_axis = np.arange(0.5, size, 1)

    # hlines and ylables
    for i in range(size):
        y_values.append(corpora[i][0])
        l = plt.hlines(y=0.5 + i, xmin=corpora[i][1], xmax=corpora[i][2], linewidth=8, color='#d62728')

    # plt.plot()
    plt.yticks(y_axis, y_values)

    plt.axis([1825, 2025, 0, size]) # TODO start date as variable: corpora[0][0]?
    plt.title('Date Ranges', fontsize=20)
    plt.xlabel('Date', fontsize=14)
    # plt.ylabel('Corpora', fontsize=14)

    plt.show()

#------------------------------------------------------------------------------
