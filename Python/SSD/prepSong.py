#!/usr/bin/env python

import midifile, sys
import urllib2

filename = ''
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename=raw_input('Please enter filename of .mid or .kar file:')

m=midifile.midifile()
m.load_file(filename)

if not m.karfile:
    print "This is not a karaoke file."
    sys.exit(0)

#get syllables and times
syls = [(s,t) for (s,t) in zip(m.karsyl, m.kartimes) if s!='/' and s!='' and s!='\\']

##TODO: create lyrics with words
# parse _ and other symbols

# figure out which track has notes for the lyrics
minDiff = -1
noteTrack = 0
candidatesForRemoval = []
for i in range(m.ntracks):
    thisTrack = [v for v in m.notes if v[4]==i]
    if (len(thisTrack) > 0):
        candidatesForRemoval.append(i)

        # deal with percussion tracks with lots of "notes"
        if len(thisTrack) < 2*len(syls):
            currentSum = 0
            numberOfSums = len(syls)
            for (s,t) in syls:
                minDistance = -1
                for v in thisTrack:
                    if (minDistance == -1) or abs(t-v[5])<minDistance:
                        minDistance = abs(t-v[5])
                currentSum = currentSum + minDistance*minDistance

            if(minDiff == -1) or (currentSum/numberOfSums < minDiff):
                minDiff = currentSum/numberOfSums
                noteTrack = i

print "note track = "+str(noteTrack)
print [v[5] for v in m.notes if v[4]==noteTrack][0:5]
print [t for (s,t) in syls[0:5]]

## check
tracks2remove = [t for t in candidatesForRemoval if t!=noteTrack and t!=m.kartrack]
m.write_file(filename, "__"+filename, tracks2remove, None)

# put syllables in hash
##TODO: maybe do this with words
sylHash = {}
for (s,t) in syls:
    sylHash[s] = []

url = 'http://translate.google.com/translate_tts?tl=pt&q='
header = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' }
for s in sylHash:
    response = urllib2.urlopen(urllib2.Request(url+s.replace(' ',''), None, header))
    responseBytes = response.read()
    mp3FilePath = './mp3s/'+s.replace(' ','').decode('iso-8859-1')+'.mp3'
    f = open(mp3FilePath, 'wb')
    f.write(responseBytes)
    f.close()

