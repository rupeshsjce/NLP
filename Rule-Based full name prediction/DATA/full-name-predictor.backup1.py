import sys
import csv
"""
import numpy as np
import math 
"""
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
        if debug: print("key file    : ",line1)
        if debug: print("output file : ",line2)
        total = total + 1
        if line1 == line2:
            count = count + 1
            # print("SAME : " + line1, line2)
        else:
            if debug: print("NOT SAME : \n" + line1 +"\n" + line2)
        if debug: print("*"*80)    
                

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
            if name2_length ==0  or len(line1.split(' AND ')[1].split(',')[0].split()) == name2_length:
                #if debug: print("key file    : ",line1)
                #if debug: print("output file : ",line2)
                total = total + 1
                if line1 == line2:
                    count = count + 1
                    # print("SAME : " + line1, line2)
                else:
                    if debug: print("NOT SAME : \n" + line1 +"\n" + line2)
                    if debug: print("*"*80)
                #if debug: print("*"*80)    
                
    if total == 0: total = 1000
    print("Accuracy for name.length {} is {}".format(name1_length, count/total*100))
    print("Total = ", total)
    return None


class nameObj():
    def __init__(self, name_one):
        self.full_name = name_one
        self.name = name_one
        self.lastname_xn = self.has_lastname_n(self.full_name, -2)
        self.lastname_yn = self.has_lastname_n(self.full_name, -1)

    def firstname_nametoken_perc(self, name):
        '''return max prob of name from male and female dict'''
        #get female likelihood
        female_percent = gender_dicts[0].get(name)
        if female_percent == None: female_percent = 0.000001

        #get male likelihood
        male_percent = gender_dicts[1].get(name)
        if male_percent == None: male_percent = 0.000001

        #Check which likelihood is higher
        if female_percent >= male_percent:
            return female_percent
        else:
            return male_percent

    def is_fn_presnt(self):
        print("is_fn_present : ", self.full_name[-1])
        '''return None if it is not found in dict'''
      
        femaleFN = gender_dicts[0].get(self.full_name[-1])
        if femaleFN is not None: return True

        maleFN = gender_dicts[1].get(self.full_name[-1])
        if maleFN is not None: return True
        print("[FALSE] is_fn_present : ", self.full_name[-1]) 
        return False



    def lastname_token_perc(self, name):
        '''return prob/percentage of name from surname'''
   
        if name in lastname_dict:
            last_name_perc = lastname_dict1.get(name)
            if last_name_perc == None: return 0.000001
            else: return last_name_perc
        else:
            return 0.000001
    
    def has_lastname_n(self, name_one, pos):
        if len(name_one) == 1:
            return 0
        else:
            if name_one[pos] in lastname_dict:
                last_name_rank = lastname_dict.get(name_one[pos])
                if last_name_rank < rankLimit:
                    return 1
                else: return 0 
            else: return 0


def predict(name_one, name_two, gender_dicts, surname_dict):
    result = add_nothing(name_one.full_name)
    # CASE-1
    if len(name_one.full_name) == 1:
        if len(name_two.name) == 4:
            result = add_last_two_token(name_one.name, name_two.name)
            return result
        elif len(name_two.name) == 3:
            result = add_last_token(name_one.name, name_two.name)
            return result
            
        elif name_two.firstname_nametoken_perc(name_two.full_name[-2]) >= name_two.lastname_token_perc(name_two.full_name[-2]):
            result = add_last_token(name_one.name, name_two.name)
            return result
        else:
            result = add_last_two_token(name_one.name, name_two.name)
            return result

    # CASE-2
    #result = name_one.full_name    #default
    epsilon = 0.0000002
    result = add_nothing(name_one.full_name)
    if len(name_one.full_name) == 2:
        if name_one.is_fn_presnt():
            if len(name_two.full_name) == 2:
                result = add_last_token(name_one.full_name, name_two.full_name)
                return result
            elif len(name_two.full_name) == 4:
                result = add_last_two_token(name_one.full_name, name_two.full_name)
                return result
            else:
                result = add_last_token(name_one.full_name, name_two.full_name)
                return result
                
        else:
            result = add_nothing(name_one.full_name)
            return result
            
                
                
            
        
        
    elif len(name_one.name) >= 3: #Accuracy =  96.11650485436894, Total =  206
        result = add_nothing(name_one.name)
        #print('rule 3.1')

    return result       

#Declares variable for filenames
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

"""
Create lastname_dict where key = lastname, value = rank
"""
lastname_dict = {}
fd = open(lastname_file, 'r')
lines = fd.readlines()
for line in lines[1:]:
    line = line.split(',')
    lastname_dict[line[0]] = int(line[1])

"""
Create lastname_dict where key = lastname, value = probability/frequency
"""
lastname_dict1 = {}
lastname_file1 = 'dist.all.last.txt'
fd = open(lastname_file1, 'r')
lines = fd.readlines()
for line in lines:
    line = line.split()
    lastname_dict1[line[0]] = float(line[1])    
    


#DRIVER CODE
"""
arguments from command line.
"""
test_file = sys.argv[1]
output_file = 'full-name-output.csv'
"""
open the test file for inputs
"""
fd = open(test_file, 'r')
lines = fd.readlines()

#PREDICT
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
        result = predict(name_one, name_two, gender_dicts, lastname_dict)
        result_final = [line, result]
        print("result_final : ", result_final)
        writer.writerow(result_final)

printPartAccuracy(1, 0,False) #1,2=96 1,3=94 1,4=95 == 95
printPartAccuracy(2, 0, False) #2,2=82 2-3=75 2,4=73.80 == 77
printPartAccuracy(3, 0, False)
printPartAccuracy(4, 0, False)
printAccuracy(False)
