# This program is a very simple lemmatizer, which learns a
# lemmatization function from an annotated corpus. The function is
# so basic I wouldn't even consider it machine learning: it's
# basically just a big lookup table, which maps every word form
# attested in the training data to the most common lemma associated
# with that form. At test time, the program checks if a form is in
# the lookup table, and if so, it gives the associated lemma; if the
# form is not in the lookup table, it gives the form itself as the
# lemma (identity mapping).

# The program performs training and testing in one run: it reads the
# training data, learns the lookup table and keeps it in memory,
# then reads the test data, runs the testing, and reports the
# results.

# The program takes two command line arguments, which are the paths
# to the training and test files. Both files are assumed to be
# already tokenized, in Universal Dependencies format, that is: each
# token on a separate line, each line consisting of fields separated
# by tab characters, with word form in the second field, and lemma
# in the third field. Tab characters are assumed to occur only in
# lines corresponding to tokens; other lines are ignored.

import sys
import re

# Global variables

# Paths for data are read from command line
train_file = sys.argv[1]
test_file = sys.argv[2]

# Counters for lemmas in the training data: word form -> lemma -> count
lemma_count = {}

# Lookup table learned from the training data: word form -> lemma
lemma_max = {}

# Variables for reporting results
training_stats = ['Wordform types', 'Wordform tokens', 'Unambiguous types', 'Unambiguous tokens',
                  'Ambiguous types', 'Ambiguous tokens', 'Ambiguous most common tokens', 'Identity tokens']
training_counts = dict.fromkeys(training_stats, 0)

test_outcomes = ['Total test items', 'Found in lookup table', 'Lookup match',
                 'Lookup mismatch', 'Not found in lookup table', 'Identity match', 'Identity mismatch']
test_counts = dict.fromkeys(test_outcomes, 0)

accuracies = {}

# Training: read training data and populate lemma counters

train_data = open(train_file, 'r')

for line in train_data:

    # Tab character identifies lines containing tokens
    if re.search('\t', line):

        # Tokens represented as tab-separated fields
        field = line.strip().split('\t')

        # Word form in second field, lemma in third field
        form = field[1]
        lemma = field[2]

        ######################################################
        ### Insert code for populating the lemma counts    ###
        ######################################################
        if lemma_count.get(form) == None:
            lemma_count[form] = {lemma: 1}
        else:
            if lemma_count.get(form).get(lemma) == None:
                lemma_count[form][lemma] = 1
            else:
                lemma_count[form][lemma] += 1

        # Increment wordform tokens.
        training_counts['Wordform tokens'] += 1

# Model building and training statistics

for form in lemma_count.keys():

    ######################################################
    ### Insert code for building the lookup table      ###
    ######################################################
    max_lemma_val = [k for k, v in lemma_count[form].items(
    ) if v == max(lemma_count[form].values())]

    lemma_max[form] = max_lemma_val[0]
    ######################################################
    ### Insert code for populating the training counts ###
    ######################################################
    if len(lemma_count[form]) > 1:
        training_counts['Ambiguous most common tokens'] += max(
            lemma_count[form].values())
        training_counts['Ambiguous tokens'] += sum(lemma_count[form].values())
        training_counts['Ambiguous types'] += 1

        # Identity token
        if form in lemma_count[form]:
            training_counts['Identity tokens'] += lemma_count[form][form]
    else:
        training_counts['Unambiguous types'] += 1
        training_counts['Unambiguous tokens'] += sum(
            lemma_count[form].values())

        # Identity token
        if form in lemma_count[form]:
            training_counts['Identity tokens'] += list(
                lemma_count[form].values())[0]

training_counts['Wordform types'] = len(lemma_count)
# Calculate expected accuracy if we used lookup on all items ###
accuracies['Expected lookup'] = ((training_counts['Unambiguous tokens'] +
                                  training_counts['Ambiguous most common tokens']) / training_counts['Wordform tokens'])

# Calculate expected accuracy if we used identity mapping on all items ###
accuracies['Expected identity'] = training_counts['Identity tokens'] / \
    training_counts['Wordform tokens']

# Testing: read test data, and compare lemmatizer output to actual lemma

test_data = open(test_file, 'r')

for line in test_data:

    # Tab character identifies lines containing tokens
    if re.search('\t', line):

        # Tokens represented as tab-separated fields
        field = line.strip().split('\t')

        # Word form in second field, lemma in third field
        form = field[1]
        lemma = field[2]

        ######################################################
        ### Insert code for populating the test counts     ###
        ######################################################
        if form in lemma_max:
            predicted_lemma = lemma_max[form]
            if predicted_lemma == lemma:
                test_counts['Lookup match'] += 1
            else:
                test_counts['Lookup mismatch'] += 1
            # Increment  'Found in lookup table'
            test_counts['Found in lookup table'] += 1
        else:
            predicted_lemma = form
            if predicted_lemma == lemma:
                test_counts['Identity match'] += 1
            else:
                test_counts['Identity mismatch'] += 1
            # Increment 'Not found in lookup table'
            test_counts['Not found in lookup table'] += 1

        # Finally Increment 'Total test items'
        test_counts['Total test items'] += 1

# Calculate accuracy on the items that used the lookup table ###
accuracies['Lookup'] = test_counts['Lookup match'] / \
    test_counts['Found in lookup table']

# Calculate accuracy on the items that used identity mapping ###
accuracies['Identity'] = test_counts['Identity match'] / \
    test_counts['Not found in lookup table']

accuracies['Overall'] = (test_counts['Lookup match'] +
                         test_counts['Identity match']) / test_counts['Total test items']

# Report training statistics and test results

output = open('lookup-output.txt', 'w')

output.write('Training statistics\n')

for stat in training_stats:
    output.write(stat + ': ' + str(training_counts[stat]) + '\n')

for model in ['Expected lookup', 'Expected identity']:
    output.write(model + ' accuracy: ' + str(accuracies[model]) + '\n')

output.write('Test results\n')

for outcome in test_outcomes:
    output.write(outcome + ': ' + str(test_counts[outcome]) + '\n')

for model in ['Lookup', 'Identity', 'Overall']:
    output.write(model + ' accuracy: ' + str(accuracies[model]) + '\n')

output.close
