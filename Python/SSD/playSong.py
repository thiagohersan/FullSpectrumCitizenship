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

pygame.mixer.init()
pygame.mixer.music.load(filename)
pygame.mixer.music.set_volume(0.0)

WORDS = True
#WORDS = False

# get tuples for syllable and word start times
s.prepWordVoice() if WORDS is True else s.prepSyllableVoice()
(syls, words) = s.parseLyrics()

wavList = []
if(WORDS is True):
    for i in range(len(words)):
        wavFilePath = s.WAVS_DIR+str(i)+".wav"
        wavList.append(pyglet.media.load(wavFilePath, streaming=False))
else:
    for i in range(len(syls)):
        wavFilePath = s.WAVS_DIR+str(i)+".wav"
        wavList.append(pyglet.media.load(wavFilePath, streaming=False))

pygame.mixer.music.play(0,0)
start=datetime.datetime.now()

nextIndex = 0
dt=0.
while pygame.mixer.music.get_busy():
    dt=(datetime.datetime.now()-start).total_seconds()
    s.midi.update_karaoke(dt)

    if(WORDS is True):
        if nextIndex < len(words):
            (i,t) = words[nextIndex]
            if(dt>=t):
                wavList[nextIndex].play()
                nextIndex = nextIndex + 1
    else:
        if nextIndex < len(syls):
            (i,t) = syls[nextIndex]
            if(dt>=t):
                wavList[nextIndex].play()
                nextIndex = nextIndex + 1

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

