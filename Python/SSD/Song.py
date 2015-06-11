import midifile

class Song:
    def __init__(self, filename):
        self.filename = filename
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
        self.syls = [(s,t) for (s,t) in syls if s!='' and s!=' ']
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
        ## TODO: (keep track of min/max??)
        self.tonedSyls = [(s,t,n) for ((s,t),n) in zip(self.syls, toneList)]

        ## check
        print "note track = "+str(noteTrack)
        print [v[5] for v in self.midi.notes if v[4]==noteTrack][0:5]
        print [t for (s,t) in self.syls[0:5]]
    
        ## write out 
        tracks2remove = [t for t in candidatesForRemoval if t!=noteTrack and t!=self.midi.kartrack]
        self.midi.write_file(self.filename, self.filename.replace(".kar", "__.kar"), tracks2remove, None)
        
        return self.tonedSyls
