#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, operator, cPickle, random


class WordTrader:
    class LoopException(Exception):
        pass

    def reset(self):
        self.replacementWords = {'cais':'', 'quas':'', 'caringundum':''}
        self.taken = []

    def __init__(self, originalCorpusFile, targetCorpusFile):
        self.originalWords = WordAnalyzer(originalCorpusFile)
        self.targetWords = WordAnalyzer(targetCorpusFile)
        self.reset()
    
    def trade(self, originalWord, enc='utf-8'):
        originalWord = originalWord.decode(enc)
        if originalWord in self.replacementWords:
            return self.replacementWords[originalWord]

        for (oWord, oPos) in WordAnalyzer.tagger.tag([originalWord]):
            oPosList = self.originalWords.posWords.get(oPos, [])
            tPosList = self.targetWords.posWords.get(oPos, [])
            try:
                oWordIndexPct = oPosList.index(oWord)/float(len(oPosList))
                # word is in original corpus
                if random.random() > oWordIndexPct:
                    # word is somewhat common, let's swap it
                    # (could use len or other metric here)
                    (candidate, minCost) = ('', -1)
                    posListStartIndex = int(oWordIndexPct*len(tPosList)) if oWordIndexPct>0.6 else 0
                    for w in tPosList[posListStartIndex:]:
                        # don't repeat words
                        if w not in self.taken:
                            cCost = abs(len(oWord) - len(w))
                            if (minCost < 0) or ((cCost < minCost) and random.random() < 0.7):
                                minCost = cCost
                                candidate = w
                            if (minCost > -1) and (minCost < 3):
                                break

                    # prevents matching words with very different sizes
                    if minCost > 3:
                        minCost = 0
                        candidate = oWord

                    if minCost is not -1:
                        # found something in for loop
                        self.replacementWords[originalWord] = candidate
                        self.taken.append(candidate)
                        return self.replacementWords[originalWord]

                # never found a candidate, tPosList was empty or original word not very common
                raise WordTrader.LoopException

            except (ValueError, ZeroDivisionError, WordTrader.LoopException) as e:
                self.replacementWords[originalWord] = originalWord
                return self.replacementWords[originalWord]
            

class WordAnalyzer:
    TAGGER_FILENAME = "txts/floresta_trigram.pos"
    BAD_CHARS = re.compile('[.?$*^+()\"\'!,;:<>/%&_=#~]')
    NON_WORDS = ['d', 'de', 'da', 'das', 'do', 'dos',
                 'e', 'a', 'as', 'o', 'os', 'ao', 'ô', 'ó', 'à',
                 'em', 'na', 'nas', 'no', 'nos', 'nessa', 'nisso', 'nesse',
                 'essa', 'esse', 'isso', 'isto', 'aquela', 'aquele', 'aquilo',
                 'q', 'que', 'quem', 'com', 'como', 'pelo',
                 'p', 'pra', 'pras', 'pro', 'pros', 'para', 'por',
                 'uma', 'umas', 'um', 'uns', 'mais', 'mas',
                 'me', 'te', 'se',
                 'rt']
    GOOD_POS = ['adj', 'adv', 'in', 'n', 'prop',
                'v-fin', 'v-pcp', 'v-ger', 'v-inf',
                'pron-indp', 'pron-pers']
    MAX_WORDS_PER_POS = 200

    with open(TAGGER_FILENAME, 'rb') as taggerFile:
        tagger = cPickle.load(taggerFile)

    def __init__(self, filename):
        self.words = {}
        self.posWords = {}
        self.wordCount = 0.0
        self.name = filename

        with open(filename, 'r') as txtFile:
            for line in txtFile:
                line0 = line
                line = re.sub('#ogiganteacordou', 'o gigante acordou', line)
                line = re.sub('#mudabrasil', 'muda brasil', line)
                line = re.sub('#acordabrasil', 'acorda brasil', line)
                line = re.sub('#changebrazil', 'muda brasil', line)
                line = re.sub('#obrasilacordou', 'brasil acordou', line)
                line = re.sub('#vemprarua', 'vem pra rua', line)
                line = re.sub('#chupadilma', 'chupa dilma', line)
                line = re.sub('#protestosp', 'protesto sp', line)
                line = re.sub('#passelivre', 'passe livre', line)
                line = re.sub('#movimentopasselivre', 'movimento passe livre', line)
                line = re.sub('#naoepor20centavosepordireitos', 'centavos direitos', line)
                line = re.sub('#verasqueumfilhoteunaofogealuta', 'verás que um filho teu não foge a luta', line)
                line = re.sub('#verásqueumfilhoteunãofogealuta', 'verás que um filho teu não foge a luta', line)
                line = re.sub('#copapraquem', 'copa pra quem', line)
                line = re.sub('ñ', 'não', line)
                line = WordAnalyzer.BAD_CHARS.sub('', line)
                line = re.sub(' -+', ' ', line)
                line = re.sub('-+ ', ' ', line)

                for word in line.split():
                    word = word.decode('utf-8').lower().encode('utf-8')
                    if word not in WordAnalyzer.NON_WORDS:
                        self.words[word] = self.words.get(word,0) + 1
                        self.wordCount += 1

        self.sortedWords = sorted(self.words.iteritems(), key=operator.itemgetter(1), reverse=True)
        self.sortedWords = [(w.decode('utf-8'), c/self.wordCount) for (w,c) in self.sortedWords]

        # organize by POS
        for w,c in self.sortedWords:
            for (ww, pos) in WordAnalyzer.tagger.tag([w]):
                if (pos in WordAnalyzer.GOOD_POS):
                    ll = self.posWords.setdefault(pos,[])
                    if len(ll)<WordAnalyzer.MAX_WORDS_PER_POS:
                        ll.append(ww)

    def printTop(self, n=50):
        print "%s (%0.0f total words) (%0.0f unique)"%(self.name.upper(), self.wordCount, len(self.sortedWords))
        for w,c in self.sortedWords[:n]:
            print "\t%s (%0.2f%%)"%(w, c*100)

    def printPos(self, n=10):
        self.printTop(0)
        for pos in self.posWords:
            print "\t%s (%0.0f words)"%(pos, len(self.posWords[pos]))
            for w in self.posWords[pos][:n]:
                print "\t\t%s"%(w)

if __name__=="__main__":
    tweetTrader=WordTrader("txts/songs.txt", "txts/tweets.txt")
    blogTrader=WordTrader("txts/songs.txt", "txts/blogs.txt")
