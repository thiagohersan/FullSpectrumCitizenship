# given karaoke syllables and times,
#     return a cleaned up array of (syllable, time) tuples and
#     an array of (word, time) tuples
def parseSyllables(karsyl__, kartimes__):
    # some initial clean up
    karsyl = list(karsyl__)
    for (i,s) in enumerate(karsyl):
        s = s.replace('/', ' ')
        s = s.replace('\\', ' ')
        s = s.replace(',', '')
        s = s.replace('.', '')
        s = s.replace('_',' ')
        karsyl[i] = s

    # get syllables and times
    syls = [(s,t) for (s,t) in zip(karsyl, kartimes__) if s!='']

    # this is a long string with the lyrics
    lyrics = ""
    for (s,t) in syls:
        lyrics += s
    lyrics = lyrics.strip()
    print lyrics.decode('iso-8859-1')

    # hack to deal with blank syllables and syllables that actually have more than one word
    sylsNoBlanks = [(s.strip(),t) for (s,t) in zip(karsyl, kartimes__) if s!='' and s!=' ']
    ultimateSyls = []
    for (s,t) in sylsNoBlanks:
        for w in s.split():
            ultimateSyls.append((w,t))

    # get tuple of (word, trigger-time)
    words = []
    sylIndex = 0
    for w in lyrics.split():
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
    syls = [(s,t) for (s,t) in syls if s!='' and s!=' ']

    return (syls, words)
