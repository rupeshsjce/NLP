import numpy as np
import sys
import os
import string
from string import digits
import json
import random
random.seed(42)


class PerceptronTrain():
    def __init__(self, input_file_path):
        self.input_path = input_file_path  # Input directory

        self.class_label = {'belief': {'truthful': 1, 'deceptive': -1},
                            'sentiment': {'positive': 1, 'negative': -1}}
        self.class_weights = {'belief': dict(), 'sentiment': dict()}
        # Initally bias is zero.
        self.class_bias = {'belief': 0, 'sentiment': 0}

        self.class_weights_avg = {'belief': dict(), 'sentiment': dict()}
        self.bias_avg = {'belief': 0, 'sentiment': 0}

        # CLEANUP HOLDINGS
        self.stop_set = self.get_stopwords(stopwords)
        # For removing punctuation
        self.trans = self.remove_punctuation()
        # For removing digits
        self.remove_digits = str.maketrans(
            '', '', digits)

        # For a given class, the length of the vocabulary. Used during smoothing also.
        self.class_vocab_size = 0
        self.total_instances_seen = 1

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

    def class_learn_params(self, n_epochs):  # STEP 1
        training_data = []
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
                        # Store all the input in a file so that we can randomize it.
                        training_data.append(doc_file)
        # Randomize it.
        random.shuffle(training_data)

        # Run through the shuffled list of training example for n_epochs.
        for epoch in range(n_epochs):
            for doc_file in training_data:
                class_sentiment = doc_file.split('/')[-4].split('_')[0]
                class_belief = doc_file.split('/')[-3].split('_')[0]
                self.get_features(
                    doc_file, class_belief, class_sentiment)

    def get_features(self, doc_file, class_belief, class_sentiment):

        classes = {'belief': class_belief, 'sentiment': class_sentiment}
        fd_f = open(doc_file, 'r')
        raw_text = fd_f.readlines()[0]
        word_list = raw_text.split(' ')

        vect_feat = dict()  # Feature Vector for a particular review.

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

                # Add to feature vector
                if token not in vect_feat:
                    vect_feat[token] = 1
                else:
                    vect_feat[token] += 1

        # Update the weights and bias for the features for each class.
        # Calculate the activation first and then multiply with class_label
        # to see if it is incorrect and if so then update the params.

        # Calculate activation (W.transpose().X + B) for this example for each class (belief and sentiment).
        class_activation_value = self.get_activation_value(vect_feat)

        # TODO: Update weight and bias for each of the features.Will come back !!!
        for c in classes.keys():
            # Y label for this particular example/input file for both class.
            label_c = self.class_label[c][classes[c]]
            if label_c * class_activation_value[c] <= 0:
                # Misclassification case, so update the weight and bias.
                for feature in vect_feat.keys():
                    count = self.total_instances_seen
                    # Update weights of the features
                    if feature not in self.class_weights[c]:
                        self.class_weights[c][feature] = label_c * \
                            vect_feat[feature]
                    else:
                        self.class_weights[c][feature] += label_c * \
                            vect_feat[feature]

                    # update cached weights
                    if feature not in self.class_weights_avg[c]:
                        self.class_weights_avg[c][feature] = label_c * \
                            count * vect_feat[feature]
                    else:
                        self.class_weights_avg[c][feature] += label_c * \
                            count * vect_feat[feature]
                # Update bias.
                self.class_bias[c] += label_c
                self.bias_avg[c] += label_c * count  # update cached bias
        self.total_instances_seen += 1  # increment counter regardless of update

    def get_activation_value(self, vect_feat):
        class_activation_value = {'belief': 0, 'sentiment': 0}
        for feature in vect_feat:
            for c in class_activation_value.keys():
                if feature in self.class_weights[c]:
                    feat_weight = self.class_weights[c][feature]
                    class_activation_value[c] += vect_feat[feature] * \
                        feat_weight
        # Add biases for both the class.
        for c in self.class_bias:
            class_activation_value[c] += self.class_bias[c]
        return class_activation_value

    def output_model(self, output_file):  # STEP 4
        vanilla_dict = {"bias": self.class_bias, "weights": self.class_weights}

        # Create averaged model
        count = self.total_instances_seen
        avg_dict = {"bias": {"belief": 0, "sentiment": 0},
                    "weights": {"belief": dict(), "sentiment": dict()}}

        for c in self.class_weights:  # weights
            for w_key in self.class_weights[c].keys():
                w_val = self.class_weights[c][w_key]
                w_val_avg = w_val - \
                    (self.class_weights_avg[c][w_key] / count)
                avg_dict["weights"][c][w_key] = w_val_avg

        for c in self.class_bias:  # bias
            b_val = self.class_bias[c]
            b_val_avg = b_val - (self.bias_avg[c] / count)
            avg_dict["bias"][c] = b_val_avg

        # Write the weight and biases to the file.
        model = json.dumps(vanilla_dict, indent=1)
        fd = open(output_file, "w")
        fd.write(model)
        fd.close()

        # Write the weight and biases to the file.
        output_avg = 'averagedmodel.txt'
        model = json.dumps(avg_dict, indent=1)
        fd = open(output_avg, "w")
        fd.write(model)
        fd.close()


# PARAMETERS
input_file_path = 'op_spam_training_data'
#input_filepath = sys.argv[1]
stopwords = 'stopwords.txt'
output_file = 'vanillamodel.txt'
n_epochs = 10

# DRIVER: Fit the model
test = PerceptronTrain(input_file_path)
test.class_learn_params(n_epochs)
test.output_model(output_file)
