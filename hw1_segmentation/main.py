#The is the main program to run
import sys, codecs, optparse, os

optparser = optparse.OptionParser()
optparser.add_option("-c", "--unigramcounts", dest='counts1w', default=os.path.join('data', 'count_1w.txt'), help="unigram counts")
optparser.add_option("-b", "--bigramcounts", dest='counts2w', default=os.path.join('data', 'count_2w.txt'), help="bigram counts")
optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'input'), help="input file to segment")
(opts, _) = optparser.parse_args()

from Entry import Entry
from Pdist1w import Pdist1w
from Pdist2w import Pdist2w
from math import log

old = sys.stdout
sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout)

P1w = Pdist1w(opts.counts1w)
P2w = Pdist2w(opts.counts2w)

with open(opts.input) as f:
    for line in f:
        utf8line = unicode(line.strip(), 'utf-8')
        entryList = []
        for index in range(len(utf8line)):
            headEntry = index - max(P1w.maxlen, P2w.maxlen)
            if (headEntry < 0):
                headEntry = 0
            maxSum = float('-Inf')
            maxEnt = 0
            maxWord = None
#Do the bygram match
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

#Do the unigram match
            if (maxWord is None):
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

            if (maxEnt >= 0):
                entryList.append(Entry(maxWord, maxSum, entryList[maxEnt]))
            else:
                entryList.append(Entry(maxWord, maxSum, None))
        print Entry.rollback(entryList[len(utf8line) - 1])
sys.stdout = old
