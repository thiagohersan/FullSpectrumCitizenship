#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, subprocess
from Song import Song

CORPUS_DIR = "./txts"
KARS_DIR = "../../../kars"

if not os.path.exists(CORPUS_DIR):
    os.makedirs(CORPUS_DIR)

corpusFile = open(os.path.join(CORPUS_DIR,"songs.txt"), 'w')
allKarFiles = [ os.path.join(KARS_DIR,f) for f in os.listdir(KARS_DIR) if os.path.isfile(os.path.join(KARS_DIR,f)) and f.endswith(".kar") ]

for f in allKarFiles:
    print "--- %s ---"%(os.path.basename(f))
    s = Song(f, justForTheLyrics=True)
    corpusFile.write(s.lyrics.decode('iso-8859-1').encode('utf-8')+'\n\n')
    corpusFile.flush()

corpusFile.close()
