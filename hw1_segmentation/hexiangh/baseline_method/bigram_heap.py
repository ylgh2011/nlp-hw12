# Import system package
from math import log
from heapq import heappush, heappop
import sys, codecs, optparse, os
import operator

# Import customized package
from data_struct import Entry, Pdist

optparser = optparse.OptionParser()
optparser.add_option("-c", "--unigramcounts", dest='counts1w', default=os.path.join('data', 'count_1w.txt'), help="unigram counts")
optparser.add_option("-b", "--bigramcounts", dest='counts2w', default=os.path.join('data', 'count_2w.txt'), help="bigram counts")
optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'input'), help="input file to segment")
(opts, _) = optparser.parse_args()

def print_chart(chart):
    for key, val in chart.items():
        if val:
            print "Chart[",key,"]: ",val.word, " prob: ", val.log_prob


def main():
    unigram = Pdist(opts.counts1w)
    bigram = Pdist(opts.counts2w)

    # substitute output
    old_output = sys.stdout
    sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout)

    heap = list()
    chart = dict()
    with open(opts.input) as f:
        cnt = 0
        maxlen = max(unigram.maxlen, bigram.maxlen)
        for line in f:
            chart = dict()
            input_text = unicode(line.strip(), 'utf-8')

            cnt += 1
            for i in range(maxlen):
                word = input_text[:i]
                if bigram(word):
                    heappush(heap, Entry(word, 0, log(bigram(word)), None))
                elif unigram(word):
                    heappush(heap, Entry(word, 0, log(unigram(word)), None))

            while heap:
                entry = heappop(heap)
                end_index = entry.start_pos + len(entry.word) - 1
                if chart.get(end_index):
                    if entry.log_prob > chart[end_index].log_prob:
                        chart[end_index] = entry
                    else:
                        continue
                else:
                    chart[end_index] = entry

                for i in range(maxlen):
                    new_word = input_text[end_index + 1: end_index + 1 + i]
                    if bigram(new_word):
                        new_log_prob = entry.log_prob + log(bigram(new_word))
                        new_entry = Entry(new_word, end_index + 1, new_log_prob, entry)
                        heappush(heap, new_entry)
                    elif unigram(new_word):
                        new_log_prob = entry.log_prob + log(unigram(new_word))
                        new_entry = Entry(new_word, end_index + 1, new_log_prob, entry)
                        heappush(heap, new_entry)
                    elif len(heap) == 0:
                        new_log_prob = entry.log_prob
                        new_entry = Entry(new_word, end_index + 1, new_log_prob, entry)
                        heappush(heap, new_entry)
                        
            # print_chart(chart)
            print chart[(len(input_text)) - 1].reverse()


    sys.stdout = old_output



if __name__ == '__main__':
    main()
