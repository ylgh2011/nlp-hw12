from math import log
from heapq import heappush, heappop
import sys, codecs, optparse, os
import operator

from data_struct_dp import Entry,bPdist


optparser = optparse.OptionParser()
optparser.add_option("-c", "--unigramcounts", dest='counts1w', default=os.path.join('data', 'count_1w.txt'), help="unigram counts")
optparser.add_option("-b", "--bigramcounts", dest='counts2w', default=os.path.join('data', 'count_2w.txt'), help="bigram counts")
optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'input'), help="input file to segment")
(opts, _) = optparser.parse_args()

class Pwdist(dict):
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

def main():
    bigram_dict = bPdist(opts.counts2w)
    unigram_dict = Pwdist(opts.counts1w)

    # substitute output
    old_output = sys.stdout
    sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout)

    print "--------------+----------------"

    print bigram_dict.show()

    sys.stdout = old_output



if __name__ == '__main__':
    main()
