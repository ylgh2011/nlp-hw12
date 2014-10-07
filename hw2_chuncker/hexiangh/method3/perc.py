
import gzip # use compressed data files
import copy, operator, optparse, sys, os

# read the valid output tags for the task
def read_tagset(tagsetfile):
    tagset = []
    for line in open(tagsetfile, 'r'):
        line = line.strip()
        tagset.append(line)
    return tagset

# for each train/test example, read the set of features 
# used for determining the output label
def read_labeled_data(labelfile, featfile):
    labeled_data = []
    lab = gzip.open(labelfile, 'r') if labelfile[-3:] == '.gz' \
        else open(labelfile, 'r')
    feat = gzip.open(featfile, 'r') if featfile[-3:] == '.gz' \
        else open(featfile, 'r')
    while True:
        labeled_list = []
        feat_list = []
        lab_w = ''
        feat_line = ''
        while True:
            lab_w = lab.readline().strip()
            if lab_w == '\n': break
            if lab_w == '': break
            lab_w = lab_w.strip()
            labeled_list.append(lab_w)
        while True:
            feat_line = feat.readline().strip()
            if feat_line == '\n': break
            if feat_line == '': break
            (feat_keyword, feat_w) = feat_line.split() # throw away the FEAT keyword
            feat_w = feat_w.strip()
            feat_list.append(feat_w)
            if feat_w == 'B': feat_list.append('T')
        if len(labeled_list) == 0:
        #if lab_w == '': 
        #    if feat_line != '': 
            if len(feat_list) != 0:
                print >>sys.stderr, "files do not align"
                print >>sys.stderr, lab_w, feat_line
            break
        else:
            labeled_data.append( (labeled_list, feat_list) )
            # data format (['Rockwell NNP','International NNP',...],['U00:_B-2','U01:_B-1','U02:Rockwell',...] )
    lab.close()
    feat.close()
    return labeled_data

def feats_for_word(start_index, feat_list):
    # iterate feature list for a word, and increase the feature index
    feats = []
    endstate = None
    end_index = start_index
    for i in range(start_index, len(feat_list)):
        # iterate the feature list
        feat_value = feat_list[i]
        # check if we reached the feats for the next word
        if feat_value[:4] == endstate:
            end_index = i
            # set up the end_index to the current exit index
            break
        feats.append(feat_value)
        # normally append the feature states
        if endstate is None: 
            endstate = feat_value[:4] 
            # set endstate to 'U00:', so that everytime this function will only iterate 1 feature history
    return (end_index, feats)

def get_maxvalue(viterbi_dict):
    maxvalue = (None, None) # maxvalue has tuple (tag, value)
    for tag in viterbi_dict.keys():
        value = viterbi_dict[tag] # value is (score, backpointer)
        if maxvalue[1] is None:
            maxvalue = (tag, value[0])
        elif maxvalue[1] < value[0]:
            maxvalue = (tag, value[0])
        else:
            pass # no change to maxvalue
    if maxvalue[1] is None:
        raise ValueError("max value tag for this word is None")
    return maxvalue

