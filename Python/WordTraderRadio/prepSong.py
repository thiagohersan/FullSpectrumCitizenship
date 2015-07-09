#!/usr/bin/env python

import sys
from Song import Song

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

#s.prepSyllableVoice()
s.prepWordVoice()
