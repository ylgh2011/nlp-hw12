"""

You have to write the perc_train function that trains the feature weights using the perceptron algorithm for the CoNLL 2000 chunking task.

Each element of train_data is a (labeled_list, feat_list) pair. 

Inside the perceptron training loop:

    - Call perc_test to get the tagging based on the current feat_vec and compare it with the true output from the labeled_list

    - If the output is incorrect then we have to update feat_vec (the weight vector)

    - In the notation used in the paper we have w = w_0, w_1, ..., w_n corresponding to \phi_0(x,y), \phi_1(x,y), ..., \phi_n(x,y)

    - Instead of indexing each feature with an integer we index each feature using a string we called feature_id

    - The feature_id is constructed using the elements of feat_list (which correspond to x above) combined with the output tag (which correspond to y above)

    - The function perc_test shows how the feature_id is constructed for each word in the input, including the bigram feature "B:" which is a special case

    - feat_vec[feature_id] is the weight associated with feature_id

    - This dictionary lookup lets us implement a sparse vector dot product where any feature_id not used in a particular example does not participate in the dot product

    - To save space and time make sure you do not store zero values in the feat_vec dictionary which can happen if \phi(x_i,y_i) - \phi(x_i,y_{perc_test}) results in a zero value

    - If you are going word by word to check if the predicted tag is equal to the true tag, there is a corner case where the bigram 'T_{i-1} T_i' is incorrect even though T_i is correct.

"""

import perc
import sys, optparse, os, copy
from collections import defaultdict

def perc_train(train_data, tagset, numepochs):
    feat_vec = defaultdict(int)
    # insert your code here
    if len(tagset) <= 0:
        raise ValueError("Empty tagset")

    numepochs = int(10)
    default_tag = tagset[0]
    for t in range(numepochs):
        tmp = 0
        # Count sentence
        print 'Iteration#',t,' is processing now.'
        for (labeled_list, feat_list) in train_data:
            labels = copy.deepcopy(labeled_list)
            # add in the start and end buffers for the context
            # for every sentence in the training set, iterate numepochs times
            output = perc.perc_test(feat_vec, labeled_list, feat_list, tagset, default_tag)
            # compare current output and true result
            # correct_flag = True
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
                    if output[i-1] is not label_pre or output[i] != label:
                        for feat in feats:
                            if feat[0] == 'B': # for bigram feature
                                feat_out = feat + ":" + output[i-1]  # feat_out is the "B:<previous output>"
                                feat_lab = feat + ":" + label_pre  # feat_lab is the "B:<previous label>"
                                feat_vec[feat_out, output[i]] = feat_vec[feat_out, output[i]] - 1
                                feat_vec[feat_lab, label] = feat_vec[feat_lab, label] + 1
                                feat_vec[feat_out, label] = feat_vec[feat_out, label] + 1
                                feat_vec[feat_lab, output[i]] = feat_vec[feat_lab, output[i]] - 1
                            else: # for U00 to U22 feature
                                feat_vec[feat, output[i]] = feat_vec[feat, output[i]] - 1
                                feat_vec[feat, label] = feat_vec[feat, label] + 1
                else:  # for i==0 case, all the first word in each sentence
                    label_pre = 'B_-1'  # previous label will be denoted by B_-1
                    for feat in feats:
                        if feat[0] == 'B':  # bigram feature case
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
    optparser.add_option("-e", "--numepochs", dest="numepochs", default=int(10), help="number of epochs of training; in each epoch we iterate over over all the training examples")
    optparser.add_option("-m", "--modelfile", dest="modelfile", default=os.path.join("data", "default.model"), help="weights for all features stored on disk")
    (opts, _) = optparser.parse_args()

    # each element in the feat_vec dictionary is:
    # key=feature_id value=weight
    feat_vec = {}
    # format: {('U14:VBG','B-VP'):w1, ...}
    tagset = []
    train_data = []

    tagset = perc.read_tagset(opts.tagsetfile)
    print >>sys.stderr, "reading data ..."
    train_data = perc.read_labeled_data(opts.trainfile, opts.featfile)
    print >>sys.stderr, "done."
    feat_vec = perc_train(train_data, tagset, int(opts.numepochs))
    perc.perc_write_to_file(feat_vec, opts.modelfile)

