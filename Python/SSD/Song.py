from getPitch import getPitchHz
import midifile
import wave

class Song:
    def __init__(self, filename):
        self.filename = filename
        self.songname = filename.replace(".kar", "")
        self.MP3S_DIR = "./mp3s/"+self.songname+"/"
        self.WAVS_DIR = self.MP3S_DIR.replace("mp3","wav")
        self.syls = None
        self.words = None
        self.lyrics = None
        self.tonedSyls = None
        self.midi=midifile.midifile()
        self.midi.load_file(filename)

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

        for (w,t) in words:
           print w.decode('iso-8859-1')+" "+str(t)

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
        toneList = []
        for i in range(self.midi.ntracks):
            thisTrack = [v for v in self.midi.notes if v[4]==i]
            if (len(thisTrack) > 0):
                candidatesForRemoval.append(i)

                # deal with percussion tracks with lots of "notes"
                if len(thisTrack) < 2*len(self.syls):
                    currentSum = 0
                    numberOfSums = len(self.syls)
                    currentToneList = []

                    for (s,t) in self.syls:
                        minDistance = -1
                        minDistanceTone = -1
                        for v in thisTrack:
                            if (minDistance == -1) or abs(t-v[5])<minDistance:
                                minDistance = abs(t-v[5])
                                minDistanceTone = v[0]
                        currentSum = currentSum + minDistance*minDistance
                        currentToneList.append(minDistanceTone)

                    if(minDiff == -1) or (currentSum/numberOfSums < minDiff):
                        minDiff = currentSum/numberOfSums
                        noteTrack = i
                        toneList = currentToneList

        if len(toneList) != len(self.syls):
            print "tone list length doesn't equal syllable list length"
        
        ## zip tone array into syls
        ## TODO: (keep track of relative tones with min/max/avg)
        self.tonedSyls = [(s,t,n) for ((s,t),n) in zip(self.syls, toneList)]

        ## check
        print "note track = "+str(noteTrack)
        print [v[5] for v in self.midi.notes if v[4]==noteTrack][0:5]
        print [t for (s,t) in self.syls[0:5]]
    
        ## write out 
        tracks2remove = [t for t in candidatesForRemoval if t!=noteTrack and t!=self.midi.kartrack]
        self.midi.write_file(self.filename, self.filename.replace(".kar", "__.kar"), tracks2remove, None)
        
        return self.tonedSyls

    def prepVoice(Self):
        if self.tonedSyls is None:
            self.parseTones()

        ## hash for downloading initial files
        sylHash = {}
        for (s,t,n) in self.tonedSyls:
            sylHash[s.strip()] = None

        url = 'http://translate.google.com/translate_tts?tl=pt&q='
        header = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' }

        if not os.path.exists(MP3S_DIR):
            os.makedirs(MP3S_DIR)
        if not os.path.exists(WAVS_DIR):
            os.makedirs(WAVS_DIR)

        for w in sylHash:
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
            sylHash[w] = wavFilePath

        ## TODO: get freq of voice closest to avg sound to use as base freq
        avgNoteFreq = 400

        voice = []
        for (i, (s,t,n)) in enumerate(self.tonedSyls):
            targetLength = 0
            if(i+1 < len(self.tonedSyls)):
                targetLength = self.tonedSyls[i+1][1] - t
            else:
                targetLength = self.tonedSyls[1][1] - self.tonedSyls[0][1]

            mWav = wave.open(sylHash[s.strip()])
            ## TODO: scale time
            ## TODO: write file i.wav or keep wav object

            currentFreq = getPitchHz(mWav)
            targetFreq = (2**(n/12))*avgNoteFreq
            ## TODO: scale frequency
            ## TODO: write file i.wav
