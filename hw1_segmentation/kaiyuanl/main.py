#The is the main program to run
import sys, codecs, optparse, os

optparser = optparse.OptionParser()
optparser.add_option("-c", "--unigramcounts", dest='counts1w', default=os.path.join('data', 'count_1w.txt'), help="unigram counts")
optparser.add_option("-b", "--bigramcounts", dest='counts2w', default=os.path.join('data', 'count_2w.txt'), help="bigram counts")
optparser.add_option("-m", "--markcounts", dest='countsmark', default=os.path.join('data', 'count_mark.txt'), help="mark_counts")
optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'input'), help="input file to segment")
(opts, _) = optparser.parse_args()

from Entry import Entry
from Pdist1w import Pdist1w
from Pdist2w import Pdist2w
from math import log

old = sys.stdout
sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout)

P1w = Pdist1w(opts.counts1w, singleCharIgnore = 7)
P2w = Pdist2w(opts.counts2w)
Pm = Pdist1w(opts.countsmark)
sumN = P1w.N + P2w.N + Pm.N
P1w.N = P2w.N = Pm.N = sumN

with open(opts.input) as f:
    for line in f:
        utf8line = unicode(line.strip(), 'utf-8')
        entryList = []
        for index in range(len(utf8line)):
            maxSum = float('-Inf')
            maxEnt = 0
            maxWord = None
            inDict = False
#Do the bygram match
            """
            headEntry = index - P1w.maxlen
            if (headEntry < 0):
                headEntry = 0
            for i in range(headEntry, index + 1):
                if (i == 0):
                    preLogP = 0
                    isHead = True
                else:
                    preLogP = entryList[i - 1].logP
                    isHead = False
                thisP = P2w(utf8line[i:index+1], isHead)
                if (thisP is None):
                    thisLogP = float('-Inf')
                else:
                    thisLogP = log(thisP["p"])
                if (thisLogP + preLogP > maxSum):
                    maxSum = thisLogP + preLogP
                    maxEnt = i - 1
                    maxWord = thisP["word"]
                    inDict = True
"""
#Do the unigram match
            if (inDict is False):
                headEntry = index - P2w.maxlen
                if (headEntry < 0):
                    headEntry = 0
                for i in range(headEntry, index + 1):
                    if (i == 0):
                        preLogP = 0
                    else:
                        preLogP = entryList[i - 1].logP
                    thisP = P1w(utf8line[i:index+1])
                    if (thisP is None):
                        thisLogP = float('-Inf')
                    else:
                        thisLogP = log(thisP)
                    if (thisLogP + preLogP > maxSum):
                        maxSum = thisLogP + preLogP
                        maxEnt = i - 1
                        maxWord = utf8line[maxEnt + 1:index + 1] 
                        inDict = True

#Do the markgram match
            if (inDict is False):
                headEntry = index - Pm.maxlen
                if (headEntry < 0):
                    headEntry = 0
                for i in range(headEntry, index + 1):
                    if (i == 0):
                        preLogP = 0
                    else:
                        preLogP = entryList[i - 1].logP
                    thisP = Pm(utf8line[i:index+1])
                    if (thisP is None):
                        thisLogP = float('-Inf')
                    else:
                        thisLogP = log(thisP)
                    if (thisLogP + preLogP > maxSum):
                        maxSum = thisLogP + preLogP
                        maxEnt = i - 1
                        maxWord = utf8line[maxEnt + 1:index + 1] 
                        inDict = True

#Connect the characters that are not in the dictionarys together
            if (inDict is False):
                maxEnt = -1
                maxWord = utf8line[:index + 1]
                maxSum = len(maxWord) * log(1./sumN)
                for i in xrange(index - 1, -1, -1):
                    if (entryList[i].inDict):
                        maxEnt = i
                        maxWord = utf8line[i + 1:index + 1]
                        maxSum = entryList[i].logP + len(maxWord) * log(1./sumN)
                        break

            if (maxEnt >= 0):
                entryList.append(Entry(maxWord, maxSum, entryList[maxEnt], inDict))
            else:
                entryList.append(Entry(maxWord, maxSum, None, inDict))
        print Entry.rollback(entryList[len(utf8line) - 1])
sys.stdout = old
