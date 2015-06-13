import urllib2, urllib, os, sys, wave, math, subprocess
import midifile
from getPitch import getPitchHz

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
        self.midi=midifile.midifile()
        self.midi.load_file(filename)
        self.FNULL = open(os.devnull, 'w')

    #   return a cleaned up array of (syllable, time) tuples and
    #   an array of (word, time) tuples
    def parseLyrics(self):
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

        ## TODO: put words with same start time back together

        # only return non-empty syllables
        self.syls = [(s.lower(),t) for (s,t) in syls if s!='' and s!=' ']
        self.words = words
        return (self.syls, self.words)

    def parseTones(self):
        noteTrack = None
        if self.syls is None or self.words is None:
            self.parseLyrics()

        # figure out which track has notes for the lyrics
        minDiff = -1
        candidatesForRemoval = []
        toneTempoList = []
        toneMedian = -1
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
                        toneMedian = int(currentToneMin + (currentToneMax-currentToneMin)/2)

        if len(toneTempoList) != len(self.syls):
            print "tone list length doesn't equal syllable list length"
            sys.exit(0)

        ## zip tone array into syls
        ##     this keeps track of tones relative to median
        self.tonedSyls = [(s.strip(),t,p-toneMedian,d) for ((s,t),(p,d)) in zip(self.syls, toneTempoList)]

        ## write out 
        tracks2remove = [t for t in candidatesForRemoval if t!=noteTrack and t!=self.midi.kartrack]
        #self.midi.write_file(self.filename, self.filename.replace(".kar", "__.kar"), tracks2remove, None)
        
        ## toned word list
        ultimateSyls = []
        for (s,t,p,d) in self.tonedSyls:
            for w in s.split():
                ultimateSyls.append((w,t,p,d))

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

        self.tonedWords = words

        return (self.tonedSyls, self.tonedWords)

    def prepSyllableVoice(self):
        if self.tonedSyls is None:
            self.parseTones()

        ## hash for downloading initial files
        ##     this maps to (filename, wave object, frequency)
        sylHash = {}
        for (s,t,p,d) in self.tonedSyls:
            sylHash[s] = None

        url = 'http://translate.google.com/translate_tts?tl=pt&q='
        header = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' }

        if not os.path.exists(self.MP3S_DIR):
            os.makedirs(self.MP3S_DIR)
        if not os.path.exists(self.WAVS_DIR):
            os.makedirs(self.WAVS_DIR)

        voiceFreqMin = -1
        voiceFreqMax = -1
        for s in sylHash:
            response = urllib2.urlopen(urllib2.Request(url+urllib.quote(s), None, header))
            responseBytes = response.read()
            mp3FilePath = self.MP3S_DIR+s.decode('iso-8859-1')+'.mp3'
            wavFilePath = mp3FilePath.replace('mp3','wav')
            f = open(mp3FilePath, 'wb')
            f.write(responseBytes)
            f.close()
            subprocess.call('ffmpeg -y -i '+mp3FilePath+" -ar 44100 "+wavFilePath, shell=True, stdout=self.FNULL, stderr=subprocess.STDOUT)
            os.remove(mp3FilePath)
            wavWave = wave.open(wavFilePath)
            wavLength = wavWave.getnframes()/float(wavWave.getframerate())
            wavFreq = getPitchHz(wavWave)
            sylHash[s] = (wavFilePath, wavLength, wavFreq)
            wavWave.close()

            if (voiceFreqMin == -1) or (wavFreq < voiceFreqMin):
                voiceFreqMin = wavFreq
            if (voiceFreqMax == -1) or (wavFreq > voiceFreqMax):
                voiceFreqMax = wavFreq

        ## get median voice freq
        voiceFreqMedian = voiceFreqMin + (voiceFreqMax-voiceFreqMin)/2

        voice = []
        for (i, (s,t,p,d)) in enumerate(self.tonedSyls):
            currentLength = sylHash[s][1]
            targetLength = max(d, 1e-6)

            currentFreq = sylHash[s][2]
            targetFreq = (2**(p/12.0))*voiceFreqMedian
            #targetFreq = (2**(p/12.0))*currentFreq

            tempoParam = (currentLength-targetLength)/targetLength*100.0
            if(currentLength < targetLength):
                tempoParam /= 2
            pitchParam = 12.0 * math.log(targetFreq/currentFreq, 2) / 4
            outputFile = "%s/%s.wav" % (self.WAVS_DIR,i)
            stParams = " %s %s -tempo=%s -pitch=%s" % (sylHash[s][0].replace(" ", "\ "), outputFile, tempoParam, pitchParam)
            subprocess.call('./soundstretch'+stParams, shell='True')

    def prepWordVoice(self):
        if self.tonedWords is None:
            self.parseTones()

        ## hash for downloading initial files
        ##     this maps to (filename, wave object, frequency)
        wordHash = {}
        for (w,t,p,d) in self.tonedWords:
            wordHash[w] = None

        url = 'http://translate.google.com/translate_tts?tl=pt&q='
        header = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' }

        if not os.path.exists(self.MP3S_DIR):
            os.makedirs(self.MP3S_DIR)
        if not os.path.exists(self.WAVS_DIR):
            os.makedirs(self.WAVS_DIR)

        voiceFreqMin = -1
        voiceFreqMax = -1
        for w in wordHash:
            response = urllib2.urlopen(urllib2.Request(url+urllib.quote(w), None, header))
            responseBytes = response.read()
            mp3FilePath = self.MP3S_DIR+w.decode('iso-8859-1')+'.mp3'
            wavFilePath = mp3FilePath.replace('mp3','wav')
            f = open(mp3FilePath, 'wb')
            f.write(responseBytes)
            f.close()
            subprocess.call('ffmpeg -y -i '+mp3FilePath+" -ar 44100 "+wavFilePath, shell=True, stdout=self.FNULL, stderr=subprocess.STDOUT)
            os.remove(mp3FilePath)
            wavWave = wave.open(wavFilePath)
            wavLength = wavWave.getnframes()/float(wavWave.getframerate())
            wavFreq = getPitchHz(wavWave)
            wordHash[w] = (wavFilePath, wavLength, wavFreq)
            wavWave.close()

            if (voiceFreqMin == -1) or (wavFreq < voiceFreqMin):
                voiceFreqMin = wavFreq
            if (voiceFreqMax == -1) or (wavFreq > voiceFreqMax):
                voiceFreqMax = wavFreq

        ## get median voice freq
        voiceFreqMedian = voiceFreqMin + (voiceFreqMax-voiceFreqMin)/2

        voice = []
        for (i, (w,t,p,d)) in enumerate(self.tonedWords):
            currentLength = wordHash[w][1]
            targetLength = max(d, 1e-6)

            currentFreq = wordHash[w][2]
            targetFreq = (2**(p[0]/12.0))*voiceFreqMedian

            tempoParam = (currentLength-targetLength)/targetLength*100.0
            #tempoParam /= 3 if(currentLength < targetLength) else 1.2
            tempoParam = 0 if(currentLength < targetLength) else tempoParam/1.2

            pitchParam = 12.0 * math.log(targetFreq/currentFreq, 2) / 3
            pitchParam = 0

            outputFile = "%s/%s.wav" % (self.WAVS_DIR,i)
            stParams = " %s %s -tempo=%s -pitch=%s" % (wordHash[w][0].replace(" ", "\ "), outputFile, tempoParam, pitchParam)
            subprocess.call('./soundstretch'+stParams, shell='True', stdout=self.FNULL, stderr=subprocess.STDOUT)
