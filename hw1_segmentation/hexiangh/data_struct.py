import sys, codecs, optparse, os
import operator

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
    def __init__(self, word, start_pos, log_prob, prev):
        self.word = word
        self.prev = prev
        self.log_prob = log_prob
        self.start_pos = start_pos

    def __lt__(self, other):
        return self.start_pos < other.start_pos

    def reverse(self):
        out_list = []
        en = self
        while en:
            out_list.insert(0, en.word)
            en = en.prev
        return " ".join(out_list)
