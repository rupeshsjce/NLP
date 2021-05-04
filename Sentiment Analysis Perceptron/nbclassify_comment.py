from sklearn.metrics import accuracy_score, precision_score, recall_score
import os
import string
from string import digits
import json
import math
import sys


class NbClassify():
    def __init__(self, model_file, stopwords):
        self.stop_set = self.extract_stopwords(stopwords)
        self.trans = self.punc_remove()  # For removing punctuation
        self.remove_digits = str.maketrans(
            '', '', digits)  # For removing digits
        self.prior_probs, self.cond_probs = self.read_model(model_file)
        self.predictions = []

    def extract_stopwords(self, stopwords):  # __init__()
        '''Make a set of stopwords from the stopwords file'''
        s_fd = open(stopwords, 'r')
        stop_raw = s_fd.readlines()
        stop_set = set([i.strip() for i in stop_raw])
        return stop_set

    def punc_remove(self):  # __init__()
        '''Make a dict that will remove special characters'''
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
        '''Read in test files one-by-one, extract features, and classify doc using model.'''
        for root, directories, files in os.walk(test_path, topdown=False):
            # print("root : ", root)
            # print("directories  :", directories)
            # print("files : ", files)
            for name in directories:
                print("for name in directories ..", directories)

                dir_split = os.path.join(root, name).split('/')
                print("dir_split :", dir_split)
                if len(dir_split) == 4:  # 15 in vocareum
                    # Get class labels
                    class_sentiment = dir_split[1].split('_')[0]
                    class_belief = dir_split[2].split('_')[0]

                    doc_files = [f for f in os.listdir(
                        os.path.join(root, name))]
                    for doc_name in doc_files:
                        doc_file = os.path.join(root, name) + '/' + doc_name
                        self.extract_features_classify(
                            doc_file, class_belief, class_sentiment)

    # called by classify()
    def extract_features_classify(self, doc_file, class_belief, class_sentiment):
        fd1.write(class_belief + " " + class_sentiment + " " + doc_file + "\n")
        '''Extract features from document/review and populate the class_feat_counts.
        Return the selected label for both classes.
        doc_file - full path to the review text'''

        # initialize bayes scores with prior probs
        p_class_given_doc = {'belief': {'truthful': math.log(self.prior_probs['belief']['truthful'], 10),
                                        'deceptive': math.log(self.prior_probs['belief']['deceptive'], 10)},
                             'sentiment': {'positive': math.log(self.prior_probs['sentiment']['positive'], 10),
                                           'negative': math.log(self.prior_probs['sentiment']['negative'], 10)}}
        r_fd = open(doc_file, 'r')
        raw_text = r_fd.readlines()[0]
        word_list = raw_text.split(' ')
        for word in word_list:
            word1 = word.lower().strip()
            # Remove digits and punctuation
            word2 = word1.translate(self.remove_digits)
            word_list2 = word2.split(',')
            for word_i in word_list2:
                token = word_i.translate(self.trans)

                # Edge case: check for inter-word commas
                if token == '':
                    continue

                # Remove stopwords
                if token in self.stop_set:
                    continue

                # For each class/label, check if the word exists within the class/label cond_probs
                # If yes, then select the cond_prob and multiply it to the bayes_scorees[c][l]
                for c in p_class_given_doc.keys():
                    labels = list(p_class_given_doc[c].keys())
                    for l in labels:
                        if token in self.cond_probs[c][l]:
                            current_prob = self.cond_probs[c][l][token]
                            prev_probs = p_class_given_doc[c][l]
                            p_class_given_doc[c][l] = prev_probs + \
                                math.log(current_prob, 10)

        # Select max class label for each class
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


# PARAMETERS
model_file = 'nbmodel.txt'
test_path = 'op_spam_dev_data'
#test_path = sys.argv[1]
stopwords = 'stopwords.txt'
output_file = 'nboutput.txt'
output_actual_file = "nbactual.txt"
fd1 = open(output_actual_file, "w")

# DRIVER
test = NbClassify(model_file, stopwords)
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
