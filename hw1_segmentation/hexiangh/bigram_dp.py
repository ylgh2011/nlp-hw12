from math import log
from heapq import heappush, heappop
import sys, codecs, optparse, os
import operator

from data_struct_dp import Entry, uPdist, bPdist


optparser = optparse.OptionParser()
optparser.add_option("-c", "--unigramcounts", dest='counts1w', default=os.path.join('data', 'count_1w.txt'), help="unigram counts")
optparser.add_option("-b", "--bigramcounts", dest='counts2w', default=os.path.join('data', 'count_2w.txt'), help="bigram counts")
optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'input'), help="input file to segment")
(opts, _) = optparser.parse_args()


def main():
    bDist = bPdist(opts.counts2w)
    uDist = uPdist(opts.counts1w)

    # substitute output
    old_output = sys.stdout
    sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout)

    entry_list = list()
    opt = dict()
    with open(opts.input) as f:
        # eventually opt(n) = opt(n - r) + r for r belongs to (n - l, n) that unigram(r) == max
        # initially opt(r) = r for r belongs to (0, l)
        cnt = 0
        for line in f:
            opt = dict()
            sentence = unicode(line.strip(), 'utf-8')
            # initialization
            for i in range(len(sentence) - 1):
                opt[i] = None

            for end_pos in range(len(sentence)):
                start_pos = max(0, end_pos - bDist.maxlen)
                opt_start = 0
                opt_prob = - 9999999999
                for alt_start in range(start_pos, end_pos + 1):

                    # calc last dp table entry index
                    word = sentence[alt_start:end_pos + 1]
                    last_end = alt_start

                    # fetch previous entry
                    if last_end == 0:
                        pre_word = '<S>'
                        pre_prob = 0
                    elif opt[last_end]:
                        pre_word = opt[last_end].word
                        pre_prob = opt[last_end].log_prob

                    # First try to match bigram, if failed, try match unigram
                    if bDist(pre_word, word):
                        prob = log(bDist(pre_word, word))
                    else:
                        if uDist(word):
                            prob = log(uDist(word) * 0.001)
                        else:
                            prob = - 9999999999


                    # print debug information
                    # print end_pos, "/", len(sentence), ",", word, ",", last_end, ", ", prob
                    # print word,", ",alt_start,"-",end_pos + 1,", ",prob, ", last end:", last_end

                    if prob + pre_prob > opt_prob:
                        opt_start = alt_start
                        opt_prob = prob + pre_prob

                    # print word, "|", pre_word , ",",alt_start,"-",end_pos + 1,", ",prob, ", last end:", last_end, "opt end:", opt_start, "opt prob:", opt_prob


                # print "chart[",end_pos + 1,"] ",opt_start,"-", end_pos + 1,":", sentence[opt_start:end_pos + 1], ", ", opt_prob, ", prev :", opt_start
                opt[end_pos + 1] = Entry(sentence[opt_start:end_pos + 1], opt_prob, opt[opt_start])

#            for key, val in opt.items():
#                if val:
#                    print "key: ",key,", val:",val.word
#
            print opt[len(sentence)].reverse()

    sys.stdout = old_output



if __name__ == '__main__':
    main()
