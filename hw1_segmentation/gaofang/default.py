
import sys, codecs, optparse, os
import collections, math, heapq

optparser = optparse.OptionParser()
optparser.add_option("-c", "--unigramcounts", dest='counts1w', default=os.path.join('data', 'count_1w.txt'), help="unigram counts")
optparser.add_option("-b", "--bigramcounts", dest='counts2w', default=os.path.join('data', 'count_2w.txt'), help="bigram counts")
optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'input'), help="input file to segment")
(opts, _) = optparser.parse_args()
Entry = collections.namedtuple('entry', 'word  start prob back')

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

    def get_length(self):
        return self.maxlen

# the default segmenter does not use any probabilities, but you could ...

def print_result(entry):
    outString = " "
    while entry.back:
        if len(entry.word) == 1 and len(entry.back.word) ==1:
            
            outString = entry.word + outString
        else: 
            outString = " " + entry.word + outString
        entry = entry.back
    outString = entry.word + outString
    print outString

Pw  = Pdist(opts.counts1w)
old = sys.stdout
sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout)
# ignoring the dictionary provided in opts.counts
with open(opts.input) as f:
    for line in f:
        chart = {}
        heap = []
        utf8line = unicode(line.strip(), 'utf-8')
        for length in range(min(Pw.get_length(), len(utf8line))):
            if Pw(utf8line[0:length]) is not None:
                entry = Entry(word=utf8line[0:length], start=0, prob=math.log(Pw(utf8line[0:length])), back=None)
                heapq.heappush(heap, (entry.start, entry))
        while heap:
            entry = heapq.heappop(heap)[1]
            endindex = entry.start + len(entry.word) - 1

            if endindex in chart:
                if entry.prob > chart[endindex].prob:
                    chart[endindex] = entry
                else:
                    continue
            else:
                chart[endindex] = entry
            for length in range(min(Pw.get_length(), len(utf8line[endindex:]))):
                if Pw(utf8line[endindex + 1:endindex + length + 1]) is not None:
                    newentry = Entry(word=utf8line[endindex + 1:endindex + length +1], start=endindex + 1, prob=(entry.prob + math.log(Pw(utf8line[endindex + 1:endindex + length + 1]))), back=entry)
                    if newentry not in heap:
                        heapq.heappush(heap, (newentry.start, newentry))

        finalindex = len(utf8line) - 1
        finalentry = chart[finalindex]
        print_result(finalentry)

sys.stdout = old

