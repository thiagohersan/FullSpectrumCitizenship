#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, subprocess

HASHTAGS = ["OGIGANTEACORDOU",
            "OGIGANTEACRODOU",
            "MUDABRASIL",
            "ACORDABRASIL",
            "CHANGEBRAZIL",
            "VEMPRARUA",
            "SP17J",
            "PROTESTOSP",
            "PASSELIVRE",
            "MOVIMENTOPASSELIVRE",
            "NAOEPOR20CENTAVOSEPORDIREITOS",
            "VERASQUEUMFILHOTEUNAOFOGEALUTA",
            "ACORDABRASIL",
            "OBRASILACORDOU",
            "COPAPRAQUEM"]

CORPUS_DIR = "./txts"

if not os.path.exists(CORPUS_DIR):
    os.makedirs(CORPUS_DIR)

corpusFile = open(os.path.join(CORPUS_DIR,"tweets.txt"), 'w')

for h in HASHTAGS:
    numBlanks = 0
    for o in range(0,1000,10):
        print "--- %s[%s] ---"%(h, o)
        out = subprocess.check_output('phantomjs ../../JS/buildTweetCorpus.js '+h+' '+str(o), shell=True)
        print out
        corpusFile.write(out)
        if (len(out) < 1) or (out.isspace()):
            numBlanks += 1
        else:
            numBlanks = 0
        # if 4 blanks in a row ... go to next hashtag (this also triggers if 50 RTs in a row)
        if numBlanks > 4:
            break

corpusFile.close()

