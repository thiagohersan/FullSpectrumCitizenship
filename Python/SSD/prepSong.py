#!/usr/bin/env python

from Song import Song
import urllib2, urllib, sys, os
from pydub import AudioSegment

MP3S_DIR = "./mp3s/"
WAVS_DIR = MP3S_DIR.replace("mp3","wav")

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

# get tuples for syllable and word start times
(syls, words) = s.parseLyrics()
tsyls = s.parseTones()

# get TTS word files with hash to avoid copies
wordHash = {}
for (w,t) in words:
    wordHash[w] = []

## add syllables as well
for (s,t) in syls:
    wordHash[s.strip()] = []

url = 'http://translate.google.com/translate_tts?tl=pt&q='
header = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' }

if not os.path.exists(MP3S_DIR):
    os.makedirs(MP3S_DIR)
if not os.path.exists(WAVS_DIR):
    os.makedirs(WAVS_DIR)

for w in wordHash:
    response = urllib2.urlopen(urllib2.Request(url+urllib.quote(w), None, header))
    responseBytes = response.read()
    mp3FilePath = MP3S_DIR+w.decode('iso-8859-1')+'.mp3'
    wavFilePath = mp3FilePath.replace('mp3','wav')
    f = open(mp3FilePath, 'wb')
    f.write(responseBytes)
    f.close()
    song = AudioSegment.from_mp3(mp3FilePath)
    song.export(wavFilePath, format="wav")
    os.remove(mp3FilePath)

