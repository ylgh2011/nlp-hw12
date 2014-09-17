#The is the main program to run
import sys, codecs, optparse, os

optparser = optparse.OptionParser()
optparser.add_option("-c", "--unigramcounts", dest='counts1w', default=os.path.join('data', 'count_1w.txt'), help="unigram counts")
optparser.add_option("-b", "--bigramcounts", dest='counts2w', default=os.path.join('data', 'count_2w.txt'), help="bigram counts")
optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'input'), help="input file to segment")
(opts, _) = optparser.parse_args()

from Entry import Entry
from Pdist import Pdist
from math import log

P1w  = Pdist(opts.counts1w)

old = sys.stdout
sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout)
# ignoring the dictionary provided in opts.counts
with open(opts.input) as f:
    for line in f:
        utf8line = unicode(line.strip(), 'utf-8')
        entryList = []
        for index in range(len(utf8line)):
            headEntry = index - P1w.maxlen
            if (headEntry < 0):
                headEntry = 0
            maxSum = float('-Inf')
            maxEnt = 0
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
            if (maxEnt >= 0):
                entryList.append(Entry(utf8line[maxEnt + 1:index + 1], maxSum, entryList[maxEnt]))
            else:
                entryList.append(Entry(utf8line[:index + 1], maxSum, None))
        print Entry.rollback(entryList[len(utf8line) - 1])
sys.stdout = old
