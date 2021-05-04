import numpy as np
import sys
import os
import string
from string import digits
import json


class MultinomailNbTrain():
    def __init__(self, input_file_path):
        self.input_path = input_file_path  # Input directory

        # Initlialize the prior probability of the class (in this case where training data is equally distributed, it will be 0.5.
        # P(truthful) = 0.5 , P(deceptive)= 0.5 . Same for P(positive) = P(negative) = 0.5). Anyways it will be calculated.
        self.prior_probs = {'belief': {'truthful': 0, 'deceptive': 0},
                            'sentiment': {'positive': 0, 'negative': 0}}
        # Just a helper tin calculating above probability as it will keep track of count of class in training data.
        self.prior_count = {'belief': {'truthful': 0, 'deceptive': 0},
                            'sentiment': {'positive': 0, 'negative': 0}}

        # prior probability for the occurrence of a term as opposed to the prior probability of a class
        # which we estimate in Equation (13.5) on the document level.
        self.priors = {'belief': {'truthful': 0, 'deceptive': 0},
                       'sentiment': {'positive': 0, 'negative': 0}}

        # CLEANUP HOLDINGS
        self.stop_set = self.get_stopwords(stopwords)
        # For removing punctuation
        self.trans = self.remove_punctuation()
        # For removing digits
        self.remove_digits = str.maketrans(
            '', '', digits)

        # Keep track of all the features for each class.
        # class_type>class>feature>count
        # class_type : belief / sentiment
        # class = belief->truthful belief->deceptive sentiment->positive sentiment->negative
        # feature = belief->truthful->token1 : 10
        self.class_feat_counts = {'belief': {'truthful': dict(), 'deceptive': dict()},
                                  'sentiment': {'positive': dict(), 'negative': dict()}}

        # For a given class, the length of the vocabulary. Used during smoothing also.
        self.class_vocab_size = 0

    def get_stopwords(self, stopwords):
        '''Make a set of stopwords from the stopwords file'''
        s_fd = open(stopwords, 'r')
        stop_raw = s_fd.readlines()
        stop_set = set([i.strip() for i in stop_raw])
        return stop_set

    def remove_punctuation(self):
        '''Make a dict that will remove special characters'''
        sp_chars = [i for i in string.punctuation]
        del_d = {sp_char: '' for sp_char in sp_chars}
        del_d[' '] = ''
        trans = str.maketrans(del_d)
        return trans

    def class_feat_count(self):  # STEP 1
        ''' Read each review file and extract the file's labels: class_belief and class_sentiment.
        For each review, tokenize and add each token to the class_feat_counts'''
        for root, directories, files in os.walk(self.input_path, topdown=False):
            for name in directories:
                if name == "fold1":
                    continue
                dir_split = os.path.join(root, name).split('/')
                #print("dir_split : ", dir_split)
                if len(dir_split) == 4:
                    # Get class labels
                    class_sentiment = dir_split[1].split('_')[0]
                    class_belief = dir_split[2].split('_')[0]
                    doc_files = [f for f in os.listdir(
                        os.path.join(root, name))]
                    for doc_name in doc_files:
                        doc_file = os.path.join(root, name) + '/' + doc_name
                        # extract features
                        self.extract_features(
                            doc_file, class_belief, class_sentiment)
        # Compute prior_probs of the class and not the terms.
        for c in self.prior_count.keys():
            print(self.prior_count)
            c_token_count = sum(self.prior_count[c].values())
            labels = list(self.prior_count[c].keys())
            for l in labels:
                c_l_prob = self.prior_count[c][l] / c_token_count
                self.prior_probs[c][l] = c_l_prob

    # called by class_feat_count()
    def extract_features(self, doc_file, class_belief, class_sentiment):
        # Update priors on the document level.
        self.prior_count['belief'][class_belief] += 1
        self.prior_count['sentiment'][class_sentiment] += 1

        ''' populate the class_feat_counts.'''
        fd_f = open(doc_file, 'r')
        raw_text = fd_f.readlines()[0]
        word_list = raw_text.split(' ')
        for word in word_list:
            word1 = word.lower().strip()
            # Remove digits and punctuation
            word2 = word1.translate(self.remove_digits)
            word_list2 = word2.split(',')
            for word_i in word_list2:
                token = word_i.translate(self.trans)
                if token == '':
                    continue
                if token in self.stop_set:
                    continue

                # Update priors of the terms and not the class.
                self.priors['belief'][class_belief] += 1
                self.priors['sentiment'][class_sentiment] += 1

                # Add belief feature
                if token not in self.class_feat_counts['belief'][class_belief]:
                    # Create feature count
                    self.class_feat_counts['belief'][class_belief][token] = 1
                else:
                    # Update feature count
                    self.class_feat_counts['belief'][class_belief][token] += 1

                # Add sentiment feature
                if token not in self.class_feat_counts['sentiment'][class_sentiment]:
                    # Create feature count
                    self.class_feat_counts['sentiment'][class_sentiment][token] = 1
                else:
                    # Update feature count
                    self.class_feat_counts['sentiment'][class_sentiment][token] += 1

    def count_feats(self):  # STEP 2
        c = list(test.priors.keys())[0]
        print("c = ", c)
        labels = list(test.priors[c].keys())
        class_feats = set()
        for l in labels:
            feats = test.class_feat_counts[c][l].keys()
            [class_feats.add(feat) for feat in feats]
        n_class_feats = len(class_feats)
        self.class_vocab_size = n_class_feats

    def plus_one_smooth_and_cond_prob(self):  # STEP 3
        # STEP 1: For each class, for each label, +1 to each feature
        for c in self.class_feat_counts.keys():
            labels = list(self.class_feat_counts[c].keys())
            for l in labels:
                for key in self.class_feat_counts[c][l].keys():
                    self.class_feat_counts[c][l][key] += 1

        # STEP 2: For each class, find the diffs between two binary labels, and add features
        for c in self.class_feat_counts.keys():
            labels = list(self.class_feat_counts[c].keys())
            X = set(self.class_feat_counts[c][labels[0]].keys())
            Y = set(self.class_feat_counts[c][labels[1]].keys())
            X_asbsent = Y.difference(X)
            Y_absent = X.difference(Y)
            # For the null instances in trainign data for a particular class,
            # add 1 to each count for that class, like for P(WTO | UK) = 0 to avoid sparseness.
            for feat in X_asbsent:
                self.class_feat_counts[c][labels[0]][feat] = 1
            for feat in Y_absent:
                self.class_feat_counts[c][labels[1]][feat] = 1

        # STEP 3: (Eq. 13.7 from the 13bayes.pdf)
        # Get the conditional probabilty by dividing fearure_count to (total terms per class + class_vocab_size)
        for c in self.class_feat_counts.keys():
            labels = list(self.class_feat_counts[c].keys())
            for l in labels:
                for key in self.class_feat_counts[c][l].keys():
                    feat_count = self.class_feat_counts[c][l][key]
                    self.class_feat_counts[c][l][key] = feat_count / \
                        (self.priors[c][l] + self.class_vocab_size)

    def output_model(self, output_file):  # STEP 4
        '''Serialize the priors and conditional probabilities into a model .txt file.'''
        model_dict = {'prior_probs': self.prior_probs,
                      'cond_probs': self.class_feat_counts}
        model = json.dumps(model_dict, indent=1)
        fd = open(output_file, "w")
        fd.write(model)
        fd.close()


# PARAMETERS
input_file_path = 'op_spam_training_data'
#input_filepath = sys.argv[1]
stopwords = 'stopwords.txt'
output_file = 'nbmodel.txt'

# DRIVER: Fit the model
test = MultinomailNbTrain(input_file_path)
test.class_feat_count()
# Count the vocab size per class (belief, sentiment)
test.count_feats()
# This will calculate the conditional probability with smoothing.
test.plus_one_smooth_and_cond_prob()
test.output_model(output_file)
