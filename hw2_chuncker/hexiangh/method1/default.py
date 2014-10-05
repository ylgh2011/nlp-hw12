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

    for t in range(0, numepochs):
        tmp = 0
        # Count sentence
        for (labeled_list, feat_list) in train_data:
            tmp += 1
            print 'Iteration#',t,' - Sentence[', tmp,'] is processing now.'
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


                if i > 0:
                    fields = labels[i - 1].split()
                    pre_label = fields[2]

                fields = labels[i].split()
                label = fields[2]

                # update feature for bigram individually since it has the mentioned conner case
                for feat in feats:
                    if feat == 'B':
                        if i == 0:
                            if v != label:
                                feat_vec['B_-1', v] = feat_vec[feat, v] - 1.0
                                feat_vec['B_-1', label] = feat_vec[feat, label] + 1.0

                        elif v != label or output[i - 1] != pre_label:
                            feat_out = 'B:' + output[i - 1]
                            feat_lab = 'B:' + pre_label
                            feat_vec[feat_out, v] = feat_vec[feat_out, v] - 1.0
                            feat_vec[feat_lab, label] = feat_vec[feat_lab, label] + 1.0
                            # print 'Update feat_vec[',feat_out, ',', v,'] = ', str(feat_vec[feat_out, v])
                            # print 'Update feat_vec[',feat_lab, ',', label,'] = ', str(feat_vec[feat_lab, label])


                if v != label:
                    for feat in feats:
                        if feat == 'B':
                            # skip bigram case
                            continue
                        else:
                            feat_vec[feat, v] = feat_vec[feat, v] - 1
                            feat_vec[feat, label] = feat_vec[feat, label] + 1
                            # print 'Update feat_vec[',feat, ',', v,'] = ', str(feat_vec[feat, v])
                            # print 'Update feat_vec[',feat, ',', label,'] = ', str(feat_vec[feat, label])



    # delete dictionary terms with value of 0 and regularize the weight
    cnt = dict()
    for key, val in feat_vec:
        if val == 0:
            del feat_vec[key]
        elif key[0] == 'B':
            if cnt.get(key[0], -1) != -1: 
                cnt[key[0]] = cnt[key[0]] + 1
            else: 
                cnt[key[0]] = 0
        else:
            if cnt.get(key[:3], -1) != -1: 
                cnt[key[:3]] = cnt[key[:3]] + 1
            else: 
                cnt[key[:3]] = 0

    for key in feat_vec:
        if key[0] == 'B':
            feat_vec[key] = feat_vec[key]/cnt[key[0]]
        elif key[:3] in cnt:
            feat_vec[key] = feat_vec[key]/cnt[key[:3]]



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

