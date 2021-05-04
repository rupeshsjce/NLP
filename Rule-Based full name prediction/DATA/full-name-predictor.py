import sys
import csv

rankLimit = 320


def add_last_token(name_one, name_two):
    return ' '.join(name_one + [name_two[-1]])


def add_last_two_token(name_one, name_two):
    return ' '.join(name_one + name_two[-2:])


def add_nothing(name_one):
    return ' '.join(name_one)


def printAccuracy(debug):
    key_file = 'dev-key.csv'
    output_file = 'full-name-output.csv'
    key_lines = open(key_file, 'r')
    output_lines = open(output_file, 'r')
    count, total = 0, 0
    for line1, line2 in zip(key_lines, output_lines):
        line1 = line1.strip()
        line2 = line2.strip()
        if debug:
            print("key file    : ", line1)
        if debug:
            print("output file : ", line2)
        total = total + 1
        if line1 == line2:
            count = count + 1
            # print("SAME : " + line1, line2)
        else:
            if debug:
                print("NOT SAME : \n" + line1 + "\n" + line2)
        if debug:
            print("*"*80)

    print("Overall Accuracy = ", count/total*100)
    print("Total = ", total)
    return None


def printPartAccuracy(name1_length, name2_length, debug):
    key_file = 'dev-key.csv'
    output_file = 'full-name-output.csv'
    key_lines = open(key_file, 'r')
    output_lines = open(output_file, 'r')
    count, total = 0, 0
    for line1, line2 in zip(key_lines, output_lines):
        line1 = line1.strip()
        line2 = line2.strip()
        if len(line1.split(' AND ')[0].split()) == name1_length:
            if name2_length == 0 or len(line1.split(' AND ')[1].split(',')[0].split()) == name2_length:
                #if debug: print("key file    : ",line1)
                #if debug: print("output file : ",line2)
                total = total + 1
                if line1 == line2:
                    count = count + 1
                    # print("SAME : " + line1, line2)
                else:
                    if debug:
                        print("NOT SAME : \n" + line1 + "\n" + line2)
                    if debug:
                        print("*"*80)
                #if debug: print("*"*80)

    if total == 0:
        total = 1000
    print("Accuracy for name.length {} is {}".format(
        name1_length, count/total*100))
    print("Total = ", total)
    return None


class nameObj():
    def __init__(self, name_one):
        self.full_name = name_one
        #self.name = name_one
        self.title, self.name = self.check_title(self.full_name, titles)

    def check_title(self, name_one, titles):
        if name_one[0] in titles:
            title = [name_one[0]]
            name_one = name_one[1:]
            return title, name_one
        else:
            title = ''
            return title, name_one

    def is_fn_presnt(self):
        '''return None if it is not found in (male/female firstname) dict'''

        femaleFN = gender_dicts[0].get(self.full_name[-1])
        if femaleFN is not None:
            return True

        maleFN = gender_dicts[1].get(self.full_name[-1])
        if maleFN is not None:
            return True
        return False


def predict(name_one, name_two, gender_dicts):
    result = add_nothing(name_one.full_name)
    # CASE-1
    if len(name_one.name) == 1:
        if len(name_two.name) == 4:
            result = add_last_two_token(name_one.full_name, name_two.name)
            return result
        else:
            result = add_last_token(name_one.full_name, name_two.name)
            return result

    # CASE-2
    result = add_nothing(name_one.full_name)
    if len(name_one.name) == 2:
        if name_one.is_fn_presnt():
            if len(name_two.name) == 2:
                result = add_last_token(name_one.full_name, name_two.name)
                return result
            elif len(name_two.name) == 4:
                result = add_last_two_token(name_one.full_name, name_two.name)
                return result
            else:
                result = add_last_token(name_one.full_name, name_two.name)
                return result

        else:
            result = add_nothing(name_one.full_name)
            return result
    # CASE REST
    elif len(name_one.name) >= 3:
        result = add_nothing(name_one.full_name)

    return result


# Declares variable for filenames
f_file = 'dist.female.first.txt'
m_file = 'dist.male.first.txt'
lastname_file = 'Names_2010Census.csv'

gender_files = [f_file, m_file]
gender_dicts = [dict(), dict()]

for file, d in zip(gender_files, gender_dicts):
    fd = open(file, 'r')
    lines = fd.readlines()
    for line in lines:
        line = line.split()
        name = line[0]
        percent = float(line[1])
        d[name] = percent


# DRIVER CODE
titles = {'REVEREND', 'DOCTOR', 'PROFESSOR', 'COLONEL'}
test_file = sys.argv[1]
output_file = 'full-name-output.csv'

fd = open(test_file, 'r')
lines = fd.readlines()

# PREDICT
with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    for line in lines:
        line = line.strip()
        name_list_str = line.split(' AND ')

        name_objects = []
        for idx, name in enumerate(name_list_str):
            name_list = name.split(' ')
            name_object = nameObj(name_list)
            name_objects.append(name_object)

        name_one = name_objects[0]
        name_two = name_objects[1]
        result = predict(name_one, name_two, gender_dicts)
        result_final = [line, result]
        writer.writerow(result_final)

printPartAccuracy(1, 0, False)
printPartAccuracy(2, 0, False)
printPartAccuracy(3, 0, True)
printPartAccuracy(4, 0, False)
printAccuracy(False)
