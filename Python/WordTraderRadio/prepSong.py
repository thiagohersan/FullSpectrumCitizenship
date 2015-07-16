#!/usr/bin/env python

import sys
from Song import Song
from WordTrader import WordTrader, ManualWordTrader

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

tweetTrader=WordTrader("txts/songs.txt", "txts/tweets.txt")
blogTrader=WordTrader("txts/songs.txt", "txts/blogs.txt")
manualTrader=ManualWordTrader("txts/manual.tweets.txt")

## plain
#s.prepWordVoice()

## with automatic dict
s.prepWordVoice(tweetTrader)

## with a manual dict
#s.prepWordVoice(manualTrader)
