#!/usr/bin/env python

# This example shows how to use pygame to build a graphic frontend for
#  a karaoke application. 
# Requires: pygame.

import midifile, time, datetime, sys
import urllib2
import pygame
import pyglet

filename = ''
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    #filename="fervendo.kar"
    #filename="leaozinho.kar"
    filename="bandeira.kar"
    #filename=raw_input('Please enter filename of .mid or .kar file:')

m=midifile.midifile()
m.load_file(filename)

pygame.init()
screenx=1200
screeny=600
screen=pygame.display.set_mode([screenx,screeny])
font=pygame.font.Font(None,60)
color1=(100,100,250,0)
color2=(250,250,250,0)

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
    sylHash[s] = pyglet.media.load(mp3FilePath.encode('utf8'), streaming=False)


pygame.mixer.init()
pygame.mixer.music.load(filename)
pygame.mixer.music.set_volume(0)
pygame.mixer.music.play(0,0)
start=datetime.datetime.now()

nextSyl = 0
dt=0.
while pygame.mixer.music.get_busy():
    dt=(datetime.datetime.now()-start).total_seconds()
    m.update_karaoke(dt)
    
    if nextSyl < len(syls):
        (s,st) = syls[nextSyl]
        if(dt>=st):
            sylHash[s].play()
            nextSyl = nextSyl + 1

    for iline in range(3):
        l=font.size(m.karlinea[iline]+m.karlineb[iline])[0]
        x0a=screenx/2-l/2.
        linea=font.render(m.karlinea[iline],0,color1)
        lineb=font.render(m.karlineb[iline],0,color2)
        recta=screen.blit(linea,[x0a,80+iline*60])
        x0b=x0a+recta.width
        recbt=screen.blit(lineb,[x0b,80+iline*60])

    pygame.display.update()
    screen.fill(0)

    time.sleep(.02)



