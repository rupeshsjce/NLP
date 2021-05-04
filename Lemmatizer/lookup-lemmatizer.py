import sys
import re

# Global variables

# Paths for data are read from command line
train_file = sys.argv[1]
test_file = sys.argv[2]
#train_file = UD_Hindi-HDTB-master/hi_hdtb-ud-train.conllu
#test_file = UD_Hindi-HDTB-master/hi_hdtb-ud-test.conllu

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
        training_counts['Wordform tokens'] += 1

        # form has not been seen before
        if lemma_count.get(form) == None:
            lemma_count[form] = {lemma: 1}

        else:  # form has been seen before
            # lemma has not been seen before
            if lemma_count.get(form).get(lemma) == None:
                lemma_count[form][lemma] = 1
            else:  # lemma has been seen before
                lemma_count[form][lemma] += 1
training_counts['Wordform types'] = len(lemma_count)

# Model building and training statistics

for key in lemma_count.keys():
    value = lemma_count[key]
    print("value :", value)
    ######################################################
    ### Insert code for building the lookup table      ###
    ######################################################
    lemma_max_val = max(value, key=lambda key: value[key])
    lemma_max[key] = lemma_max_val
    print("key/form  is {} and it's most probable lemma is {} ".format(key, lemma_max_val))

    ######################################################
    ### Insert code for populating the training counts ###
    ######################################################
    if len(value) > 1:
        training_counts['Ambiguous tokens'] += sum(value.values())
        training_counts['Ambiguous types'] += 1
        training_counts['Ambiguous most common tokens'] += max(value.values())

        # check if its an identity token
        if key in value:
            training_counts['Identity tokens'] += value[key]
    else:
        training_counts['Unambiguous tokens'] += sum(value.values())
        training_counts['Unambiguous types'] += 1

        # check if its an identity token
        if key in value:
            training_counts['Identity tokens'] += sum(value.values())

### Calculate expected accuracy if we used lookup on all items ###
accuracies['Expected lookup'] = ((training_counts['Unambiguous tokens'] +
                                  training_counts['Ambiguous most common tokens']) / training_counts['Wordform tokens'])

### Calculate expected accuracy if we used identity mapping on all items ###
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
        lemma_true = field[2]

        ######################################################
        ### Insert code for populating the test counts     ###
        ######################################################
        test_counts['Total test items'] += 1

        if form in lemma_max:
            lemma_predict = lemma_max[form]
            test_counts['Found in lookup table'] += 1
            if lemma_predict == lemma_true:
                test_counts['Lookup match'] += 1
            else:
                test_counts['Lookup mismatch'] += 1
        else:
            lemma_predict = form
            test_counts['Not found in lookup table'] += 1
            if lemma_predict == lemma_true:
                test_counts['Identity match'] += 1
            else:
                test_counts['Identity mismatch'] += 1

### Calculate accuracy on the items that used the lookup table ###
accuracies['Lookup'] = test_counts['Lookup match'] / \
    test_counts['Found in lookup table']

### Calculate accuracy on the items that used identity mapping ###
accuracies['Identity'] = test_counts['Identity match'] / \
    test_counts['Not found in lookup table']

### Calculate overall accuracy ###
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

output.close()
