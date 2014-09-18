import sys, codecs, optparse, os
from heapq import heappush
from heapq import heappop

from TryLib import Pdist
from TryLib import Entry
from TryLib import updateHeap
from TryLib import heapString

def main():
    optparser = optparse.OptionParser()
    optparser.add_option("-c", "--unigramcounts", dest='counts1w', default=os.path.join('data', 'count_1w.txt'), help="unigram counts")
    optparser.add_option("-b", "--bigramcounts", dest='counts2w', default=os.path.join('data', 'count_2w.txt'), help="bigram counts")
    optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'input'), help="input file to segment")
    (opts, _) = optparser.parse_args()

    Pw = Pdist(opts.counts1w)
    input_str = unicode(file(opts.input).read(), 'utf-8')

    heap = []
    chart = {}
    updateHeap(heap, 0, input_str, Pw, 0, None)

    while heap:
        curEntry = heappop(heap)
        endIndex = curEntry.start_pos + len(curEntry.word) - 1
        if endIndex in chart:
            preEntry = chart[endIndex]
            if preEntry.log_prob < curEntry.log_prob:
                chart[endIndex] = curEntry
            else:
                if heap == []:
                    updateHeap(heap, endIndex+1, input_str, Pw, preEntry.log_prob, preEntry)
                continue
        else:
            chart[endIndex] = curEntry

        updateHeap(heap, endIndex+1, input_str, Pw, curEntry.log_prob, curEntry)

    curEntry = chart[len(input_str) - 1]
    ans = []

    while curEntry is not None:
        ans.append(curEntry.word)
        curEntry = curEntry.back_p

    sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout)
    print ' '.join(reversed(ans)),

if __name__ == '__main__':
    main()


