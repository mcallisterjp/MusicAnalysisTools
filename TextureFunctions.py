import unittest

import pickle
import numpy as np
import matplotlib.pyplot as plt

from collections import Counter
from fractions import Fraction

from music21 import common
from music21 import exceptions21
from music21 import pitch
from music21 import interval
from music21 import stream

#------------------------------------------------------------------------------

def getOffsets(score):
    '''
    Retrieves position of note beginnings across a score.
    Expressed in terms of 'offset' from the start.
    ''' #To do: include expression in terms of bars / meter

    allNotes = score.stripTies().flat.notes
    allOffsets = [x.offset for x in allNotes]
    return allOffsets

def allTimePointOffsetCounts(allOffsets, minValue=8):
    '''
    Lists number of offsets for every timepoint (integrating timepoints with no offsets)
    '''

    filteredOffsets = [x for x in allOffsets if (Fraction(x).denominator*minValue == int)]
    # Fraction(x).denominator < minValue/4]
    # Deals with binary divisions, but not triplets.
    # TO DO triplets, possibly with lcmValue = BasicSupportingFunctions.lcm(x, y)

    denoms = [Fraction(x).denominator for x in allOffsets]
    maxDenom = max(denoms)

    allOffsetsNoFractions = [x*maxDenom for x in allOffsets]

    counts = Counter(allOffsetsNoFractions) # keys = 'positions'; values = counts
    firstOffset = int(min(allOffsetsNoFractions))
    lastOffset = int(max(allOffsetsNoFractions))
    # numberOfOffsets = len(allOffsets)
    spanRange = lastOffset - firstOffset

    allTimePointOffsetCounts = []
    for x in range(spanRange):
        if x in counts.keys(): # keys = positions;
            allTimePointOffsetCounts.append(counts[x]) # values = counts
        else:
            allTimePointOffsetCounts.append(0) #No offsets at this position

    return allTimePointOffsetCounts
    # To do: consider returning a new dict at this point; working with values thereafter

def allTimePointsWeighted(allTimePointOffsetCounts):
    '''
    Weights each offset count / timepoint by proximity to maximum/minimum no. of voices (0-n).
    '''

    allTimePointsWeighted = []
    maxInSection = max(allTimePointOffsetCounts)
    for x in allTimePointOffsetCounts:
        firstValue = x/maxInSection
        if firstValue > 0.5:
            weightedValue = round(1 - firstValue, 2)
        elif firstValue <= 0.5:
            weightedValue = round(firstValue, 2)
        allTimePointsWeighted.append(weightedValue)
    return allTimePointsWeighted

def getWindowedAverage(listOfWeightedTimePoints, windowSize=16):
    '''
    Takes an average for a certain number (input) of weighted timepoints.
    '''

    numberOfTimepoints = len(listOfWeightedTimePoints)
    averagePerWindow = []
    for i in range(numberOfTimepoints - windowSize):
        valuesList = []
        for j in range(windowSize):
            temporaryValue = listOfWeightedTimePoints[i+j]
            valuesList.append(temporaryValue)
        ourAverage = sum([x for x in valuesList]) / windowSize
        averagePerWindow.append(round(ourAverage, 2))
    return averagePerWindow

def doOneScore(score, windowSize=8):
    '''
    Runs the functions up to and including windowed average for an input score or passage
    '''
    try:
        parsedScore = score.parse() # Non-corpus
    except:
        parsedScore = score # Corpus
    offsets = getOffsets(parsedScore)
    timePoints = allTimePointOffsetCounts(offsets)
    weightedTimePoints = allTimePointsWeighted(timePoints)
    windowedAverages = getWindowedAverage(weightedTimePoints, windowSize=windowSize)
    return windowedAverages

def doCorpus(LocalCorpusName, noOfWorks=5): #LocalCorpus
    '''
    Runs the functions up to and including windowed average for all works in a corpus.
    '''

    for score in corpus.corpora.LocalCorpus(str(LocalCorpusName)).all()[:noOfWorks]: #don't forget 'all' for local corpus
        #print (score.metadata.parentTitle)
        eachOneOfThem = doOneScore(score)

        info = []
        comp = score.metadata.composer
        parent = score.metadata.parentTitle
        title = score.metadata.title
        uniqueName = [comp[0:4], '-', #Start of composer name
                      parent[5:10], '-', #Start of title, ommitting 'Missa'
                      title] #Whole title for case of Agnus I vs II
        fileName = str(''.join(uniqueName))
        print(fileName)
        country=countryDict[comp]

        testList = [x for x in range(10)]
        info = [comp, parent, title, country, eachOneOfThem]
        storePickle(info, fileName)

#         storePickle(eachOneOfThem, score.metadata.parentTitle)

def getRankedLocalMax(info, #Input data
                      n=10, #How many to return
                      threshold=0.2, #Minimum peak value
                      windowSize=16): #Minimum range of 'local'
    '''
    Returns
    ((x coordinate timepoint, y coordinate value),
        Number of timepoints for which this is a local max)
    '''

    shortList = []
    for lineIndex in range(len(info)-windowSize):
        currentValues = []
        for ws in range(windowSize):
            x = lineIndex+ws # timepoint
            y = info[lineIndex+ws] #value
            currentTuple = (x,y)
            currentValues.append(currentTuple)
        localMax = max(currentValues,key=lambda item:item[1])
        if localMax[1] > threshold:
            shortList.append(localMax)

    return [x for x in Counter(shortList).most_common(n) if x[1] > 1]

