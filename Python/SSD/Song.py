import urllib2, urllib, os, sys, shutil, wave, math, subprocess
import midifile, wave
from getPitch import getPitchHz

# escape space on filenames being sent to shell commands
def escSpace(s):
    return s.replace(" ", "\ ")

class Song:
    def __init__(self, filename):
        self.filename = filename
        self.songname = os.path.basename(filename).replace(".kar", "")
        self.MP3S_DIR = "./mp3s/"+self.songname+"/"
        self.WAVS_DIR = self.MP3S_DIR.replace("mp3","wav")
        self.syls = None
        self.words = None
        self.lyrics = None
        self.tonedSyls = None
        self.tonedWords = None
        self.firstNoteTime = None
        self.midi=midifile.midifile()
        self.midi.load_file(filename)
        self.FNULL = open(os.devnull, 'w')

    #   return a cleaned up array of (syllable, time) tuples and
    #   an array of (word, time) tuples
    def parseLyrics(self):
        if (self.syls is not None) and (self.words is not None):
            return (self.syls, self.words)

        # some initial clean up
        karsyl = list(self.midi.karsyl)
        kartimes = list(self.midi.kartimes)
        for (i,s) in enumerate(karsyl):
            s = s.replace('/', ' ')
            s = s.replace('\\', ' ')
            s = s.replace('_',' ')
            s = s.replace('\"', '')
            s = s.replace('\'', '')
            s = s.replace(',', '')
            s = s.replace('.', '')
            s = s.replace('!', '')
            s = s.replace('?', '')
            karsyl[i] = s

        # get syllables and times
        syls = [(s,t) for (s,t) in zip(karsyl, kartimes) if s!='']

        # this is a long string with the lyrics
        self.lyrics = ""
        for (s,t) in syls:
            self.lyrics += s
        self.lyrics = self.lyrics.strip()
        print self.lyrics.decode('iso-8859-1')

        # hack to deal with blank syllables and syllables that actually have more than one word
        sylsNoBlanks = [(s.strip(),t) for (s,t) in zip(karsyl, kartimes) if s!='' and s!=' ']
        ultimateSyls = []
        for (s,t) in sylsNoBlanks:
            for w in s.split():
                ultimateSyls.append((w,t))

        # get tuple of (word, trigger-time)
        words = []
        sylIndex = 0
        for w in self.lyrics.split():
            (s,t) = ultimateSyls[sylIndex]
            words.append((w,t))
            fromSyls = s
            sylIndex += 1
            while (fromSyls != w):
                (s,t) = ultimateSyls[sylIndex]
                fromSyls += s
                sylIndex += 1

        ## put words with same start time back together
        ultimateWords = []
        i = 0
        while (i < len(words)):
            currentWord = words[i]
            ii = i+1
            while (ii < len(words)) and (words[i][1] == words[ii][1]):
                currentWord = (currentWord[0]+" "+words[ii][0], currentWord[1])
                ii += 1
            i = ii
            ultimateWords.append(currentWord)

        # only return non-empty syllables
        self.syls = [(s.lower(),t) for (s,t) in syls if s!='' and s!=' ']
        self.words = words
        return (self.syls, self.words)

    def parseTones(self):
        if (self.tonedSyls is not None) and (self.tonedWords is not None):
            return (self.tonedSyls, self.tonedWords)

        if self.syls is None or self.words is None:
            self.parseLyrics()

        noteTrack = None
        # figure out which track has notes for the lyrics
        minDiff = -1
        candidatesForRemoval = []
        toneTempoList = []
        toneMedian = -1
        firstNoteTime = -1
        for n in range(self.midi.ntracks):
            thisTrack = [v for v in self.midi.notes if v[4]==n]
            if (len(thisTrack) > 0):
                candidatesForRemoval.append(n)

                # deal with percussion tracks with lots of "notes"
                if len(thisTrack) < 2*len(self.syls):
                    currentSum = 0
                    numberOfSums = len(self.syls)
                    currentToneList = []
                    currentToneMin = -1
                    currentToneMax = -1
                    thisTracksFirstNoteTime = thisTrack[0][5]

                    for (s,t) in self.syls:
                        minDistance = -1
                        minDistanceTone = -1
                        minDistanceTempo = -1
                        for (i,v) in enumerate(thisTrack):
                            if (minDistance == -1) or abs(t-v[5])<minDistance:
                                minDistance = abs(t-v[5])
                                minDistanceTone = v[0]
                                minDistanceTempo = 0

                                ii = i
                                while (minDistanceTempo == 0) and (ii+1<len(thisTrack)):
                                    minDistanceTempo = thisTrack[ii][5]-v[5]
                                    ii += 1
                                if (minDistanceTempo == 0):
                                    minDistanceTempo = thisTrack[ii][5]-thisTrack[ii-1][5]

                        currentSum = currentSum + minDistance*minDistance
                        currentToneList.append((minDistanceTone,minDistanceTempo))
                        if (currentToneMin == -1) or (minDistanceTone < currentToneMin):
                            currentToneMin = minDistanceTone
                        if (currentToneMax == -1) or (minDistanceTone > currentToneMax):
                            currentToneMax = minDistanceTone

                    if(minDiff == -1) or (currentSum/numberOfSums < minDiff):
                        minDiff = currentSum/numberOfSums
                        noteTrack = n
                        toneTempoList = currentToneList
                        firstNoteTime = thisTracksFirstNoteTime
                        toneMedian = int(currentToneMin + (currentToneMax-currentToneMin)/2)
                        toneSum = sum([tone for (tone,tempo) in toneTempoList])
                        print "tone(max, avg): %s %s"%(currentToneMax,toneSum/len(toneTempoList))

        if len(toneTempoList) != len(self.syls):
            print "tone list length doesn't equal syllable list length"
            sys.exit(0)

        ## zip tone array into syls
        ##     this keeps track of tones relative to median
        self.tonedSyls = [(s.strip(),t,p-toneMedian,d) for ((s,t),(p,d)) in zip(self.syls, toneTempoList)]
        self.firstNoteTime = firstNoteTime

        ## write out wav from stripped midi
        if not os.path.exists(self.WAVS_DIR):
            os.makedirs(self.WAVS_DIR)

        tracks2remove = [t for t in candidatesForRemoval if t!=noteTrack and t!=self.midi.kartrack]
        outFileKar = self.filename.replace(".kar", "__.kar")
        self.midi.write_file(self.filename, outFileKar, tracks2remove, None, noteTrack)
        outFileWav = "%s/00.%s.wav" % (self.WAVS_DIR,self.songname)
        midiParams = "-A 100 %s -OwM -o %s"%(outFileKar, outFileWav)
        subprocess.call('timidity '+midiParams, shell=True, stdout=self.FNULL, stderr=subprocess.STDOUT)
        os.remove(outFileKar)
        ## TODO: lower pitch of entire song if necessary

        ## toned word list
        ultimateSyls = []
        for (s,t,p,d) in self.tonedSyls:
            for w in s.split():
                ultimateSyls.append((w,t,p,d))
            if(len(s.split()) > 1):
                print "%s"%(s.decode('iso-8859-1'))

        # get tuple of (word, (trigger-times), (pitches), duration)
        words = []
        sylIndex = 0
        for w in self.lyrics.lower().split():
            (s,t,p,d) = ultimateSyls[sylIndex]
            fromSyls = s
            tt = [t]
            pp = [p]
            dd = d
            sylIndex += 1
            while (fromSyls != w):
                (s,t,p,d) = ultimateSyls[sylIndex]
                fromSyls += s
                tt.append(t)
                pp.append(p)
                dd += d
                sylIndex += 1
            words.append((w,tt, pp, dd))

        ## put words with same start time back together
        ultimateWords = []
        i = 0
        while (i < len(words)):
            currentWord = words[i]
            ii = i+1
            while (ii < len(words)) and (words[i][1][0] == words[ii][1][0]):
                currentWord = (currentWord[0]+" "+words[ii][0],
                    currentWord[1]+words[ii][1],
                    currentWord[2]+words[ii][2],
                    currentWord[3])
                ii += 1
            i = ii
            ultimateWords.append(currentWord)

        self.tonedWords = ultimateWords

        return (self.tonedSyls, self.tonedWords)

    def prepSyllableVoice(self):
        if self.tonedSyls is None:
            self.parseTones()

        ## hash for downloading initial files
        ##     this maps to (filename, wave object)
        sylHash = {}
        for (s,t,p,d) in self.tonedSyls:
            sylHash[s] = None

        url = 'http://translate.google.com/translate_tts?tl=pt&q='
        header = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' }

        if not os.path.exists(self.MP3S_DIR):
            os.makedirs(self.MP3S_DIR)
        if not os.path.exists(self.WAVS_DIR):
            os.makedirs(self.WAVS_DIR)

        for s in sylHash:
            response = urllib2.urlopen(urllib2.Request(url+urllib.quote(s), None, header))
            responseBytes = response.read()
            mp3FilePath = self.MP3S_DIR+s.decode('iso-8859-1')+'.mp3'
            wavFilePath = mp3FilePath.replace('mp3','wav')
            f = open(mp3FilePath, 'wb')
            f.write(responseBytes)
            f.close()
            ffParams = "-y -i %s -ar 44100 %s"%(escSpace(mp3FilePath), escSpace(wavFilePath))
            subprocess.call('ffmpeg '+ffParams, shell=True, stdout=self.FNULL, stderr=subprocess.STDOUT)
            wavWave = wave.open(wavFilePath)
            wavLength = wavWave.getnframes()/float(wavWave.getframerate())
            wavWave.close()
            sylHash[s] = (wavFilePath, wavLength)
        shutil.rmtree(self.MP3S_DIR)

        for (i, (s,t,p,d)) in enumerate(self.tonedSyls):
            currentLength = sylHash[s][1]
            targetLength = max(d, 1e-6)

            tempoParam = (currentLength-targetLength)/targetLength*100.0
            tempoParam = 0 if(currentLength < targetLength) else tempoParam/1.2

            outputFile = "%s/%s.wav" % (self.WAVS_DIR,i)
            stParams = "%s %s -tempo=%s" % (escSpace(sylHash[s][0]), outputFile, tempoParam)
            subprocess.call('./soundstretch '+stParams, shell='True', stdout=self.FNULL, stderr=subprocess.STDOUT)

    def prepWordVoice(self):
        if self.tonedWords is None:
            self.parseTones()

        ## hash for downloading initial files
        ##     this maps to (filename, wave object)
        wordHash = {}
        for (w,t,p,d) in self.tonedWords:
            wordHash[w] = None

        url = 'http://translate.google.com/translate_tts?tl=pt&q='
        header = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' }

        if not os.path.exists(self.MP3S_DIR):
            os.makedirs(self.MP3S_DIR)
        if not os.path.exists(self.WAVS_DIR):
            os.makedirs(self.WAVS_DIR)

        for w in wordHash:
            response = urllib2.urlopen(urllib2.Request(url+urllib.quote(w), None, header))
            responseBytes = response.read()
            mp3FilePath = self.MP3S_DIR+w.decode('iso-8859-1')+'.mp3'
            wavFilePath = mp3FilePath.replace('mp3','wav')
            f = open(mp3FilePath, 'wb')
            f.write(responseBytes)
            f.close()
            ffParams = "-y -i %s -ar 44100 %s"%(escSpace(mp3FilePath), escSpace(wavFilePath))
            subprocess.call('ffmpeg '+ffParams, shell=True, stdout=self.FNULL, stderr=subprocess.STDOUT)
            wavWave = wave.open(wavFilePath)
            wavLength = wavWave.getnframes()/float(wavWave.getframerate())
            wavWave.close()
            wordHash[w] = (wavFilePath, wavLength)
        shutil.rmtree(self.MP3S_DIR)

        voiceData = []
        voiceWriter = None
        for (i, (w,t,p,d)) in enumerate(self.tonedWords):
            if(" " in w):
                print "%s.wav %s"%(i, w)

            currentLength = wordHash[w][1]
            targetLength = max(d, 1e-6)

            tempoParam = (currentLength-targetLength)/targetLength*100.0
            #tempoParam /= 3 if(currentLength < targetLength) else 1.2
            tempoParam = 0 if(currentLength < targetLength) else tempoParam

            outputFile = "%s/%s.wav" % (self.WAVS_DIR,i)
            stParams = "%s %s -tempo=%s" % (escSpace(wordHash[w][0]), outputFile, tempoParam)
            subprocess.call('./soundstretch '+stParams, shell='True', stdout=self.FNULL, stderr=subprocess.STDOUT)

            voiceReader = wave.open(outputFile)
            framerate = voiceReader.getframerate()
            sampwidth = voiceReader.getsampwidth()
            voiceBytes = voiceReader.readframes(voiceReader.getnframes())
            voiceFloats = wave.struct.unpack("%dh"%(len(voiceBytes)/sampwidth), voiceBytes)

            if (voiceWriter is None):
                voiceFilename = "%s/%s.wav" % (self.WAVS_DIR,"00.vox")
                voiceWriter = wave.open(voiceFilename, 'w')
                voiceWriter.setparams((voiceReader.getnchannels(), sampwidth, framerate, 8, 'NONE', 'NONE'))

            # pad space between words with 0s
            ## TODO: deal with case of overshooting (due to words with same start time)
            voiceData += [0] * (int((t[0]-self.firstNoteTime)*framerate) - len(voiceData))
            voiceData += voiceFloats

            # close voice wav
            voiceReader.close()

        for (x,y) in zip(voiceData[0::2], voiceData[1::2]):
            voiceWriter.writeframes(wave.struct.pack("hh", x,y))
        voiceWriter.close()

        # TODO: remove all temp wav files
