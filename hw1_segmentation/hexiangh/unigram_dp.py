from math import log
from heapq import heappush, heappop
import sys, codecs, optparse, os
import operator

optparser = optparse.OptionParser()
optparser.add_option("-c", "--unigramcounts", dest='counts1w', default=os.path.join('data', 'count_1w.txt'), help="unigram counts")
optparser.add_option("-b", "--bigramcounts", dest='counts2w', default=os.path.join('data', 'count_2w.txt'), help="bigram counts")
optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'input'), help="input file to segment")
(opts, _) = optparser.parse_args()

class Pdist(dict):
    "The distribution function over given algorithm"

    def __init__(self, filename, sep = '\t', N = None, missingfn = None):
        self.maxlen = 0
        for line in file(filename):
            (key, freq) = line.split(sep)
            try:
                utf8key = unicode(key, 'utf-8')
            except:
                raise ValueError(("Unexpected error %s") % (sys.exc_info()[0]))
            self[utf8key] = self.get(utf8key, 0) + int(freq)
            self.maxlen = max(len(utf8key), self.maxlen)
        self.N = float(N or sum(self.itervalues()))
        self.missingfn = missingfn or (lambda k, N: 1./N)

    def __call__(self, key):
        if key in self:
            return float(self[key])/float(self.N)
        elif len(key) == 1:
            return self.missingfn(key, self.N)
        else:
            return None

class Entry:
    def __init__(self, word, log_prob, prev = None):
        self.word = word
        self.prev = prev
        self.log_prob = log_prob


    def __lt__(self, other):
        return self.start_pos < other.start_pos

    def reverse(self):
        out_list = []
        en = self
        while en:
            out_list.insert(0, en.word)
            en = en.prev
        return " ".join(out_list)


def main():
    unigram = Pdist(opts.counts1w)

    # substitute output
    old_output = sys.stdout
    sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout)

    entry_list = list()
    opt = dict()
    with open(opts.input) as f:
        # eventually opt(n) = opt(n - r) + r for r belongs to (n - l, n) that unigram(r) == max
        # initially opt(r) = r for r belongs to (0, l)
        cnt = 0
        for line in f:
            opt = dict()
            sentence = unicode(line.strip(), 'utf-8')
            # initialization
            for i in range(len(sentence) - 1):
                opt[i] = None

            for end_pos in range(len(sentence)):
                start_pos = max(0, end_pos - unigram.maxlen)
                opt_start = 0
                opt_prob = - 9999999999
                for alt_start in range(start_pos, end_pos + 1):
                    word = sentence[alt_start:end_pos + 1]
                    # Get word probability
                    if unigram(word):
                        prob = log(unigram(word))
                    else:
                        prob = - 9999999999
                    
                    # calc last dp table entry index
                    last_end = max(alt_start, 0)
                    # Print debug information
                    # print end_pos, "/", len(sentence), ",", word, ",", last_end, ", ", prob
                    # print word,", ",alt_start,"-",end_pos + 1,", ",prob, ", last end:", last_end
                    if opt[last_end]:
                        prob = opt[last_end].log_prob + prob
                        # print word, ",", prob

                    if prob > opt_prob:
                        opt_start = alt_start
                        opt_prob = prob

                    # print word,", ",alt_start,"-",end_pos + 1,", ",prob, ", last end:", last_end, "opt end:", opt_start, "opt prob:", opt_prob


                # print "chart[",end_pos + 1,"] ",opt_start,"-", end_pos + 1,":", sentence[opt_start:end_pos + 1], ", ", opt_prob, ", prev :", opt_start
                opt[end_pos + 1] = Entry(sentence[opt_start:end_pos + 1], opt_prob, opt[opt_start])

#            for key, val in opt.items():
#                if val:
#                    print "key: ",key,", val:",val.word
#
            print opt[len(sentence)].reverse()

    sys.stdout = old_output



if __name__ == '__main__':
    main()
