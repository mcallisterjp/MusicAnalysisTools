from music21 import common, stream, clef, note, bar, interval

def countList(workOrPart, printUnusual=False):
    '''
    Returns a list of intervals and (optionally) prints cases that would be unusual in early music.
    '''
    intervalList = []
    partNotes = workOrPart.recurse().getElementsByClass(['Note', 'Rest', 'Clef'])
    for i in range(len(partNotes)-1):
        n1 = partNotes[i]
        if 'Rest' in n1.classes or 'Clef' in n1.classes:
            continue
        n2 = partNotes[i + 1]
        if 'Rest' in n2.classes or 'Clef' in n2.classes:
            continue
        intervalObj = interval.Interval(n1, n2)
        semis = intervalObj.semitones
        if printUnusual and (abs(semis) > 12 or abs(semis) == 6 or abs(semis) == 10 or abs(semis) == 11):
             print('******')
             print(semis)
             print(n1)
             print(n1.measureNumber)
             print(n1.getContextByClass('Part'))
             print(list(n1.contextSites())[-1].site.filePath)
        intervalList.append(intervalObj)
    return intervalList

def getSemitoneRange(part, limit=25):
    '''
    Get the overall range of an input part expressed in semitones within a set range.
    '''
    ambitus = part.analyze('ambitus')
    if not ambitus:
        semitones = 0
    else:
        semitones = ambitus.semitones

    if semitones > limit:
        semitones = limit
    return semitones
