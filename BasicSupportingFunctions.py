import unittest

import os
import pickle
import csv

import numpy as np
import math
import scipy.stats

import matplotlib.pyplot as plt

#------------------------------------------------------------------------------

#Maths

def monteCarlo(data, function, iterations=100, sampleSize=50, value=5, proportion=0.05):
    '''
    Conducts a basic Monte Carlo test for input data and function type.
    Returns the count of successful trials,
    the proportion overall,
    and True/False for the meeting of conditions.
    '''

    dataPoints = len(data)
    resultCount = 0

    for i in range(iterations):
        thisSample = random.sample(data, sampleSize)
        result = function(thisSample)
        if result < value:
            resultCount +=1

    proved = False
    actualProportion = resultCount / iterations
    if actualProportion < proportion:
        proved = True

    return resultCount, actualProportion, proved

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

def lcm(x, y):
    '''
    Returns the lowest common multple of two values
    '''

    # Choose the greater number:
    if x > y:
        greater = x
    else:
        greater = y
    while(True):
        if((greater % x == 0) and (greater % y == 0)):
            lcm = greater
            break
        greater += 1

    return lcm

#------------------------------------------------------------------------------

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

def writeCSV(dataList,
             csvFilePath='/Users/',
             csvFileName='Test.csv',):
            # objectsOfInterest
    '''
    Writes data to a CSV file.
    '''

    with open(csvFilePath+csvFileName, 'w') as csvfile:
        csvOut = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for entry in dataList:
            csvOut.writerow([x for x in entry])

def getFiles(path='/Users/', extension=None):
    '''
    Retrieves files in the listed directory. So:
    >>> fileList = getFiles(directory)
    >>> for fileName in fileList:
    >>>     [Any of the other functions]
    '''

    fileList = []
    for file in os.listdir(path):
        if extension:
            if file.endswith(extension):
                fileList.append(file)
        else:
            fileList.append(file)
    return fileList

#------------------------------------------------------------------------------

#Patterns

def match(longList, shortListOrLists, print=True):
    for i in range(len(longlist) - len(shortlist)):
        hitLists = []
        currentPattern = longlist[i:i+len(shortlist)]
        if currentPattern in shortListOrLists:
            hitLists.append(currentPattern)
            if print:
                print(currentPattern)

    tupleList = map(tuple, hitLists)
    countList = Counter(tupleList)

    return countList

#------------------------------------------------------------------------------

#Patterns

class Test(unittest.TestCase):

    def testMatch(self):

        longList = [4, 6, 2, 4, 4, 4, 12, 4, 6, 2, 4,]
        shortLists = [[4, 6], [2, 4]]

        test = match(longList, shortLists)

        self.assertIsInstance(test, dict)
        self.assertEqual(test[shortLists[0]],2) # Check. shortLists[0] as key in test (dict), value 2

#------------------------------------------------------------------------------
