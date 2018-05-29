import unittest

import os
import pickle
import numpy as np
import matplotlib.pyplot as plt

from fractions import Fraction
from collections import Counter

from music21 import common
from music21 import exceptions21
from music21 import pitch
from music21 import interval
from music21 import stream
from music21 import converter

#------------------------------------------------------------------------------

countryDict = {'Agricola, Alexander': 'Franco-Flemish',
    'Aston, Hugh': 'British',
    'Bauldeweyn, Noel': 'Franco-Flemish',
    'Brumel, Antoine': 'French',
    'Carvor, Robert': 'British',
    'Colebault, Jacques': 'French',
    'Compere, Loyset': 'French',
    'Compère, Loyset': 'French',
    'Comp&egrave;re, Loyset': 'French',
    'Divitis, Antonius': 'Franco-Flemish',
    'Fayrfax, Robert': 'British',
    'Fevin, Antoine de': 'French',
    'Févin, Antoine de': 'French',
    'F&eacute;vin, Antoine de': 'French',
    'Fevin, Robert de': 'French',
    'Févin, Robert de': 'French',
    'F&eacute;vin, Robert de': 'French',
    'Ghiselin, Johannes': 'Franco-Flemish',
    'Gombert, Nicolas': 'Franco-Flemish',
    'Isaac, Heinrich': 'Franco-Flemish',
    'Janequin, Clement': 'French',
    'Rue, Pierre de la': 'Franco-Flemish',
    'Morales, Cristobal de': 'Spanish',
    'Moulu, Pierre': 'Franco-Flemish',
    'Mouton, Jean': 'French',
    'Obrecht, Jacob': 'Franco-Flemish',
    'Orto, Marbrianus de': 'Franco-Flemish',
    'Peñalosa, Francisco de': 'Spanish',
    'Penalosa, Francisco de': 'Spanish',
    'Pipelare, Matthaeus': 'Franco-Flemish',
    'Prez, Josquin des': 'Franco-Flemish',
    'Taverner, John': 'British',
    }

#------------------------------------------------------------------------------

# Processing data for storing basic version that is adapatable as required
# One score, up to weighted values (so everything reversible)

def getOffsets(score):
    '''
    Retrieves position of note beginnings across a score.
    Expressed in terms of 'offset' from the start.
    '''
    #NB: score necessarily already parsed
    #TODO: include expression in terms of bars / meter

    allNotes = score.stripTies().flat.notes
    allOffsets = [x.offset for x in allNotes]
    return allOffsets

def allTimePointOffsetCounts(allOffsets, minRhyDenom=8):
    '''
    Lists number of offsets for every timepoint (integrating timepoints with no offsets).
    Specify minimum rhythmic value by 'denominator' i.e. 1/4 note = 4; 1/8 note = 8.
    '''
    # E.g. use 4 for scores in original values (JRP), but 8 for modern editions.

    filteredOffsets = [x for x in allOffsets if Fraction(x).denominator <= minRhyDenom/4]
    # TODO. Not currently dealing with triplets. Fix with lcm(x, y)?

    # Multiply up to have only integer timepoints (no fractions).
    # This is both for processing the lists and to remove editorial differences.
    denoms = [Fraction(x).denominator for x in filteredOffsets]
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
            allTimePointOffsetCounts.append(0) # No offsets at this position

    return allTimePointOffsetCounts
    # To do: consider returning a new dict at this point; working with values thereafter

def allTimePointsWeighted(allTimePointOffsetCounts):
    '''
    Weights each offset count / timepoint by proximity to maximum/minimum no. of voices (0-n).
    '''

    allTimePointsWeighted = []
    maxInSection = max(allTimePointOffsetCounts)
    for x in allTimePointOffsetCounts:

        ## This is the homorhythmicity metric, wih range 0-1.
        ## Low value = low homorhythmicity; high value = highly homorhythmic.
        firstValue = x/maxInSection
        if firstValue > 0.5:
            weightedValue = 2*round(firstValue - 0.5, 2)
        elif firstValue <= 0.5:
            weightedValue = 2*round(0.5 - firstValue, 2)
        allTimePointsWeighted.append(weightedValue)
    return allTimePointsWeighted

def doOneScore(score):
    '''
    Runs the functions up to and including windowed average for an input score or passageself.
    Can be called on a parsed score or path to the file for conversion.
    '''

    try:
        parsedScore = converter.parse(score) # Simplest way; covers both corpus and non-corpus
    except:
        parsedScore = score # if alredy parsed

    offsets = getOffsets(parsedScore)
    timePoints = allTimePointOffsetCounts(offsets)
    weightedTimePoints = allTimePointsWeighted(timePoints)
    # windowedAverages = getWindowedAverage(weightedTimePoints, windowSize=windowSize)
    return weightedTimePoints #windowedAverages removed to after pickling

#------------------------------------------------------------------------------

