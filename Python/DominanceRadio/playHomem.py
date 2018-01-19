#!/usr/bin/env python
# -*- coding: utf-8 -*-

import midifile, time, datetime, sys
import pygame

pygame.init()
screenx=1280
screeny=778
screen=pygame.display.set_mode([screenx,screeny])
font=pygame.font.Font(None,60)
color1=(213,0,0,0)
color2=(8,8,8,0)

m=midifile.midifile()
filename = "../DominanceRadio/kars/homem.kar"
m.load_file(filename)

pygame.mixer.init()
pygame.mixer.music.load(filename)

for (i,s) in enumerate(zip(m.karsyl, m.kartimes)):
  syl = s[0].decode('latin')
  #print "[%d]: %s (%.5f)"%(i,syl,s[1])
  if(syl == 'Nun' and m.karsyl[i+1] == 'ca'):
    m.karsyl[i] = 'Nã'.decode('utf-8').encode('latin')
    m.karsyl[i+1] = 'o'
  elif(syl == ' vi' and m.karsyl[i+1] == ' ras'):
    m.karsyl[i] = ' vem'
  elif(syl == ' co' and m.karsyl[i+1] == 'bra'):
    m.karsyl[i] = ' co'
    m.karsyl[i+1] = 'pa'
  elif(syl == ' co' and m.karsyl[i+1] == 'rrer'):
    m.karsyl[i] = ' mu'
    m.karsyl[i+1] = 'dar'
  elif(syl == ' co' and m.karsyl[i+1] == 'me'):
    m.karsyl[i] = ' acor'
    m.karsyl[i+1] = 'da'
  elif(syl == ' sou' and m.karsyl[i+2] == ' ho' and m.karsyl[i+3] == 'mem'):
    m.karsyl[i] = ' vou'
    m.karsyl[i+1] = ' pra'
    m.karsyl[i+2] = ' ru'
    m.karsyl[i+3] = 'a'
  elif(syl == ' sou é ho'.decode('utf-8') and m.karsyl[i+1] == 'mem'):
    m.karsyl[i] = ' vou pra'
    m.karsyl[i+1] = ' rua'
  elif(syl == ' sou é'.decode('utf-8') and m.karsyl[i+1] == ' ho'):
    m.karsyl[i] = ' vou pra'
    m.karsyl[i+1] = ' ru'
    m.karsyl[i+2] = 'a'
  elif(syl == ' ho' and m.karsyl[i+1] == 'mem' and m.karsyl[i+2] == ' com'):
    m.karsyl[i] = ' pra'
    m.karsyl[i+1] = ' rua'
  elif(syl == ' mui' and m.karsyl[i+1] == 'to' and m.karsyl[i+2] == ' ho'):
    m.karsyl[i+2] = ' ru'
    m.karsyl[i+3] = 'a'
  elif(syl == ' co' and m.karsyl[i+1] == 'mo' and m.karsyl[i+2] == ' sou'):
    m.karsyl[i+2] = ' vou'
  elif(syl == ' diz' and m.karsyl[i+1] == ' que eu' and m.karsyl[i+2] == ' sou'):
    m.karsyl[i+2] = ' vou'
  elif(syl == 'ga' and m.karsyl[i+1] == ' sou' and m.karsyl[i+2] == ' mui'):
    m.karsyl[i+1] = ' vou'
  elif(syl == 'Eu' and m.karsyl[i+1] == ' sou'):
    m.karsyl[i+1] = ' vou'
  elif(syl == 'Sou'):
    m.karsyl[i] = 'Vou'
  elif(syl == 'Me' and m.karsyl[i+1] == 'ni' and m.karsyl[i+2] == 'no'):
    m.karsyl[i] = 'Gi'
    m.karsyl[i+1] = 'gan'
    m.karsyl[i+2] = 'te'
  elif(syl == 'Me' and m.karsyl[i+1] == 'ni' and m.karsyl[i+2] == 'no eu'):
    m.karsyl[i] = 'Gi'
    m.karsyl[i+1] = 'gan'
    m.karsyl[i+2] = 'te eu'
  elif(syl == 'Já es'.decode('utf-8') and m.karsyl[i+1] == 'tou'):
    m.karsyl[i] = 'Acor'
    m.karsyl[i+1] = 'dou'
    m.karsyl[i+2] = ' ho'
    m.karsyl[i+3] = 'je'
  elif(syl == 'Na' and m.karsyl[i+1] == 'mo' and m.karsyl[i+2] == 'ran'):
    m.karsyl[i] = 'Fa'
    m.karsyl[i+1] = 'ze'
    m.karsyl[i+2] = 'n'
    m.karsyl[i+3] = 'do'
  elif(syl == ' na' and m.karsyl[i+1] == 'mo' and m.karsyl[i+2] == 'ran'):
    m.karsyl[i] = ' fa'
    m.karsyl[i+1] = 'ze'
    m.karsyl[i+2] = 'n'
    m.karsyl[i+3] = 'do'
  elif(syl == ' prá'.decode('utf-8') and m.karsyl[i+1] == ' ca' and m.karsyl[i+2] == 'sar'):
    m.karsyl[i] = ' mani'
    m.karsyl[i+1] = 'fes'
    m.karsyl[i+2] = 'tar'
  elif(syl == 'bis' and m.karsyl[i+1] == 'lo' and m.karsyl[i+2] == 'mem'):
    m.karsyl[i] = 'bi'
    m.karsyl[i+1] = 'so'
    m.karsyl[i+2] = 'mem'

for (i,s) in enumerate(zip(m.karsyl, m.kartimes)):
  syl = s[0].decode('latin')
  print "[%d]: %s (%.5f)"%(i,syl,s[1])

def playHomem():
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
      screen.fill((250,250,250))

      time.sleep(.1)


