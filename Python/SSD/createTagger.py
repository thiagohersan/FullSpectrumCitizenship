#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nltk
from nltk.corpus import floresta
import cPickle

FILENAME = "txts/floresta_trigram.pos"

def simplify_tag(t):
    if '+' in t:
        return t[t.index('+')+1:]
    else:
        return t

tsents = floresta.tagged_sents()
tsents = [[(w.lower(),simplify_tag(t)) for (w,t) in sent] for sent in tsents if sent]
train = tsents[100:]
test = tsents[:100]

tagger0 = nltk.DefaultTagger('n')
tagger1 = nltk.UnigramTagger(train, backoff=tagger0)
tagger2 = nltk.BigramTagger(train, backoff=tagger1)
tagger = nltk.TrigramTagger(train, backoff=tagger2)

tagger.evaluate(test)

with open(FILENAME, 'wb') as outFile:
    cPickle.dump(tagger, outFile, -1)