def perc_test(feat_vec, labeled_list, feat_list, tagset, default_tag):
    # feature vector is the training result, default_tag is NP
    output = []
    labels = copy.deepcopy(labeled_list)
    # add in the start and end buffers for the context
    labels.insert(0, '_B-1 _B-1 _B-1')
    labels.insert(0, '_B-2 _B-2 _B-2') # first two 'words' are B_-2 B_-1
    labels.append('_B+1 _B+1 _B+1')
    labels.append('_B+2 _B+2 _B+2') # last two 'words' are B_+1 B_+2

    # size of the viterbi data structure
    N = len(labels)

    # Set up the data structure for viterbi search
    viterbi = {}
    for i in range(0, N):
        viterbi[i] = {} 
        # each column contains for each tag: a (value, backpointer) tuple


    # We do not tag the first two and last two words
    # since we added B_-2, B_-1, B_+1 and B_+2 as buffer words 
    viterbi[0]['_B-2',''] = (0.0, ('',''))
    viterbi[1]['_B-2','_B-1'] = (0.0, ('_B-2',''))

    # find the value of best_tag for each word i in the input
    feat_index = 0
    for i in range(2, N-2):
        (feat_index, feats) = feats_for_word(feat_index, feat_list)
        # retrieve the feature for a word
        if len(feats) == 0:
            print >>sys.stderr, " ".join(labels), " ".join(feat_list), "\n"
            raise ValueError("features do not align with input sentence")

        fields = labels[i].split()
        # e.g. 'International NNP' split into 'International' & 'NNP'
        (word, postag) = (fields[0], fields[1])
        # word = 'International', postag = 'NNP'
        found_tag = False

        # viterbi array - dynamic programming table 
        for u in tagset:
            # u is the previous tag, conditional tag
            for v in tagset:
                # v is the current tag

                # iterate whole tag set
                has_trigram_feat = False
                has_bigram_feat = False
                weight = 0.0

                # sum up all feature weight
                for feat in feats:
                    if feat == 'B': has_bigram_feat = True
                    if feat == 'T': has_trigram_feat = True
                    if (feat, v) in feat_vec:
                        weight += feat_vec[feat, v]


                prev_list = []
                best_weight = 0.0
                backpointer = ('', '')
                for (prev_u, prev_v) in viterbi[i-1]:
                    if prev_v == u:
                        # print >>sys.stderr, "word:", word, "feat:", feat, "tag", v, "prev_tag:", prev_v, "prev_prev_tag:", prev_u
                        (prev_value, prev_backpointer) = viterbi[i-1][prev_u, prev_v]
                        prev_tag_weight = weight
                        if has_trigram_feat:
                            prev_tag_feat = "T:" + prev_u + ',' + prev_v
                            if (prev_tag_feat, v) in feat_vec:
                                # add trigram value
                                prev_tag_weight += feat_vec[prev_tag_feat, v]

                        # if has_bigram_feat:
                        #     prev_tag_feat = "B:" + prev_v
                        #     if (prev_tag_feat, v) in feat_vec:
                        #         # add bigram value
                        #         prev_tag_weight += feat_vec[prev_tag_feat, v]
                        

                        if best_weight <= prev_tag_weight + prev_value:
                            best_weight = prev_tag_weight + prev_value
                            backpointer = (prev_u, prev_v)
                        # prev_list.append( (prev_tag_weight + prev_value, (prev_u, prev_v)) )

                    # (best_weight, backpointer) = sorted(prev_list, key=operator.itemgetter(0), reverse=True)[0]
                    # print >>sys.stderr, "best_weight:", best_weight, "backpointer:", backpointer

                if best_weight != 0.0:
                    viterbi[i][u, v] = (best_weight, backpointer)
                    found_tag = True

        if found_tag is False:
        # if not found, set default tag
            viterbi[i][default_tag, default_tag] = (0.0, (default_tag, default_tag))

    # recover the best sequence using backpointers
    maxvalue = get_maxvalue(viterbi[N-3])
    best_tag = maxvalue[0]
    # print viterbi
    for i in range(N-3, 1, -1):
        # reverse the sentense and insert into the output
        output.insert(0,best_tag[1])
        (value, backpointer) = viterbi[i][best_tag]
        best_tag = backpointer

    return output


# backup for original viterbi algorithm
# def perc_test(feat_vec, labeled_list, feat_list, tagset, default_tag):
#     # feature vector is the training result, default_tag is NP
#     output = []
#     labels = copy.deepcopy(labeled_list)
#     # add in the start and end buffers for the context
#     labels.insert(0, 'B_-1 B_-1 B_-1')
#     labels.insert(0, 'B_-2 B_-2 B_-2') # first two 'words' are B_-2 B_-1
#     labels.append('B_+1 B_+1 B_+1')
#     labels.append('B_+2 B_+2 B_+2') # last two 'words' are B_+1 B_+2

#     # size of the viterbi data structure
#     N = len(labels)

#     # Set up the data structure for viterbi search
#     viterbi = {}
#     for i in range(0, N):
#         viterbi[i] = {} 
#         # each column contains for each tag: a (value, backpointer) tuple


#     # We do not tag the first two and last two words
#     # since we added B_-2, B_-1, B_+1 and B_+2 as buffer words 
#     viterbi[0]['B_-2'] = (0.0, '')
#     viterbi[1]['B_-1'] = (0.0, 'B_-2')

#     # find the value of best_tag for each word i in the input
#     feat_index = 0
#     for i in range(2, N-2):
#         (feat_index, feats) = feats_for_word(feat_index, feat_list)
#         # retrieve the feature for a word
#         if len(feats) == 0:
#             print >>sys.stderr, " ".join(labels), " ".join(feat_list), "\n"
#             raise ValueError("features do not align with input sentence")

