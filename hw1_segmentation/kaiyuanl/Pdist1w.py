#the class for doing the dictionary operations for unigram.
class Pdist1w(dict):
    "A probability distribution estimated from counts in datafile."

    def __init__(self, filename, sep='\t', N=None, singleCharIgnore = 0):
        self.maxlen = 0 
        for line in file(filename):
            (key, freq) = line.split(sep)
            try:
                utf8key = unicode(key, 'utf-8')
            except:
                raise ValueError("Unexpected error %s" % (sys.exc_info()[0]))
            self[utf8key] = self.get(utf8key, 0) + int(freq)
            self.maxlen = max(len(utf8key), self.maxlen)
        self.N = float(N or sum(self.itervalues()))
#Add a new argument to ignore the single characters that appear too few
        self.singleCharIgnore = singleCharIgnore

    def __call__(self, key):
        if key in self:
            if ((len(key) > 1) or (self[key] > self.singleCharIgnore) ):
                return float(self[key])/float(self.N)
        #else: return self.missingfn(key, self.N)
        else: return None
