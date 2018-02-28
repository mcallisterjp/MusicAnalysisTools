from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
import csv
import os

def getFiles(filePath='/Users/'):
    fileList = []
    for file in os.listdir(filePath):
        if file.endswith(".csv"):
            fileList.append(file)
    return fileList

# Specific Triad Types:
def getSetsOfType(directoryOrFile='/Users/',
                  chordType='[0, 4, 8]',
                  multipleFiles=True,):
    '''
    Get all cases of a specific chord type (expressed as PC Set).
    Returns a dict with each transposition of the chord,
    and the number of times it occurs.
    Can be applied to a single file (e.g one composer on YCAC)
    or to several (e.g. all of YCAC)
    '''
    chordList = []
    if multipleFiles:
        fileList = getFiles(directoryOrFile)
        for name in fileList:
            print(file)
            f = open(directoryOrFile+name)
            next(f) # Ignore header line
            for row in csv.reader(f):
                if row[2] == chordType: # Normal form type
                    chordList.append(row[3]) #Specific transposition
    else:
        f = open(directoryOrFile)
        next(f)
        for row in csv.reader(f):
            if row[2] == chordType:
                chordList.append(row[3])

    chordArray = np.array(Counter(chordList)) # TODO: Maybe add most common filter?
    return chordArray

def getAllNormals(filePath):
    '''
    Retrieves all normal orders in a file and compares relative usage
    '''
    primeList = []
    f = open(filePath)
    next(f) # to skip header line. Ossia: f.readline(), but not f.next() which is for python 2

    for row in csv.reader(f):
            primeList.append(row[2])

    return primeList

def compareAllNormals(primeList,
                      triadsOfInterest=('major','minor'),
                      Counts=True,
                      Proportions=True,):
    '''
    Compares relative usage of triad types in a file
    expressed in terms of counts, proportion of the whole, or both.
    Options: 'major', 'minor', 'diminished', 'augmented', 'triads' (all of the above)
    '''

    overallInfo = []
    total = len(primeList)

    hitList = []
    if 'major' in triadsOfInterest:
        hitList.append('[0, 4, 7]')
    if 'minor' in triadsOfInterest:
        hitList.append('[0, 3, 7]')
    if 'diminished' in triadsOfInterest:
        hitList.append('[0, 3, 6]')
    if 'augmented' in triadsOfInterest:
        hitList.append('[0, 4, 8]')
    if 'triads' in triadsOfInterest:
        hitList.append('[0, 4, 7]', '[0, 3, 7]', '[0, 3, 6]', '[0, 4, 8]')
        #To do: generalise wider than triads?
        #'Diminished Seventh', '[0, 3, 6, 9]'
    if hitList == []:
        print ("Please chose one or more triad types: 'major', 'minor', 'diminished', 'augmented', 'triads' (all of the above)")

    if Counts:
        currentTuple = ('Overall', total)
        overallInfo.append(currentTuple)
    for triad in hitList:
        currentCount = primeList.count(triad)
        if Counts:
            currentName = triad+' Count'
            currentTuple = (currentName, currentCount)
            overallInfo.append(currentTuple)
        if Proportions:
            currentName = triad+' Proportion'
            currentTuple = (currentName, currentCount/total)
            overallInfo.append(currentTuple)
    return overallInfo

def offsetPositions(file):
    '''
    Gets usage counts for augmented chord slices
    and the same weighted for 'length' (though NB issues with YCAC)
    '''

    offs = []
    allNorms = []
    augs = []

    f = open(file)
    next(f)
    for row in csv.reader(f):
        offs.append(float(row[0])) # all offsets
        allNorms.append(row[2]) # all normal forms

    #Get piece lengths by the sudden step back down to (or near) 0.
    totals = []
    for index, i in enumerate(offs):
        if i < offs[index - 1]:
            totals.append(offs[index - 1])

    #Get position info for all augmenteds
    positions = []
    for i in [i for i,x in enumerate(allNorms) if x == '[0, 4, 8]']:
        positions.append(i)

    #Retrieve relevant offset values and subtract using position info all augmenteds
    for p in positions:
    ##    print(offs[p+1]-offs[p])
        if offs[p+1]-offs[p] > 0: #Work around in case of last chord in piece (e.g. maj / min)
            augs.append(offs[p+1]-offs[p])

    returnInfo = {'No. of Works': len(totals),
                  'No. of Augmented Slices': len(augs),
                  'Total Slices': len(offs),
                  'Count Proportion': len(augs)/len(offs),
                  'Total augs weighted for length': sum(augs),
                  'Total overall weighted for length': sum(totals),
                  'Weighted Proportion': sum(augs)/sum(totals),}

    return returnInfo
