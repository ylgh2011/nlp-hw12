"""
### Averaged perceptron algorithm

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
    feat_vec = defaultdict(float)
    avg_feat_vec = defaultdict(float)
    tau_feat_vec = dict()
    # insert your code here
    if len(tagset) <= 0:
        raise ValueError("Empty tagset")

    numepochs = int(2)
    default_tag = tagset[0]
    m = len(train_data) # length of training data
    for t in range(numepochs):
        print 'Iteration#',t,' is processing now.'
        for j, (labeled_list, feat_list) in enumerate(train_data):
            labels = copy.deepcopy(labeled_list)
            # add in the start and end buffers for the context
            # for every sentence in the training set, iterate numepochs times
            output = perc.perc_test(feat_vec, labeled_list, feat_list, tagset, default_tag)
            # compare current output and true result
            # correct_flag = True
            if j != m or t != numepochs - 1:
                feat_index = 0
                # check word by word if the predicted tag is equal to the true tag
                for i, v in enumerate(output):
                    (feat_index, feats) = perc.feats_for_word(feat_index, feat_list)
                    # retrieve the feature for a word
                    if len(feats) == 0:
                        print >>sys.stderr, " ".join(labels), " ".join(feat_list), "\n"
                        raise ValueError("features do not align with input sentence")
                    
                    label = labels[i].split()[2]
                    if i > 0: 
                        label_pre = labels[i-1].split()[2]
                        for feat in feats:

                            if feat[0] == 'B': # for bigram feature
                                feat_out = feat + ":" + output[i-1]  # feat_out is the "B:<previous output>"
                                feat_lab = feat + ":" + label_pre  # feat_lab is the "B:<previous label>"

                                if   output[i-1] != label_pre and output[i] != label:

                                    if feat in tau_feat_vec:
                                        (js, ts) = tau_feat_vec[feat]
                                        for tag in tagset:
                                            if (feat, tag) in avg_feat_vec:
                                                avg_feat_vec[feat, tag] = avg_feat_vec[feat, tag] + feat_vec[feat, tag] * (t*m + j - ts*m - js)


                                    # update original feature vector
                                    feat_vec[feat_out, output[i]]   -= 1.0
                                    feat_vec[feat_lab, output[i]]   -= 1.0
                                    feat_vec[feat_out, label]       += 1.0
                                    feat_vec[feat_lab, label]       += 1.0

                                    # update avg feature vector
                                    avg_feat_vec[feat_out, output[i]]   -= 1.0
                                    avg_feat_vec[feat_lab, output[i]]   -= 1.0
                                    avg_feat_vec[feat_out, label]       += 1.0
                                    avg_feat_vec[feat_lab, label]       += 1.0

                                    tau_feat_vec[feat_out] = (j, t)
                                    tau_feat_vec[feat_lab] = (j, t)

                                elif output[i-1] == label_pre and output[i] != label:

                                    if feat in tau_feat_vec:
                                        (js, ts) = tau_feat_vec[feat]
                                        for tag in tagset:
                                            if (feat, tag) in avg_feat_vec:
                                                avg_feat_vec[feat, tag] = avg_feat_vec[feat, tag] + feat_vec[feat, tag] * (t*m + j - ts*m - js)


                                    feat_vec[feat_lab, output[i]]   -= 2.0
                                    feat_vec[feat_lab, label]       += 2.0

                                    avg_feat_vec[feat_lab, output[i]]   -= 2.0
                                    avg_feat_vec[feat_lab, label]       += 2.0
                                    
                                    tau_feat_vec[feat_lab] = (j, t)

                                elif output[i-1] != label_pre and output[i] == label:
                                    pass

                                elif output[i-1] == label_pre and output[i] == label:
                                    pass

                            else: # for U00 to U22 feature

                                if output[i] != label and feat in tau_feat_vec:
                                    (js, ts) = tau_feat_vec[feat]
                                    for tag in tagset:
                                        if (feat, tag) in avg_feat_vec:
                                            avg_feat_vec[feat, tag] = avg_feat_vec[feat, tag] + feat_vec[feat, tag] * (t*m + j - ts*m - js)

                                feat_vec[feat, output[i]] -= 1.0
                                feat_vec[feat, label] += 1.0

                                avg_feat_vec[feat, output[i]] -= 1.0
                                avg_feat_vec[feat, label] += 1.0

                                # update vector
                                tau_feat_vec[feat] = (j, t)


                    else:  # for i==0 case, all the first word in each sentence
                        label_pre = 'B_-1'  # previous label will be denoted by B_-1
                        for feat in feats:


                            if feat[0] == 'B':  # bigram feature case
                                feat = feat + ":" + label_pre

                            if output[i] != label and feat in tau_feat_vec:
                                (js, ts) = tau_feat_vec[feat]
                                for tag in tagset:
                                    if (feat, tag) in avg_feat_vec:
                                        avg_feat_vec[feat, tag] = avg_feat_vec[feat, tag] + feat_vec[feat, tag] * (t*m + j - ts*m - js)


                            feat_vec[feat, output[i]] -= 1.0
                            feat_vec[feat, label] += 1.0

                            avg_feat_vec[feat, output[i]] -= 1.0
                            avg_feat_vec[feat, label] += 1.0

                            tau_feat_vec[feat] = (j, t)


            else:
                # last sentence of each iteration
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
                        for feat in feats:
                            if feat[0] == 'B': # for bigram feature
                                feat_out = feat + ":" + output[i-1]  # feat_out is the "B:<previous output>"
                                feat_lab = feat + ":" + label_pre  # feat_lab is the "B:<previous label>"

                                if   output[i-1] != label_pre and output[i] != label:

                                    if feat in tau_feat_vec:
                                        (js, ts) = tau_feat_vec[feat]
                                        for tag in tagset:
                                            if (feat, tag) in avg_feat_vec:
                                                avg_feat_vec[feat, tag] = avg_feat_vec[feat, tag] + feat_vec[feat, tag] * (t*m + j - ts*m - js)

                                    # update original feature vector
                                    feat_vec[feat_out, output[i]]   -= 1.0
                                    feat_vec[feat_lab, output[i]]   -= 1.0
                                    feat_vec[feat_out, label]       += 1.0
                                    feat_vec[feat_lab, label]       += 1.0

                                    # update avg feature vector
                                    avg_feat_vec[feat_out, output[i]]   -= 1.0
                                    avg_feat_vec[feat_lab, output[i]]   -= 1.0
                                    avg_feat_vec[feat_out, label]       += 1.0
                                    avg_feat_vec[feat_lab, label]       += 1.0

                                elif output[i-1] == label_pre and output[i] != label:

                                    if feat in tau_feat_vec:
                                        (js, ts) = tau_feat_vec[feat]
                                        for tag in tagset:
                                            if (feat, tag) in avg_feat_vec:
                                                avg_feat_vec[feat, tag] = avg_feat_vec[feat, tag] + feat_vec[feat, tag] * (t*m + j - ts*m - js)


                                    feat_vec[feat_lab, output[i]]   -= 2.0
                                    feat_vec[feat_lab, label]       += 2.0

                                    avg_feat_vec[feat_lab, output[i]]   -= 2.0
                                    avg_feat_vec[feat_lab, label]       += 2.0
                                    

                                elif output[i-1] != label_pre and output[i] == label:
                                    pass

                                elif output[i-1] == label_pre and output[i] == label:
                                    pass

                            else: # for U00 to U22 feature

                                if output[i] != label and feat in tau_feat_vec:
                                    (js, ts) = tau_feat_vec[feat]
                                    for tag in tagset:
                                        if (feat, tag) in avg_feat_vec:
                                            avg_feat_vec[feat, tag] = avg_feat_vec[feat, tag] + feat_vec[feat, tag] * (t*m + j - ts*m - js)


                                feat_vec[feat, output[i]] -= 1.0
                                feat_vec[feat, label] += 1.0

                                avg_feat_vec[feat, output[i]] -= 1.0
                                avg_feat_vec[feat, label] += 1.0


                    else:  # for i==0 case, all the first word in each sentence
                        label_pre = 'B_-1'  # previous label will be denoted by B_-1
                        for feat in feats:
                            if feat[0] == 'B':  # bigram feature case
                                feat = feat + ":" + label_pre
                            
                            if output[i] != label and feat in tau_feat_vec:
                                (js, ts) = tau_feat_vec[feat]
                                for tag in tagset:
                                    if (feat, tag) in avg_feat_vec:
                                        avg_feat_vec[feat, tag] = avg_feat_vec[feat, tag] + feat_vec[feat, tag] * (t*m + j - ts*m - js)


                            feat_vec[feat, output[i]] -= 1.0
                            feat_vec[feat, label] += 1.0

                            avg_feat_vec[feat, output[i]] -= 1.0
                            avg_feat_vec[feat, label] += 1.0

        mid_vec = copy.deepcopy(avg_feat_vec)
        filename = 'mid_model_' + str(t + 1)
        for key in mid_vec.keys():
            mid_vec[key] = mid_vec[key]/float((t + 1)*m)
        perc.perc_write_to_file(mid_vec, filename)
        # end of iteration

    # averaging perceptron
    for key in avg_feat_vec.keys():
        avg_feat_vec[key] = avg_feat_vec[key]/float(numepochs*m)
    # please limit the number of iterations of training to n iterations
    return avg_feat_vec

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

