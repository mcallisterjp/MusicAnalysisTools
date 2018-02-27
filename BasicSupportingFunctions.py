import os
import pickle
import math
import scipy.stats

#Maths

def getPValueBinomial(first, second, nullHyp=0.5):
    '''
    Returns the PValue for a distribution of two sets of T, F, or two-bin data.
    '''
    if first < second:
        first, second = second, first
    total = first + second
    proportion = first / total
    standardError = math.sqrt((nullHyp * (1 - nullHyp)) / total)
    zValue = (proportion - nullHyp) / standardError
    return scipy.stats.norm.sf(abs(zValue))

def getPercentile(l, amount=0.9):
    l = sorted(l)
    lLen = len(l)
    bottomHalfAmount = (1 - amount) / 2
    topHalfAmount = 1 - bottomHalfAmount

    bottomFivePercent = round(lLen * bottomHalfAmount)
    topFivePercent = round(lLen * topHalfAmount)
    return l[bottomFivePercent:topFivePercent + 1]

#Files

def storePickle(obj, path, filename):
    filename = path + filename + '.p'
    with open(filename, 'wb') as fileout:
        pickle.dump(obj, fileout)
    return filename

def loadPickle(path, filename):
    filename = path + filename + '.p'
    with open(filename, 'rb') as filein:
        obj = pickle.load(filein)
    return obj
