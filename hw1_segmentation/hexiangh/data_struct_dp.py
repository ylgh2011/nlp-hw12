import sys, codecs, optparse, os
import operator

class bPdist(dict):
    "The distribution function over given algorithm"

    def __init__(self, bigram,sep = '\t', N = None, missingfn = None):
        self.maxlen = 0
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
            self[utf8cond][utf8key] = self[utf8cond].get(utf8key, 0) + float(freq)
            self.maxlen = max(len(utf8key), len(utf8cond), self.maxlen)

        # probability smoothing 
#        for vals in self.values():
#            vals_cnt = len(vals)
#            penaulty = 0.1 / vals_cnt
#            for key in vals.keys():
#                vals[key] = vals[key] - penaulty

#            vals.update({'Unknown':0.1})

        
        # self.N = float(N or sum([i for vals in self.values() for i in vals.values()]))
        self.missingfn = missingfn or (lambda k, N: 1./N)

    def __call__(self, cond, key):
        # Return bigram possibility
        if cond in self.keys():
            if key in self[cond].keys():
                return float(self[cond][key])/float(sum(self[cond].values()))
#            elif len(key) == 1:
#                return float(self[cond]['Unknown'])/float(sum(self[cond].values()))
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


class uPdist(dict):
    # Distribution for unigram alone
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
    def __init__(self, word, log_prob, prev = None, in_dict = False, is_digit = False, is_unit = False):
        self.word = word
        self.prev = prev
        self.log_prob = log_prob
        self.in_dict = in_dict


    def __lt__(self, other):
        return self.start_pos < other.start_pos

    def reverse(self):
        out_list = []
        en = self
        while en:
            out_list.insert(0, en.word)
            en = en.prev
        return " ".join(out_list)
