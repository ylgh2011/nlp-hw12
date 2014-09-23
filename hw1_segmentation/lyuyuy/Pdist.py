#the class for doing the dictionary operations for unigram.
class Pdist(dict):
    "A probability distribution estimated from counts in datafile."

    def __init__(self, filename, sep='\t', N=None, singleCharIgnore=0, doubleCharIgnore=0, firstWordOnly=False):
        self.maxlen = 0 
        for line in file(filename):
            (key, freq) = line.split(sep)
            try:
                utf8key = unicode(key, 'utf-8')
            except:
                raise ValueError("Unexpected error %s" % (sys.exc_info()[0]))
            if firstWordOnly:
                utf8key = utf8key.split(' ')[0]
            self[utf8key] = self.get(utf8key, 0) + int(freq)
            self.maxlen = max(len(utf8key), self.maxlen)
        self.N = float(N or sum(self.itervalues()))
#Add a new argument to ignore the single characters that appear too few
        self.singleCharIgnore = singleCharIgnore
        self.doubleCharIgnore = doubleCharIgnore

    def __call__(self, key):
        if key in self:
            if (len(key) == 1) and (self[key] <= self.singleCharIgnore):
                return None
            if (len(key) == 2) and (self[key] <= self.doubleCharIgnore):
                return None
            return float(self[key]) / float(self.N)
        # elif len(key) == 1:
        #     return 1.0 / float(self.N)
        else: 
            return None

    def getCount(self, key):
        if key in self:
            return self[key]
        else:
            return 0

    @staticmethod
    def isNumber(c):
        lst = ['\xef\xbc\x90', '\xef\xbc\x91', '\xef\xbc\x92', '\xef\xbc\x93', '\xef\xbc\x94', '\xef\xbc\x95', '\xef\xbc\x96', '\xef\xbc\x97', '\xef\xbc\x98', '\xef\xbc\x99', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        for item in lst:
            if item.decode('utf-8') == c.decode('utf-8'):
                return True
        return False

    @staticmethod
    def isUnitNumber(c):
        lst = ['\xe5\xb9\xb4', '\xe5\xb9\xb4', '\xe6\x9c\x88', '\xe6\x97\xa5', '\xe7\x99\xbe', '\xe5\x8d\x83', '\xe4\xb8\x87', '\xe5\xa4\x9a']
        for item in lst:
            if item.decode('utf-8') == c.decode('utf-8'):
                return True
        return False

    @staticmethod
    def isDot(c):
        lst = ['\xef\xbc\x8e', '\xc2\xb7', '.']
        for item in lst:
            if item.decode('utf-8') == c.decode('utf-8'):
                return True
        return False


