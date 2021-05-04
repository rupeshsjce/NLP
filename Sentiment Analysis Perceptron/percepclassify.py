import numpy as np
from sklearn.metrics import precision_score, recall_score, accuracy_score
import sys
import os
import string
from string import digits
import json
import math


class PerceptronClassify():
    def __init__(self, model_file):
        # Keep the final predictions [class_a class_b doc_file]
        self.predictions = []

        # Get the prior prob of classes and conditional probability of terms/features given the class.
        self.bias, self.weights = self.read_model(model_file)

        # CLEAN-UP. Same as we did in the learner class.
        self.stop_set = self.get_stopwords(stopwords)
        self.trans = self.remove_punctuation()
        self.remove_digits = str.maketrans(
            '', '', digits)

    def get_stopwords(self, stopwords):
        s_fd = open(stopwords, 'r')
        stop_raw = s_fd.readlines()
        stop_set = set([i.strip() for i in stop_raw])
        return stop_set

    def remove_punctuation(self):
        sp_chars = [i for i in string.punctuation]
        del_d = {sp_char: '' for sp_char in sp_chars}
        del_d[' '] = ''
        trans = str.maketrans(del_d)
        return trans

    def read_model(self, model_file):  # __init__()
        '''Get bias and weights from model file.'''
        with open(model_file) as json_file:
            model_dict = json.load(json_file)
            bias_fetched, weights_fetched = model_dict["bias"], model_dict["weights"]
            return bias_fetched, weights_fetched

    def classify(self, test_path):
        '''Read each of the test files, extract features, and classify doc using model.'''
        for root, directories, files in os.walk(test_path, topdown=False):
            for name in directories:
                dir_split = os.path.join(root, name).split('/')
                if len(dir_split) == 4:
                    doc_files = [f for f in os.listdir(
                        os.path.join(root, name))]
                    for doc_name in doc_files:
                        doc_file = os.path.join(root, name) + '/' + doc_name
                        self.read_features_classify(doc_file)

    def read_features_classify(self, doc_file):
        '''Get input features from the document and calculate activation 
        (by multiply against associated weights and adding bias).
        Return the selected label for both classes.'''

        activation_val = {
            "belief": self.bias["belief"], "sentiment": self.bias["sentiment"]}

        vect_feat = dict()
        fd_f = open(doc_file, 'r')
        raw_text = fd_f.readlines()[0]
        word_list = raw_text.split(' ')
        for word in word_list:
            word1 = word.lower().strip()
            word2 = word1.translate(self.remove_digits)
            word_list2 = word2.split(',')
            for word_i in word_list2:
                token = word_i.translate(self.trans)
                if token == '':
                    continue
                if token in self.stop_set:
                    continue

                # Add to feature vector
                if token not in vect_feat:
                    vect_feat[token] = 1
                else:
                    vect_feat[token] += 1

        # Compute activation score from vect_feat * weights
        for feat in vect_feat.keys():
            for c in activation_val.keys():
                if feat in self.weights[c]:
                    w_x = self.weights[c][feat] * vect_feat[feat]
                    prev_val = activation_val[c]
                    activation_val[c] = prev_val + w_x

        # Convert into labels as per (w*x + b) for the input features.
        preds = []
        for c in activation_val.keys():
            if c == 'belief':
                preds.append('truthful') if activation_val[c] > 0 else preds.append(
                    'deceptive')
            elif c == 'sentiment':
                preds.append('positive') if activation_val[c] > 0 else preds.append(
                    'negative')
        preds.append(doc_file)
        self.predictions.append(preds)

    def output_result(self, output_file):
        fd = open(output_file, "w")
        for pred in test.predictions:
            fd.write(' '.join(pred) + '\n')
        fd.close()


# PARAMETERS
# model_file = 'averagedmodel.txt'
model_file = 'vanillamodel.txt'
# model_file = sys.argv[1]

stopwords = 'stopwords.txt'
output_file = 'percepoutput.txt'
test_path = 'op_spam_dev_data'
#test_path = sys.argv[2]

# DRIVER
test = PerceptronClassify(model_file)
test.classify(test_path)
test.output_result(output_file)
