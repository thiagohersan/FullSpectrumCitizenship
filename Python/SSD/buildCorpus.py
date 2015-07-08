#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, subprocess, getopt
from Song import Song

HASHTAGS = ["OGIGANTEACORDOU",
            "MUDABRASIL",
            "ACORDABRASIL",
            "CHANGEBRAZIL",
            "OBRASILACORDOU",
            "VEMPRARUA",
            "CHUPADILMA",
            "SP17J",
            "PROTESTOSP",
            "PASSELIVRE",
            "MOVIMENTOPASSELIVRE",
            "NAOEPOR20CENTAVOSEPORDIREITOS",
            "VERASQUEUMFILHOTEUNAOFOGEALUTA",
            "COPAPRAQUEM"]

CORPUS_DIR = "./txts"
KARS_DIR = "../../../kars"
JS_DIR = "../../JS"

PERIODS = [(1370516400,1371294000), (1371298000,1372590000)]

def getSongText():
    if not os.path.exists(CORPUS_DIR):
        os.makedirs(CORPUS_DIR)

    corpusFile = open(os.path.join(CORPUS_DIR,"songs.txt"), 'w')
    allKarFiles = [ os.path.join(KARS_DIR,f) for f in os.listdir(KARS_DIR) if os.path.isfile(os.path.join(KARS_DIR,f)) and f.endswith(".kar") ]

    for f in allKarFiles:
        print "--- %s ---"%(os.path.basename(f))
        s = Song(f, justForTheLyrics=True)
        corpusFile.write(s.lyrics.decode('iso-8859-1').lower().encode('utf-8')+'\n\n')
        corpusFile.flush()

    corpusFile.close()

def getTweetText():
    if not os.path.exists(CORPUS_DIR):
        os.makedirs(CORPUS_DIR)

    corpusFile = open(os.path.join(CORPUS_DIR,"tweets.txt"), 'w')
    jsScript = os.path.join(JS_DIR, "buildTweetCorpus.js")

    for h in HASHTAGS:
        for (t0,t1) in PERIODS:
            numBlanks = 0
            for o in range(0,1000,10):
                print "--- %s[%s] [%s %s]---"%(h, o, t0, t1)
                out = subprocess.check_output("phantomjs %s %s %s %s %s"%(jsScript, h, o, t0, t1), shell=True)
                print out
                corpusFile.write(out)
                if (len(out) < 1) or (out.isspace()):
                    numBlanks += 1
                else:
                    numBlanks = 0
                # if 5 blanks in a row ... go to next hashtag/period (this also triggers if 50 RTs in a row)
                if numBlanks > 4:
                    break

    corpusFile.close()


if __name__=="__main__":
    if len(sys.argv) < 2:
        print "Please select song (-s --song) or tweet (-t --tweet) option"
        sys.exit(2)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "st", ["song", "tweet"])
    except getopt.GetoptError as err:
        print str(err)
        print "Please select song (-s --song) or tweet (-t --tweet) option"
        sys.exit(2)

    for o, a in opts:
        if o in ("-s", "--song"):
            getSongText()
        elif o in ("-t", "--tweet"):
            getTweetText()
