#!/usr/bin/env python

import midifile, time, datetime, sys
import pygame
import pyglet

filename = ''
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename=raw_input('Please enter filename of .mid or .kar file:')

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

# put syllables in hash
sylHash = {}
for (s,t) in syls:
    mp3FilePath = './mp3s/'+s.replace(' ','').decode('iso-8859-1')+'.mp3'
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

