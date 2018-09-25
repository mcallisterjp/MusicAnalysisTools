import unittest

from music21 import common
from music21 import converter
from music21 import exceptions21
from music21 import interval
from music21 import key
from music21 import meter
from music21 import pitch
from music21 import roman
from music21 import stream

from collections import Counter
from numpy import array
import csv
import os

#------------------------------------------------------------------------------

# music21 > Tabular (and so also for covering RN > m21 > tabular)

class M21toTSV:

    def process(inputHarmonicAnalysis,
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
                                    None, #'altchord',
                                    item.measureNumber,
                                    item.offset, # beat
                                    None, # 'totbeat',
                                    None, # 'timesig', # 5
                                    None,# 'op',
                                    None,# 'no',
                                    None,# 'mov',
                                    item.quarterLength, # 'length',
                                    None, # 'global_key', # 10
                                    item.key.name, # local_key
                                    None, # 'pedal',
                                    item.figure, # 'numeral',
                                    None, # 'form',
                                    None, # 'figbass', # 15
                                    None, # 'changes',
                                    None, # 'relativeroot',
                                    None, # 'phraseend'
                                    ]     # TODO: Review these and fill remaining columns
                        info.append(thisEntry)

                with open(outFilePath+outFileName, 'a') as csvfile: # 'a' to allow multiple works
                    csvOut = csv.writer(csvfile, delimiter='\t',
                                        quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    for sublist in info:
                        csvOut.writerow([x for x in sublist])

#------------------------------------------------------------------------------

# Tabular > music21 (thus covers also tabular > m21 > RN)

class TSVtoM21:

    def process(file):
        '''
        Takes a TSV file and returns a music21 stream.
        '''

        harmonicArray = TSVtoM21.prepFile(file)
        prepdStream = TSVtoM21.prepStream(harmonicArray=harmonicArray)
        m21stream = TSVtoM21.makeM21stream(prepdStream=prepdStream,
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

        s = prepdStream
        p = s.parts[0]

        timesig = str(harmonicArray[0][5])
        ts = meter.TimeSignature(timesig)
        numerator = ts.numerator

        measures = list([int(row[2]) for row in harmonicArray])
        firstMeasure = measures[0]
        difference = 0 # initialise. 0 where no anacrusis (piece starts at the beginning of m1).
        if firstMeasure == 0:
            measure1index = measures.index(1)
            difference += (harmonicArray[measure1index][4] - harmonicArray[0][4]) # totbeat

        # Insert all measures into stream
        for eachMeasureNo in range(measures[0], measures[-1]): # Might start with 0 or 1
            m = stream.Measure(number=eachMeasureNo)
            m.offset = (eachMeasureNo-1)*numerator + difference
            # TODO checks for timesig changes
            # TODO generaise for all timesig types (compound)
            p.insert(m)

        for row in harmonicArray:

            # Get info.
            firstColumn = str(row[0]) # ABC's chordchord
            # altchord =
            thisMeasure = int(row[2]) # ABC's measure
            beat =  float(row[3]) # NB beat = offset + 1, so add extra variable for ...
            offsetInMeasure = beat - 1
            totbeat = float(row[4]) # music21's 'offset' but again, + 1 (starts on 1)
            # timesig = # Needed to check changes TODO
            # op = # Dealt with in metadata, must not change. TODO
            # no = # Dealt with in metadata, must not change. TODO
            # mov = # Dealt with in metadata, must not change. TODO
            length = float(row[9]) # music21's 'quarterLength'
            global_key = str(row[10])
            local_key = TSVtoM21.getLocalKey(str(row[11]), global_key) #***
            # pedal =
            numeral = str(row[13])
            form = str(row[14])
            figbass = str(row[15])
            changes = str(row[16])
            relativeRoot = str(row[17])
            # phraseend

            # Insert the rn to the relevant measure
            if numeral: # If there is a rn. Covers empty strings. Ossia if thisChord is not '@none'.
                combined = ''.join([numeral, form, figbass, changes]) # Empty string if not used.
                if relativeRoot: # special case requiring '/'.
                    combined = ''.join([combined, '/', relativeRoot])
                rn = roman.RomanNumeral(combined, local_key) # e.g. ('VI', 'F')
                rn.quarterLength = length
                try:
                    p.measure(thisMeasure).insert(offsetInMeasure, rn)
                except: # TODO fix this bug
                    raise ValueError('No such measure number %s in this piece' %thisMeasure)

        return s

    def getLocalKey(local_key, global_key):
        '''
        Re-casts comparative local key (e.g. V of G major) in its own terms (D major).
        '''

        asRoman = roman.RomanNumeral(local_key, global_key)
        rt = asRoman.root().name
        if asRoman.isMajorTriad():
            newKey = rt.upper()
        elif asRoman.isMinorTriad():
            newKey = rt.lower()

        return newKey

    def characterSwaps(txtString):
        '''
        Swaps out ABC’s text representations of harmonic ideas for music21’s version.
        '''
        # Placeholder function in case if the need to expand.
        # NB non issues:
        # - music21 work with 64 or 6/4,
        # - not using the first column, so no need to remove the '\\' or '.'

        characterDict = {'%': '/o',} # '+': '',

        for key in characterDict:
            txtString = txtString.replace(key, characterDict[key])

        return txtString

class PartsFromCombinedString:
    '''
    Functions for breaking up the combined, column 0 'chord' string into its component parts.
    Not usually necessary as they're given in later columns.
    '''

    def getRelativeRoot(rn, local_key):
        '''
        Separates comparative roman numeral for tonicisiations like 'V/IV' into the component parts of
        - a roman numeral (V) and
        - a (very) local key (IV)
        and expresses that very local key in relation to the local key in column 11.
        '''

        if '/' not in rn:
            raise ValueError("Only call this function to seperate a comparative roman numeral like 'V/V'")
        else:
            position = rn.index('/')
            very_local_as_roman = rn[position+1:]
            very_local_as_key = getLocalKey(very_local_as_roman, local_key)

        return very_local_as_key

    def extricateRoman(col0String):
        '''
        Retrieves the roman numeral (with inversions etc) from the column 0 value,
        cutting the key information which is more easily retrievable from local_key.
        '''

        if '.' not in col0String:
            raise ValueError("Only call this function on a string with '.' to indicate key changes.")
        else:
            lastDotIndex = finalOccurence(col0String, '.')
            extricatedRoman = col0String[lastDotIndex+1:]

        return extricatedRoman

    def finalOccurence(haystack, needle):
        '''
        Returns the final occurence of one string in another.
        '''

        flippedHaystack = haystack[::-1]
        negIndex = flippedHaystack.find(needle)
        realIndex = len(haystack) - (negIndex + 1)

        return realIndex

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
    # Location of TSV file -- music21 virtual corpus?

    def testOfCharacter(self):

        startText = 'before%after'
        newText = [characterSwaps(x) for x in startText]
        # '%' > '/o'

        self.assertIsInstance(startText, str)
        self.assertIsInstance(newText, str)
        self.assertEqual(len(startText), 12)
        self.assertEqual(len(newText), 13)
        self.assertEqual(startText[6], '%')
        self.assertEqual(newText[6], '/')

    # def testGetRelativeRoot(self):
    #
    #     PartsFromCombinedString.getRelativeRoot

    def testExtricateRoman(self):

        col0String = 'ii.#viio2'
        extricatedRoman = PartsFromCombinedString.extricateRoman(col0String)

        self.assertIsInstance(extricatedRoman, str)
        self.assertEqual(extricatedRoman[0], '#')

    def testFinalOccurence(self):

        haystack = 'je.nrtjer34jweqw39iodjsd'
        index = PartsFromCombinedString.finalOccurence(haystack, '.')

        self.assertIsInstance(index, int)
        self.assertEqual(index, 2)
