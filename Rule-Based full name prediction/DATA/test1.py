import os
import sys
from IPython.core.interactiveshell import InteractiveShell
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 1000)

InteractiveShell.ast_node_interactivity = "all"


def printAccuracy():
    key_file = 'dev-key.csv'
    output_file = 'full-name-output1.csv'
    key_lines = open(key_file, 'r')
    output_lines = open(output_file, 'r')
    count, total = 0, 0
    for line1, line2 in zip(key_lines, output_lines):
        total = total + 1
        #print(line1 + " XXXXX " + line2)
        if line1 == line2:
            count = count + 1
            # print("SAME : " + line1, line2)

    print("Accuracy = ", count/total*100)
    return None


# Add 0 token from name2 : if len(name1 >=2) AND name1[-1] is the lastname (Rank of lastname > 150)
# Add 1 token from name2 : if name1[-1] is not the lastname AND name2[-2] is not the lastname AND name2[-1] is the lastname. (len(name2)>=2)
# Add 2 token from name2 : if name1[-1] is not the lastname AND both name2[-2] and name2[-1] are the lastname. (len(name2)>=3)

def predict(name1, name2, gender_dicts, surname_dict):
    rank_thresohlod = 1000
    print("NAMES : " + name1 + " AND " + name2)
    # dict Value; if not present then None
    name1lastwordvalue = surname_dict.get(name1.split()[-1])
    name2lastwordvalue = surname_dict.get(name2.split()[-1])
    name2secondlastwordvalue = surname_dict.get(name2.split()[-2])

    print("Values of  name1lastwordvalue, name2secondlastwordvalue, name2lastwordvalue : ",
          name1lastwordvalue, name2secondlastwordvalue, name2lastwordvalue)

    # print(name1, len(name1.split()), name1.split()[-1], name1lastwordvalue)
    # print(name2, len(name2.split()))
    # name1lastwordvalue = surname_dict.get(name1.split()[-1]) # dict Value; if not present then None
    if len(name1.split()) >= 2 and name1lastwordvalue is not None and name1lastwordvalue < rank_thresohlod:
        print("COND1 : " + name1)
        return name1

    # print(name1lastwordvalue, len(name2.split()),
    #       name2secondlastwordvalue, name2lastwordvalue)
    if (name1lastwordvalue is None or name1lastwordvalue > rank_thresohlod) and len(name2.split()) >= 2 and (name2secondlastwordvalue is None or name2secondlastwordvalue > rank_thresohlod) and (name2lastwordvalue is not None and name2lastwordvalue < rank_thresohlod):
        print("COND2 : " + name1 + " " + name2.split()[-1])
        return name1 + " " + name2.split()[-1]

    # and (name2lastwordvalue is not None and name2lastwordvalue < rank_thresohlod):
    if (name1lastwordvalue is None or name1lastwordvalue > rank_thresohlod) and len(name2.split()) >= 2 and (name2secondlastwordvalue is not None and name2secondlastwordvalue < rank_thresohlod):
        print("COND3 : " + name1 + " " + name2.split()
              [-2] + " " + name2.split()[-1])
        return name1 + " " + name2.split()[-2] + " " + name2.split()[-1]

    print("NONE CONDITION :", name1)
    return name1


# setting up path to the data file
PATH = os.path.abspath('')
#PATH = os.path.join(PATH, 'DATA')
names = 'dev-key.csv'

# read in the data as panda dataframe
df = pd.read_csv(os.path.join(PATH, names))
print(df.sample(5))
# df.head(10)
# df

#DRIVER - PREPROCESSING
# Create dicts of male and female names with key = name, value = percent

# PARAMETERS
female_file = 'dist.female.first.txt'
male_file = 'dist.male.first.txt'
surname_file = 'Names_2010Census.csv'

gender_files = [female_file, male_file]
gender_dicts = [dict(), dict()]


# Build 2 dictionary: One for female and other for male (key=name, value = percent)
for file, d in zip(gender_files, gender_dicts):
    fd = open(file, 'r')
    lines = fd.readlines()
    # print(lines)
    for line in lines:
        line = line.split()  # split with space by default
        name = line[0]
        percent = float(line[1])
        d[name] = percent


# Create surname_dict where key = lastname, value = rank
surname_dict = {}
fd = open(surname_file, 'r')
lines = fd.readlines()
# print(lines)
for line in lines[1:]:
    line = line.split(',')
    surname_dict[line[0]] = int(line[1])


# Add 0 token from name2 : if len(name1 >=2) AND name1[-1] is the lastname (Rank of lastname > 150)
# Add 1 token from name2 : if name1[-1] is not the lastname AND name2[-2] is not the lastname AND name2[-1] is the lastname. (len(name2)>=2)
# Add 2 token from name2 : if name1[-1] is not the lastname AND both name2[-2] and name2[-1] are the lastname. (len(name2)>=3)


dev_file = 'dev-test.csv'
fd = open(dev_file, 'r')
lines = fd.readlines()
count = 0
for line in lines:
    count = count + 1
    #print("line : ",line)
    line = line.split(' AND ')
    print(line[0] + "====" + line[1])
    tokens = line[0].split(' ')
    print(tokens)
    print("++++++++++++++++++")
    if count > 5:
        break


# test_file = sys.argv[1] # Read from command line
test_file = 'dev-test.csv'
output = open('full-name-output1.csv', 'w')
test_lines = open(test_file, 'r')
for line in test_lines:
    line = line.strip()  # Remove newline character
    [first_person, second_person] = line.split(' AND ')
    # predicted_first_person = first_person  # Simple and mostly wrong
    predicted_first_person = predict(
        first_person, second_person, gender_dicts, surname_dict)
    output.write(line + ',' + predicted_first_person + '\n')
output.close


# Calculate  and print the accuracy.
printAccuracy()
