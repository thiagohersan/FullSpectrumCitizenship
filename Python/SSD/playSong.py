#!/usr/bin/env python

from Song import Song
import time, datetime, sys
import pygame
import pyglet

filename = ''
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    print "Please provide a .kar karaoke file."
    sys.exit(0)

s = Song(filename)
if not s.midi.karfile:
    print "This is not a karaoke file."
    sys.exit(0)

pygame.init()
screenx=1200
screeny=600
screen=pygame.display.set_mode([screenx,screeny])
font=pygame.font.Font(None,60)
color1=(100,100,250,0)
color2=(250,250,250,0)

# get tuples for syllable and word start times
(syls, words) = s.parseLyrics()

# get TTS word files with hash to avoid copies
wordHash = {}
for (w,t) in words:
    mp3FilePath = './mp3s/'+w.decode('iso-8859-1')+'.mp3'
    wordHash[w] = pyglet.media.load(mp3FilePath.encode('utf8'), streaming=False)

pygame.mixer.init()
pygame.mixer.music.load(filename)
pygame.mixer.music.set_volume(0.0)
pygame.mixer.music.play(0,0)
start=datetime.datetime.now()

nextWord = 0
dt=0.
while pygame.mixer.music.get_busy():
    dt=(datetime.datetime.now()-start).total_seconds()
    s.midi.update_karaoke(dt)

    if nextWord < len(words):
        (w,wt) = words[nextWord]
        if(dt>=wt):
            wordHash[w].play()
            nextWord = nextWord + 1

    for iline in range(3):
        l=font.size(s.midi.karlinea[iline]+s.midi.karlineb[iline])[0]
        x0a=screenx/2-l/2.
        linea=font.render(s.midi.karlinea[iline],0,color1)
        lineb=font.render(s.midi.karlineb[iline],0,color2)
        recta=screen.blit(linea,[x0a,80+iline*60])
        x0b=x0a+recta.width
        recbt=screen.blit(lineb,[x0b,80+iline*60])

    pygame.display.update()
    screen.fill(0)

    time.sleep(.02)

