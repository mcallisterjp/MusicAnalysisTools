import unittest

from music21 import common
from music21 import exceptions21
from music21 import pitch
from music21 import interval
from music21 import stream
from music21 import converter

from collections import Counter
from numpy import array
import csv
import os

#------------------------------------------------------------------------------

# music21 > Tabular

def M21toTSV(inputHarmonicAnalysis,
             outFilePath,
             outFileName='TSV_FILE.tsv',):
    '''
    Makes a TSV file from a music21 harmonic analysis stream.
    Output modelled on Neuwirth et al 2018's Annotated Beethoven Corpus (ABC),
    https://github.com/DCMLab/ABC/issues
    NB: not code used in that project; author unaffiliated with the ABC.
    '''

    # From ABC original list of column values.

    headers = ['chord', # 0
                 'altchord',
                 'measure',
                 'beat',
                 'totbeat',
                 'timesig', # 5
                 'op',
                 'no',
                 'mov',
                 'length',
                 'global_key', # 10
                 'local_key',
                 'pedal',
                 'numeral',
                 'form',
                 'figbass', # 15
                 'changes',
                 'relativeroot',
                 'phraseend']

    info = [headers]

    for item in inputHarmonicAnalysis.recurse():
        if 'RomanNumeral' in item.classes:
            thisEntry = [item.figure,
                        None,
                        item.measureNumber,
                        item.offset, # beat
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None, # Global key
                        item.key.name, # Local key
                        None, # 'pedal',
                        item.figure, # 'numeral',
                        None, # 'form',
                        None, # 'figbass', # 15
                        None, # 'changes',
                        None, # 'relativeroot',
                        None, # 'phraseend'
                        ]     # TODO: fill in remaining information columns
            info.append(thisEntry)

    with open(outFilePath+outFileName, 'a') as csvfile: # NB 'a' not 'w' to allow multiple works
        csvOut = csv.writer(csvfile, delimiter='\t',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for sublist in info:
            csvOut.writerow([x for x in sublist])

#------------------------------------------------------------------------------

# Tabular > music21

def TSVtoM21(file):
    '''
    Takes a TSV file and returns a music21 stream.
    '''

    harmonicArray = prepFile(file)

    prepdStream = prepStream(harmonicArray=harmonicArray)

    m21stream = makeM21stream(prepdStream=prepdStream,
                              harmonicArray=harmonicArray)

    return m21stream

def prepFile(file):
    '''
    Takes a TSV file and returns an array.
    '''

    f = open(file, 'r') # open the file for reading
    data = []
    for row_num, line in enumerate(f):
        values = line.strip().split('\t')
        if row_num != 0: # first line is the header
            data.append([v.strip('\"') for v in values]) # Remove the extra set of quotes
    harmonicArray = array(data)
    f.close()

    return harmonicArray

def prepStream(harmonicArray):
    '''
    Prepares a m21 stream for the harmonic analysis to go into.
    '''
    # TODO -- option for putting in corresponding score.

    s = stream.Score()
    p = stream.Part()

    p.insert(0, key.Key(harmonicArray[0][10])) # starting key sig
    p.insert(0, meter.TimeSignature(harmonicArray[0][5])) # starting time sig

    s.append(p)

    return s

def makeM21stream(prepdStream, harmonicArray):
    '''
    Takes chords from an array and inserts them into a music21 stream.
    '''

    measureList = [] # Keep a list of which are in

    for row in harmonicArray:

        # Get the info
        thisChord = row[0]
        thisMeasure = int(row[2])
        metricalPosition = float(row[3]) # ABC's 'beat'
        measureOffset = float(row[4]) # ABC's 'totbeat'; music21's 'offset'
        qLength = float(row[9]) # ABC's 'length'; music21's 'quarterLength
        global_key = str(row[10])
        local_key = str(row[11])
        numeral = str(row[13])

        # Check if measure is in; if not, insert.
        if thisMeasure not in measureList:
            m = stream.Measure(number=thisMeasure)
            m.offset = measureOffset
            p.insert(m) # insert new measure (not already there)
            measureList.append(thisMeasure)

        # Insert the rn to the measure (which is now definitely in)
        if str(row[13]): # If there actually is a rn given ...
            rn = roman.RomanNumeral(numeral, global_key) # e.g. roman.RomanNumeral('VI', 'F')
            # *** TODO *** global_key > local_key
            rn.quarterLength = qLength
            p.measure(thisMeasure).insert(metricalPosition - 1, rn) # rn at the relevant offset in bar (NB off by 1 error)

    return s

#------------------------------------------------------------------------------

class Test(unittest.TestCase):

    def testM21toTSV(self):

        testMonteverdiHarmony = corpus.parse('monteverdi/madrigal.3.1.rntxt')

        TSVMonteverdiHarmony = M21toTSV(testMonteverdiHarmony,
                                        outFilePath='/Users/Mark/Desktop/',
                                        outFileName='MonTSV.tsv')

        from io import IOBase

        openFile = open('/Users/Mark/Desktop/MonTSV.tsv', 'w')
        self.assertIsInstance(openFile, IOBase)


    # def testTSVtoM21(self):
    # Location of TSV file -- musc21 virtual corpus?
