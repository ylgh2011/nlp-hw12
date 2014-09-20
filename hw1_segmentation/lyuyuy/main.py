#The is the main program to run
import sys, codecs, optparse, os

optparser = optparse.OptionParser()
optparser.add_option("-c", "--unigramcounts", dest='counts1w', default=os.path.join('data', 'count_1w.txt'), help="unigram counts")
optparser.add_option("-b", "--bigramcounts", dest='counts2w', default=os.path.join('data', 'count_2w.txt'), help="bigram counts")
optparser.add_option("-m", "--markcounts", dest='countsmark', default=os.path.join('data', 'count_mark.txt'), help="mark_counts")
optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'input'), help="input file to segment")
(opts, _) = optparser.parse_args()

from Entry import Entry
from Pdist import Pdist
from math import log

old = sys.stdout
sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout)

# P1w = Pdist(filename = opts.counts1w, singleCharIgnore = int(sys.argv[1]), doubleCharIgnore = int(sys.argv[2]))
P1w = Pdist(filename = opts.counts1w, singleCharIgnore = 36, doubleCharIgnore = 0)
P2w = Pdist(filename = opts.counts2w)
P2wFirstWordOnly = Pdist(filename = opts.counts2w, firstWordOnly = True)

# Pm = Pdist(opts.countsmark)
# sumN = P1w.N + P2w.N + Pm.N
# P1w.N = P2w.N = Pm.N = sumN

with open(opts.input) as f:
    for line in f:
        utf8line = unicode(line.strip(), 'utf-8')
        entryList = []
        for index in range(len(utf8line)):
            maxSum = float('-Inf')
            maxEnt = -1
            maxWord = None

            inDict = False
            isNum = False
            isCharNum = False

#Do the gram match
            if inDict is False:
                headEntry = index - max(P1w.maxlen, P2w.maxlen)
                if (headEntry < 0):
                    headEntry = 0
                for i in range(headEntry, index + 1):
                    wordA = '' if i == 0 else entryList[i - 1].word
                    wordB = utf8line[i:index+1]

# ***AB: P(B | A) = P(A, B) / P(A)
                    P_AB = P2w(wordA + ' ' + wordB) # P(A, B)
                    P_A = P1w(wordA)                # P(B)
                    if P_AB is not None:
                        log_P_B_base_A = log(P_AB) - (log(P_A) if P_A is not None else 0)
                        # countA = P2wFirstWordOnly.getCount(wordA)
                        # countAB = P2w.getCount(wordA + ' ' + wordB)
                        # log_P_B_base_A = log(float(countAB) / float(countA)) if P_A is not None else 0
                    else:
                        p1_wordB = P1w(wordB)
                        log_P_B_base_A = log(p1_wordB) if p1_wordB is not None else float('-Inf')

                    thisLogP = log_P_B_base_A
                    preLogP  = 0 if i == 0 else entryList[i - 1].logP

                    if (thisLogP + preLogP >= maxSum) or (maxSum == float('-Inf')):
                        maxSum = thisLogP + preLogP
                        maxEnt = i - 1
                        maxWord = utf8line[maxEnt + 1:index + 1]
                    if (P1w(wordB) is not None) or (P2w(wordA + ' ' + wordB) is not None):
                        inDict = True

#Connect the characters that are not in the dictionaries
            if inDict is False:
                maxEnt = -1
                maxWord = utf8line[:index + 1]
                maxSum = len(maxWord) * log(1.0/P1w.N)
                for i in range(index - 1, -1, -1):
                    if entryList[i].inDict:
                        maxEnt = i
                        maxWord = utf8line[i + 1:index + 1]
                        maxSum = entryList[i].logP + len(maxWord) * log(1.0/P1w.N)
                        break

#Connect consecutive numbers
            index_char = utf8line[index].encode('utf-8')
            isNum = Pdist.isNumber(index_char)
            isCharNum = Pdist.isCharNumber(index_char)
            isDot = Pdist.isDot(index_char)
            if isNum or (isCharNum and (not inDict)) or isDot:
                if isDot and (not inDict):
                    isNum = True
                if isNum:
                    inDict = True if not isDot else inDict
                maxEnt = -1
                maxWord = utf8line[:index + 1]
                maxSum = len(maxWord) * log(1.0/P1w.N)
                for i in range(index - 1, -1, -1):
                    if not entryList[i].isNum:
                        maxEnt = i
                        maxWord = utf8line[i + 1:index + 1]
                        maxSum = entryList[i].logP + len(maxWord) * log(1.0/P1w.N)
                        break



            if maxEnt >= 0:
                entryList.append(Entry(maxWord, maxSum, entryList[maxEnt], inDict, isNum, isCharNum))
            else:
                entryList.append(Entry(maxWord, maxSum, None, inDict, isNum, isCharNum))

        print Entry.rollback(entryList[len(utf8line) - 1])

        # for item in entryList:
        #     print item.__str__(),
        # print

sys.stdout = old