#         fields = labels[i].split()
#         # e.g. 'International NNP' split into 'International' & 'NNP'
#         (word, postag) = (fields[0], fields[1])
#         # word = 'International', postag = 'NNP'
#         found_tag = False
#         for tag in tagset:
#             # iterate the tag set
#             has_bigram_feat = False
#             weight = 0.0
#             # sum up the weights for all features except the bigram features
#             for feat in feats:
#                 # e.g. feat == 'U14:VBG', tag == 'B-VP'
#                 if feat == 'B': has_bigram_feat = True
#                 if (feat, tag) in feat_vec:
#                     # if in the trained feature vector, we have this (feat tag) tuple, add up the weight 
#                     weight += feat_vec[feat, tag]
#                     #print >>sys.stderr, "feat:", feat, "tag:", tag, "weight:", feat_vec[feat, tag]
#             prev_list = []
#             for prev_tag in viterbi[i-1]:
#                 #print >>sys.stderr, "word:", word, "feat:", feat, "tag:", tag, "prev_tag:", prev_tag
#                 (prev_value, prev_backpointer) = viterbi[i-1][prev_tag]
#                 prev_tag_weight = weight
#                 if has_bigram_feat:
#                     prev_tag_feat = "B:" + prev_tag
#                     if (prev_tag_feat, tag) in feat_vec:
#                         # Add bigram value
#                         prev_tag_weight += feat_vec[prev_tag_feat, tag]
#                 prev_list.append( (prev_tag_weight + prev_value, prev_tag) )
#             (best_weight, backpointer) = sorted(prev_list, key=operator.itemgetter(0), reverse=True)[0]
#             #print >>sys.stderr, "best_weight:", best_weight, "backpointer:", backpointer
#             if best_weight != 0.0:
#                 viterbi[i][tag] = (best_weight, backpointer)
#                 found_tag = True
#         if found_tag is False:
#             # if not found, set default tag
#             viterbi[i][default_tag] = (0.0, default_tag)

#     # recover the best sequence using backpointers
#     maxvalue = get_maxvalue(viterbi[N-3])
#     best_tag = maxvalue[0]
#     # print viterbi
#     for i in range(N-3, 1, -1):
#         # reverse the sentense and insert into the output
#         output.insert(0,best_tag)
#         (value, backpointer) = viterbi[i][best_tag]
#         best_tag = backpointer

#     return output

def conll_format(output, labeled_list):
    """ 
    conlleval documentation states that:
    the file should contain lines with items separated
    by delimiter characters (default is space). The final
    two items should contain the correct tag and the 
    guessed tag in that order. Sentences should be
    separated from each other by empty lines or lines
    with boundary fields (default -X-).
    """
    conll_output = []
    for i, v in enumerate(output):
        conll_output.append(labeled_list[i] + " " + v)
    return conll_output

def perc_testall(feat_vec, data, tagset):
    # feat_vec is the training result
    if len(tagset) <= 0:
        raise ValueError("Empty tagset")
    default_tag = tagset[0]
    for (labeled_list, feat_list) in data:
        # Each sentense is a tuple of two lists
        # So that every time output one sentence
        # data format [(['Rockwell NNP','International NNP',...],['U00:_B-2','U01:_B-1','U02:Rockwell',...] ), (...), ...]
        output = perc_test(feat_vec, labeled_list, feat_list, tagset, default_tag)
        print "\n".join(conll_format(output, labeled_list))
        print

def perc_read_from_file(filename):
    import pickle
    pfile = open(filename, 'rb')
    try:
        feat_vec = pickle.load(pfile)
    except:
        feat_vec = {}
    pfile.close()
    return feat_vec

def perc_write_to_file(feat_vec, filename):
    import pickle
    output = open(filename, 'wb')
    pickle.dump(feat_vec, output)
    output.close()

if __name__ == '__main__':
    optparser = optparse.OptionParser()
    optparser.add_option("-t", "--tagsetfile", dest="tagsetfile", default=os.path.join("data", "tagset.txt"), help="tagset that contains all the labels produced in the output, i.e. the y in \phi(x,y)")
    optparser.add_option("-i", "--inputfile", dest="inputfile", default=os.path.join("data", "input.txt.gz"), help="input data, i.e. the x in \phi(x,y)")
    optparser.add_option("-f", "--featfile", dest="featfile", default=os.path.join("data", "input.feats.gz"), help="precomputed features for the input data, i.e. the values of \phi(x,_) without y")
    # optparser.add_option("-i", "--inputfile", dest="inputfile", default=os.path.join("data", "small.test"), help="input data, i.e. the x in \phi(x,y)")
    # optparser.add_option("-f", "--featfile", dest="featfile", default=os.path.join("data", "small.test.feats"), help="precomputed features for the input data, i.e. the values of \phi(x,_) without y")
    optparser.add_option("-m", "--modelfile", dest="modelfile", default=os.path.join("data", "default.model"), help="weights for all features stored on disk")
    (opts, _) = optparser.parse_args()

    # each element in the feat_vec dictionary is:
    # key=feature_id value=weight
    feat_vec = {}
    tagset = []
    test_data = []

    tagset = read_tagset(opts.tagsetfile)
    print >>sys.stderr, "reading data ..."
    test_data = read_labeled_data(opts.inputfile, opts.featfile)
    print >>sys.stderr, "done."
    feat_vec = perc_read_from_file(opts.modelfile)
    perc_testall(feat_vec, test_data, tagset)