# Corpus processing, saving, retrieving

def getFiles(filePath='/Users/', extension=None):
    '''
    Retrieves files in the listed directory. So:
    >>> fileList = getFiles(directory)
    >>> for fileName in fileList:
    >>>     [Any of the other functions]
    '''

    fileList = []
    legitExtensions = ['.mid', '.xml', '.mxl', '.krn']

    if extension is not None: # If extension input when calling function
        for file in os.listdir(filePath):
            if file.endswith(extension): # That same input
                fileList.append(file)
    elif extension is None: # If no extension input when calling function
            for file in os.listdir(filePath):
                for ext in legitExtensions:
                    if file.endswith(ext):
                        fileList.append(file)
    return fileList

def doCorpus(filePath, noOfWorks=5): #LocalCorpus
    '''
    Runs the functions up to and including windowed average for all works in a corpus.
    '''

    fileList = getFiles(filePath)
    for fileName in fileList:
    # Alternatively, for score in corpus.corpora.LocalCorpus(str(LocalCorpusName)).all()[:noOfWorks]:
    # NB 'all' when using local corpus

        fullPath = filePath+fileName # Path and name

        data = doOneScore(fullPath)
        info = [data] # So info[0] is all the data

        medataList = [] # Later to be added as info[1]
        medataList.append(fileName) # info[1][0] = metadata[0] = fileName
        medataList.append(fullPath) # info[1][1] = metadata[1] = fullPath
        # ... adding more if possible in try except

        parsedScore = converter.parse(fullPath)
        # TODO efficiency issue: currently having to parse each score twice: here and in doOneScore.

        try: # try except for case of no metadata

            comp = parsedScore.metadata.composer
            medataList.append(comp)
            parent = parsedScore.metadata.parentTitle
            medataList.append(parent)
            title = parsedScore.metadata.title
            medataList.append(title)
            country=countryDict[comp]
            medataList.append(country)

            combined = [comp, '-', parent, '-', title]
            # uniqueName = [comp[0:4], '-', #Start of composer name
            #               parent[5:10], '-', #Start of title, ommitting 'Missa'
            #               title] #Whole title for case of Agnus I vs II
            uniqueName = str(''.join(combined))
            medataList.append(uniqueName)

        except: # forget metadata and work from the directory and file names

            pass

        info.append(medataList) # ([data],[metadata])

        storePickle(info, fileName)

def storePickle(obj, filename, path='/Users/Mark/Desktop/Pickles/'):
    filename = path + filename + '.p'
    with open(filename, 'wb') as fileout:
        pickle.dump(obj, fileout)
    return filename

def loadPickle(filename, path='/Users/Mark/Desktop/Pickles/'):
    filename = path + filename + '.p'
    with open(filename, 'rb') as filein:
        obj = pickle.load(filein)
    return obj

#------------------------------------------------------------------------------

# Working with the data

def getOverallHValue(listOfWeightedTimePoints):
    '''
    Gets the the overall homorhythmicity values for the movement.
    '''
    average = sum([x for x in listOfWeightedTimePoints]) / len(listOfWeightedTimePoints)
    outAverage = (round(average, 2))
    return outAverage

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

def getRankedLocalMax(info, #Input data
                      n=10, #How many to return
                      threshold=0.25, #Minimum peak value. Depends on input minimum rhythmic value.
                      windowSize=16): #Minimum range of 'local'
    '''
    Returns
    ((x coordinate timepoint, y coordinate value for homorhythmicity),
        Number of timepoints for which this is a local max)
    '''
    ## Remember: homorhythmicity range 0-1; low value = low homorhythmicity.

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
                      RankBy='timePoints',
                      threshold=0.75, #Maximum peak value
                      windowSize=16): #Minimum range of 'local'
    '''
    Returns
    ((x coordinate timepoint, y coordinate value),
        Number of timepoints for which this is a local min)
    '''
    #TODO Rank-by options. RankByDict= {'x':***,'y':***, 'timePoints':***}

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

#------------------------------------------------------------------------------

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

    plt.figure(figsize=(15, 6))
    plt.bar(indexes, values, width)
    plt.xticks(indexes, labels)
    plt.title(title, fontsize=20, family='serif')
    plt.xlabel(xLabel, fontsize=14, family='serif')
    plt.ylabel(yLabel, fontsize=14, family='serif')
#     plt.xticks(np.arange(min(dataList), max(dataList) + stepSize, stepSize),)

    return plt

def plotWindowedAverages(dataList, xLabel=None, yLabel=None, title=None):
    plt.figure(figsize=(15, 6))
    plt.plot(dataList)
    plt.xlabel('Offset (eigth notes)', fontsize=14, family='serif')
    plt.ylabel('Windowed average', fontsize=14, family='serif')
    # plt.xticks(np.arange(min(intervalList), max(intervalList) + 1, 1),)
    plt.plot
    plt.show()
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
