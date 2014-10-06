"""
Voting Multi-dimensional Data Representation
    1) relevant words set Ws
    2) transfer original input to specialized output 
        * fs(<wi, pi, ti>) = / <wi, pi, wi*pi*ti>,  if wi belongs to Ws
                             \ <pi, pi*ti>,         otherwise

"""
import perc
import sys, optparse, os, copy
from collections import defaultdict

def perc_train(train_data, tagset, numepochs, word_set):
    feat_vec = defaultdict(int)
    # insert your code here
    if len(tagset) <= 0:
        raise ValueError("Empty tagset")

    numepochs = int(1)
    default_tag = tagset[0]
    for t in range(numepochs):
        tmp = 0
        # Count sentence
        print 'Iteration#',t,' is processing now.'
        cnt = 0
        for (labeled_list, feat_list) in train_data:
            cnt = cnt + 1
            if cnt % 1000 == 0:
                print 'current status: ', str(round(100*cnt/9000.0,2)),'%'
            labels = copy.deepcopy(labeled_list)
            # add in the start and end buffers for the context
            # for every sentence in the training set, iterate numepochs times
            output = perc.perc_test(feat_vec, labeled_list, feat_list, tagset, default_tag, word_set)

            feat_index = 0
            # check word by word if the predicted tag is equal to the true tag
            for i, v in enumerate(output):
                (feat_index, feats) = perc.feats_for_word(feat_index, feat_list)
                # retrieve the feature for a word
                if len(feats) == 0:
                    print >>sys.stderr, " ".join(labels), " ".join(feat_list), "\n"
                    raise ValueError("features do not align with input sentence")
                
                fields = labels[i].split()
                label = fields[2]
                if i > 0: 
                    label_pre = labels[i-1].split()[2]
                    if output[i-1] != label_pre or output[i] != label:
                        for feat in feats:
                            if feat[0] == 'B': 
                            # for bigram feature
                                feat_out = feat + ":" + output[i-1]  
                                # feat_out is the "B:<previous output>"
                                feat_lab = feat + ":" + label_pre  
                                # feat_lab is the "B:<previous label>"
                                # reward best condition

                                feat_vec[feat_lab, label] = feat_vec[feat_lab, label] + 1

                                # penalize condition
                                feat_vec[feat_out, output[i]] = feat_vec[feat_out, output[i]] - 1
                                
                            else: 
                            # for U00 to U22 feature
                                feat_vec[feat, output[i]] = feat_vec[feat, output[i]] - 1
                                feat_vec[feat, label] = feat_vec[feat, label] + 1
                else:
                    # for i==0 case, all the first word in each sentence
                    label_pre = 'B_-1'  # previous label will be denoted by B_-1
                    for feat in feats:
                        if feat[0] == 'B':  
                        # bigram feature case
                            feat = feat + ":" + label_pre
                        feat_vec[feat, output[i]] = feat_vec[feat, output[i]] - 1
                        feat_vec[feat, label] = feat_vec[feat, label] + 1

    # please limit the number of iterations of training to n iterations
    return feat_vec

if __name__ == '__main__':
    optparser = optparse.OptionParser()
    optparser.add_option("-t", "--tagsetfile", dest="tagsetfile", default=os.path.join("data", "tagset.txt"), help="tagset that contains all the labels produced in the output, i.e. the y in \phi(x,y)")
    optparser.add_option("-i", "--trainfile", dest="trainfile", default=os.path.join("data", "train.txt.gz"), help="input data, i.e. the x in \phi(x,y)")
    optparser.add_option("-f", "--featfile", dest="featfile", default=os.path.join("data", "train.feats.gz"), help="precomputed features for the input data, i.e. the values of \phi(x,_) without y")
    # optparser.add_option("-i", "--trainfile", dest="trainfile", default=os.path.join("data", "train.dev"), help="input data, i.e. the x in \phi(x,y)")
    # optparser.add_option("-f", "--featfile", dest="featfile", default=os.path.join("data", "train.feats.dev"), help="precomputed features for the input data, i.e. the values of \phi(x,_) without y")
    optparser.add_option("-e", "--numepochs", dest="numepochs", default=int(10), help="number of epochs of training; in each epoch we iterate over over all the training examples")
    optparser.add_option("-m", "--modelfile", dest="modelfile", default=os.path.join("data", "default.model"), help="weights for all features stored on disk")
    optparser.add_option("-w", "--wordsetfile", dest="wordsetfile", default=os.path.join("data", "word_set"), help="the word set write to disk")
    (opts, _) = optparser.parse_args()

    # each element in the feat_vec dictionary is:
    # key=feature_id value=weight
    feat_vec = {}
    # format: {('U14:VBG','B-VP'):w1, ...}
    tagset = []
    train_data = []

    tagset = perc.read_tagset(opts.tagsetfile)
    print >>sys.stderr, "reading data ..."
    data = perc.read_labeled_data(opts.trainfile, opts.featfile)
    word_set = data[0]
    perc.perc_write_to_file(word_set, opts.wordsetfile)
    train_data = data[1]
    print >>sys.stderr, "done."
    feat_vec = perc_train(train_data, tagset, int(opts.numepochs), word_set)
    perc.perc_write_to_file(feat_vec, opts.modelfile)

