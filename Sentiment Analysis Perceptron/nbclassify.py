import numpy as np
from sklearn.metrics import precision_score, recall_score, accuracy_score
import sys
import os
import string
from string import digits
import json
import math


class MultinomailNbClassify():
    def __init__(self, model_file):
        # Keep the final predictions [class_a class_b doc_file]
        self.predictions = []

        # Get the prior prob of classes and conditional probability of terms/features given the class.
        self.prior_probs, self.cond_probs = self.read_model(model_file)

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
        '''Read and store the model file into memory.'''
        with open(model_file) as json_file:
            model_dict = json.load(json_file)
        prior_probs = model_dict['prior_probs']
        cond_probs = model_dict['cond_probs']
        return prior_probs, cond_probs

    def classify(self, test_path):
        '''Read each of the test files, extract features, and classify doc using model.'''
        for root, directories, files in os.walk(test_path, topdown=False):
            for name in directories:
                dir_split = os.path.join(root, name).split('/')
                if len(dir_split) == 4:
                    # Get class labels
                    class_sentiment = dir_split[1].split('_')[0]
                    class_belief = dir_split[2].split('_')[0]

                    doc_files = [f for f in os.listdir(
                        os.path.join(root, name))]
                    for doc_name in doc_files:
                        doc_file = os.path.join(root, name) + '/' + doc_name
                        self.read_features_classify(
                            doc_file, class_belief, class_sentiment)

    def read_features_classify(self, doc_file, class_belief, class_sentiment):
        fd1.write(class_belief + " " + class_sentiment + " " + doc_file + "\n")

        # initialize p_class_given_doc with prior probs
        p_class_given_doc = {'belief': {'truthful': math.log(self.prior_probs['belief']['truthful'], 10),
                                        'deceptive': math.log(self.prior_probs['belief']['deceptive'], 10)},
                             'sentiment': {'positive': math.log(self.prior_probs['sentiment']['positive'], 10),
                                           'negative': math.log(self.prior_probs['sentiment']['negative'], 10)}}
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

                # For each class/label, check if the word exists within the class/label cond_probs
                # If yes, then select the cond_prob and multiply it to the bayes_scorees[c][l]
                # To avoid float multiplication overflow, We are going to use log as it is monotonically increasing.
                for c in p_class_given_doc.keys():
                    labels = list(p_class_given_doc[c].keys())
                    for l in labels:
                        if token in self.cond_probs[c][l]:
                            current_prob = self.cond_probs[c][l][token]
                            # For the first time, it will be prior prob of class. And then it will be sum of prior plus previous terms.
                            prev_probs = p_class_given_doc[c][l]
                            p_class_given_doc[c][l] = prev_probs + \
                                math.log(current_prob, 10)

        # Select the argmax class label for each class.
        preds = []
        for c in p_class_given_doc.keys():
            label = max(
                p_class_given_doc[c], key=lambda key: p_class_given_doc[c][key])
            preds.append(label)
        preds.append(doc_file)
        self.predictions.append(preds)

    def output_results(self, output_file):
        fd = open(output_file, "w")
        for pred in test.predictions:
            fd.write(' '.join(pred) + '\n')
        fd.close()


# NB classifier PARAMETERS
model_file = 'nbmodel.txt'
test_path = 'op_spam_dev_data'
#test_path = sys.argv[1]
stopwords = 'stopwords.txt'
output_file = 'nboutput.txt'
output_actual_file = "nbactual.txt"
fd1 = open(output_actual_file, "w")

# DRIVER
test = MultinomailNbClassify(model_file)
test.classify(test_path)
test.output_results(output_file)
fd1.close()


predictions = []
# Using readlines()
file1 = open(output_file, 'r')
OLines = file1.readlines()
for line in OLines:
    predictions.append(line)

Y_test = []
# Using readlines()
file2 = open(output_actual_file, 'r')
ALines = file2.readlines()
for line in ALines:
    Y_test.append(line)

precision = precision_score(predictions, Y_test, average="weighted")
recall = recall_score(predictions, Y_test, average="weighted")
print("Accuracy : ", accuracy_score(predictions, Y_test))
print("Precision : ", precision)
print("Recall : ", recall)
F1 = 2 * (precision * recall) / (precision + recall)
print("F1 score : ", F1)
