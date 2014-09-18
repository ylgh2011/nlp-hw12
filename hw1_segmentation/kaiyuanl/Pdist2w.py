#the class for doing the dictionary operations for bygram.
class Pdist2w(dict):
    "A probability distribution estimated from counts in datafile."

    def __init__(self, filename, sep='\t', N=None):
        self.maxlen = 0
        self.N = 0
        for line in file(filename):
            (key, freq) = line.split(sep)
            try:
                utf8word = unicode(key, 'utf-8')
            except:
                raise ValueError("Unexpected error %s" % (sys.exc_info()[0]))
            isHead = False
#Special check: is the word at head
            if (utf8word.find(unicode("<S> ", 'utf-8')) >= 0):
                utf8word = utf8word.replace(unicode("<S> ", 'utf-8'), '')
                isHead = True
            utf8key = utf8word.replace(unicode(" ", 'utf-8'), '')
            self[utf8key] = {"freq": self.get(utf8key, {"freq": 0})["freq"] + int(freq), "word": utf8word, "head": isHead}
            self.maxlen = max(len(utf8key), self.maxlen)
            self.N += int(freq)
        self.N = float(N or self.N)

    def __call__(self, key, isHead):
        if (key in self) and (isHead == self[key]["head"]):
            return {"p": float(self[key]["freq"])/float(self.N), "word": self[key]["word"]}
        else: return None