def getRankedLocalMin(info, #Input data
                      n=10, #How many to return
                      threshold=0.2, #Maximum peak value
                      windowSize=16): #Minimum range of 'local'
    '''
    Returns
    ((x coordinate timepoint, y coordinate value),
        Number of timepoints for which this is a local min)
    '''

    shortList = []
    for lineIndex in range(len(info)-windowSize):
        currentValues = []
        for ws in range(windowSize):
            x = lineIndex+ws # timepoint
            y = info[lineIndex+ws] #value
            currentTuple = (x,y)
            currentValues.append(currentTuple)
        localMin = min(currentValues,key=lambda item:item[1])
        if localMin[1] < threshold:
            shortList.append(localMin)

    return [x for x in Counter(shortList).most_common(n) if x[1] > 1]

# Imported from elsewhere

def storePickle(obj, filename):
    path = '/Users/Mark/Desktop/'#Pickles/'
    filename = path + filename + '.p'
    with open(filename, 'wb') as fileout:
        pickle.dump(obj, fileout)
    return filename

def loadPickle(filename):
    path = '/Users/Mark/Desktop/'#Pickles/'
    filename = path + filename + '.p'
    with open(filename, 'rb') as filein:
        obj = pickle.load(filein)
    return obj

def histogramOfAverages(dataList, xLabel=None, yLabel=None, title=None):
    if xLabel is None:
        xLabel = 'Average hr values per 10 onsets'
    if yLabel is None:
        yLabel = 'Frequency of usage'
    if title is None:
        title = 'Homorhythmicity'

    counterCase = Counter(dataList)
    labels, values = zip(*counterCase.items())
    indexes = np.arange(len(labels))
    width = 0.95

    plt.bar(indexes, values, width)
    plt.xticks(indexes, labels)
    plt.title(title, fontsize=20, family='serif')
    plt.xlabel(xLabel, fontsize=14, family='serif')
    plt.ylabel(yLabel, fontsize=14, family='serif')
#     plt.xticks(np.arange(min(dataList), max(dataList) + stepSize, stepSize),)

    return plt

#------------------------------------------------------------------------------

class Test(unittest.TestCase):

    def testGetOffsets(score):

        testscore = corpus.parse('bach/bwv1.6')
        testOffsets = getOffsets(testscore)

        self.assertIsInstance(testOffsets, list)
        self.assertIsInstance(testOffsets[0], int)

    def testTimePointOffsetCounts(self):

        testscore = corpus.parse('bach/bwv1.6')
        testOffsets = getOffsets(testscore)
        testAllOffsets = allTimePointOffsetCounts(testOffsets)

        self.assertIsInstance(testAllOffsets, list)
        self.assertIsInstance(testAllOffsets[0], int)

    def testAllTimePointsWeighted(self):

        testscore = corpus.parse('bach/bwv1.6')
        testOffsets = getOffsets(testscore)
        testAllOffsets = allTimePointOffsetCounts(testOffsets)
        testAllOffsetsWeighted = allTimePointsWeighted(testAllOffsets)

        self.assertIsInstance(testAllOffsetsWeighted, list)
        self.assertIsInstance(testAllOffsets[0], float)

    def testWindowedAverage(self):

        testscore = corpus.parse('bach/bwv1.6')
        testOffsets = getOffsets(testscore)
        testAllOffsets = allTimePointOffsetCounts(testOffsets)
        testAllOffsetsWeighted = allTimePointsWeighted(testAllOffsets)
        avs = getWindowedAverage(testAllOffsetsWeighted)

        self.assertIsInstance(avs, list)
        self.assertIsInstance(avs[0], float)

    # def testDoOneScore(self):

    def testGetRankedLocalMax(self):

        testInfo = [0.04, 0.04, 0.04, 0.05, 0.05, 0.05, 0.06, 0.08, 0.09, 0.09, 0.09, 0.1, 0.1,
        0.1, 0.1, 0.09, 0.09, 0.09, 0.09, 0.08, 0.08, 0.08, 0.06, 0.05, 0.05, 0.05, 0.05, 0.05,
        0.06, 0.06, 0.06, 0.07, 0.07, 0.07, 0.07, 0.1, 0.1, 0.1, 0.1,]

        testResult = TextureFunctions.getRankedLocalMax(testInfo, n=2, threshold=0.09, windowSize=4)

        self.assertEqual(len(testResult), n)
        self.assertIsInstance(testResult[0][0][0], int) # Position
        self.assertIsInstance(testResult[0][0][1], float) # Value (average)
        self.assertIsInstance(testResult[0][1], int) # Count

    def testGetRankedLocalMin(self):

        testInfo = [0.04, 0.04, 0.04, 0.05, 0.05, 0.05, 0.06, 0.08, 0.09, 0.09, 0.09, 0.1, 0.1,
        0.1, 0.1, 0.09, 0.09, 0.09, 0.09, 0.08, 0.08, 0.08, 0.06, 0.05, 0.05, 0.05, 0.05, 0.05,
        0.06, 0.06, 0.06, 0.07, 0.07, 0.07, 0.07, 0.1, 0.1, 0.1, 0.1,]

        testResult = TextureFunctions.getRankedLocalMin(testInfo, n=2, threshold=0.09, windowSize=4)

        self.assertEqual(len(testResult), n)
        self.assertIsInstance(testResult[0][0][0], int) # Position
        self.assertIsInstance(testResult[0][0][1], float) # Value (average)
        self.assertIsInstance(testResult[0][1], int) # Count

#-------------------------------------------------------------------------------
