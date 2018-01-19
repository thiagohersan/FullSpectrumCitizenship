#!/usr/bin/env python

import midifile, time, datetime, sys
import pygame

pygame.init()
screenx=1280
screeny=778
screen=pygame.display.set_mode([screenx,screeny])
font=pygame.font.Font(None,60)
color1=(213,0,0,0)
color2=(250,250,250,0)

m=midifile.midifile()
filename = "../DominanceRadio/kars/tristeza.kar"
m.load_file(filename)

pygame.mixer.init()
pygame.mixer.music.load(filename)

for (i,s) in enumerate(zip(m.karsyl, m.kartimes)):
  syl = s[0].replace(' ','').decode('latin')
  print "[%d]: %s (%.5f)"%(i,syl,s[1])

m.karsyl[1] = "Gi"
m.karsyl[2] = "gan"
m.karsyl[3] = "te"

m.karsyl[17] = " acor"
m.karsyl[18] = "da"

m.karsyl[22] = " sen"
m.karsyl[23] = "do"

m.karsyl[30] = " pro"
m.karsyl[31] = "tes"
m.karsyl[32] = "to"

m.karsyl[52] = " fa"
m.karsyl[53] = "zer"

m.karsyl[57] = " ru"
m.karsyl[58] = "a"

m.karsyl[69] = " mu"
m.karsyl[70] = "dar"

m.karsyl[86] = " fa"
m.karsyl[87] = "zer"

m.karsyl[91] = " ru"
m.karsyl[92] = "a"

m.karsyl[103] = " mu"
m.karsyl[104] = "dar"

def play():
  pygame.mixer.music.play(0,0) # Start song at 0 and don't loop
  start=datetime.datetime.now()

  #start=start-datetime.timedelta(0,9) # To start lyrics at a later point
  dt=0.
  while pygame.mixer.music.get_busy():
      dt=(datetime.datetime.now()-start).total_seconds()
      m.update_karaoke(dt)

      for iline in range(3):
          l=font.size(m.karlinea[iline]+m.karlineb[iline])[0]
          x0a=screenx/2-l/2.
          linea=font.render(m.karlinea[iline],0,color1)
          lineb=font.render(m.karlineb[iline],0,color2)
          recta=screen.blit(linea,[x0a,280+iline*60])
          x0b=x0a+recta.width
          recbt=screen.blit(lineb,[x0b,280+iline*60])

      pygame.display.update()
      screen.fill(0)

      time.sleep(.1)


