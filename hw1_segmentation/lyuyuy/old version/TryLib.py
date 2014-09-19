from math import log
from heapq import heappush
from heapq import heappop

class Pdist(dict):
    "A probability distribution estimated from counts in datafile."

    def __init__(self, filename, sep='\t', N=None, missingfn=None):
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
        self.missingfn = missingfn or (lambda k, N: 1./N)

    def __call__(self, key):
        if key in self: return float(self[key])/float(self.N)
        #else: return self.missingfn(key, self.N)
        elif len(key) == 1: return self.missingfn(key, self.N)
        else: return None


class Entry:
    def __init__(self, word, start_pos, log_prob, back_p):
        self.word = word
        self.start_pos = start_pos
        self.log_prob = log_prob
        self.back_p = back_p

    def __str__(self):
        return "{word: " + self.word + ", start_pos: " + str(self.start_pos) + ", log_prob: " + str(self.log_prob) + "}"

    def __lt__(self, other):
        if self.start_pos == other.start_pos:
            return len(self.word) < len(other.word)
        return self.start_pos < other.start_pos



def updateHeap(heap, startingIndex, input_str, Pw, curEntryLogProb, curEntry):
    if startingIndex >= len(input_str):
        return

    for i in range(Pw.maxlen):
        currentStr = input_str[startingIndex : startingIndex + i + 1]
        if currentStr in Pw:
            # print currentStr
            heappush(heap, Entry(currentStr, startingIndex, curEntryLogProb + log(float(Pw[currentStr])/Pw.N, 2), curEntry))
    if heap == []:
        heappush(heap, Entry(input_str[startingIndex], startingIndex, curEntryLogProb + log(1.0/Pw.N, 2), curEntry))



def heapString(heap):
    ans = '['
    for item in heap:
        ans += item.__str__() + ', '
    return ans+']'



