# NLP

CSCI-544 Spring 2021.
Python Coding Assignments.

1. Full-name predictions : 

Overview
Person names in the English language typically consist of one or more forenames followed by one or more surnames (optionally preceded by zero or more titles and followed by zero or more suffixes). This situation can create ambiguity, as it is often unclear whether a particular name is a forename or a surname. For example, given the sequence Imogen and Andrew Lloyd Webber, it is not possible to tell what the full name of Imogen is, since that would depend on whether Lloyd is part of Andrew’s forename or surname (as it turns out, it is a surname: Imogen Lloyd Webber is the daughter of Andrew Lloyd Webber). This exercise explores ways of dealing with this kind of ambiguity.

You will write a program that takes a string representing the names of two persons (joined by and), and tries to predict the full name of the first person in the string. To develop your program, you will be given a set of names with correct solutions: these are not names of real people – rather, they have been constructed based on lists of common forenames and surnames. The names before the and are the first person’s forenames, any titles they may have, and possibly surnames; the names after the and are the second person’s full name. For each entry, your program will output its best guess as to the first person’s full name. The assignment will be graded based on accuracy, that is the number of names predicted correctly on an unseen dataset constructed the same way.


2. Building Lemmatizer :

Overview
In this assignment you will write a very simple lemmatizer, which learns a lemmatization function from an annotated corpus. The function is so basic I wouldn’t even consider it machine learning: it’s basically just a big lookup table, which maps every word form attested in the training data to the most common lemma associated with that form. At test time, the program checks if a form is in the lookup table, and if so, it gives the associated lemma; if the form is not in the lookup table, it gives the form itself as the lemma (identity mapping).

The program performs training and testing in one run: it reads the training data, learns the lookup table and keeps it in memory, then reads the test data, runs the testing, and reports the results. The program output is in a fixed format, reporting 15 counters and 5 performance measures. The assignment will be graded based on the correctness of these measures.

3. Sentiment Analysis on hotel reviews (naive bayes classifier):

Overview
In this assignment you will write a naive Bayes classifier to identify hotel reviews as either truthful or deceptive, and either positive or negative. You will be using the word tokens as features for classification. The assignment will be graded based on the performance of your classifiers, that is how well they perform on unseen test data compared to the performance of a reference classifier.

4. Sentiment Analysis on Hotel Reviews using perceptron :

Overview
In this assignment you will write perceptron classifiers (vanilla and averaged) to identify hotel reviews as either truthful or deceptive, and either positive or negative. You may use the word tokens as features, or any other features you can devise from the text. The assignment will be graded based on the performance of your classifiers, that is how well they perform on unseen test data compared to the performance of a reference classifier.

5. Part-of-speech tagging (POST) using Hidden Markov Model (HMM) :

Overview
In this assignment you will write a Hidden Markov Model part-of-speech tagger for Italian, Japanese, and a surprise language. The training data are provided tokenized and tagged; the test data will be provided tokenized, and your tagger will add the tags. The assignment will be graded based on the performance of your tagger, that is how well it performs on unseen test data compared to the performance of a reference tagger.

