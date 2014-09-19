import sys, codecs, optparse, os
import operator

class Pdist(dict):
    "The distribution function over given algorithm"

    def __init__(self, bigram, penalty = 0.2, sep = '\t', N = None, missingfn = None):
        self.maxlen = 0
        self.penalty = penalty
        # Model example { "key_1":{ "key_2": 1, "key_3": 2}}
        # Construct unigram probability distribution
        for line in file(bigram):
            sub_sep = ' '
            (keys, freq) = line.split(sep)
            (cond, key) = keys.split(sub_sep)
            try:
                utf8cond = unicode(cond, 'utf-8')
                utf8key = unicode(key, 'utf-8')
            except:
                raise ValueError(("Unexpected error %s") % (sys.exc_info()[0]))

            # if this entry is not created, create it
            if self.get(utf8cond, None) is None:
                self[utf8cond] = dict()
            self[utf8cond][utf8key] = self[utf8cond].get(utf8key, 0) + float(freq) #- penalty
            self.maxlen = max(len(utf8key), len(utf8cond), self.maxlen)

        # for val in self.values():
            


        self.N = float(N or sum([i for vals in self.values() for i in vals.values()]))
        self.missingfn = missingfn or (lambda k, N: 1./N)

    def __call__(self, cond, key = None):
        if key:
            # Return bigram possibility
            if cond in self.keys():
                if key in self[cond]:
                    return float(self[cond][key])/float(self.N)
            else:
                return None

            pass
        else:
            # Return unigram possibility
            if cond in self.keys():
                return float(sum(x for x in self[cond].values()))/float(self.N)
            elif len(cond) == 1:
                return self.missingfn(cond, self.N)
            else:
                return None

    def show(self):
        outstr = ""
        for (key, vals) in self.items():
            outstr = outstr + "{ "+  key + ": ["
            for (subkey, subval) in vals.items():
                outstr = outstr + subkey + " : " + str(subval) + " "
            outstr = outstr + "] = " + str(sum(x for x in vals.values()))+ " }\n"
        return outstr

""" Distribution for unigram alone
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
"""

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
