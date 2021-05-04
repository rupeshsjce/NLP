
"""
2. The name lists are strictly optional: you do not need to use them at all.
I wrote a solution that gets around 85% accuracy on the development data without using the name lists.
Using only the first column in the lists of forenames (names only, no numbers, and no surnames) I am able to boost accuracy to 89%.
I have not yet found a way to use the numbers to improve on that result, but I haven't spent much time on this;
I will keep working on the problem, and will let you know if the reference solution goes higher.
"""
import sys
import csv
import numpy as np
import math 

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
                if debug: print("key file    : ",line1)
                if debug: print("output file : ",line2)
                total = total + 1
                if line1 == line2:
                    count = count + 1
                    # print("SAME : " + line1, line2)
                else:
                    if debug: print("NOT SAME : \n" + line1 +"\n" + line2)
                if debug: print("*"*80)    
                
    if total == 0: total = 1000
    print("Accuracy for name.length {} is {}".format(name1_length, count/total*100))
    print("Total = ", total)
    return None


#NAME CLASS
class name_obj():
    '''Represents all attributes of a given name. For use on name_one and name_two.
    Attributes: full_name, title, name, first_name, gender, lastname_yn '''
    def __init__(self, name_one, rank_thresh):
        self.full_name = name_one
        self.title, self.name = self.check_title(self.full_name, titles)
        self.first_name = self.name[0]
        self.gender = self.firstname_gender(self.name)
        self.lastname_xn = self.has_lastname_n(self.name, rank_thresh, -2)
        self.lastname_yn = self.has_lastname_n(self.name, rank_thresh, -1)

    def check_title(self, name_one, titles):
        if name_one[0] in titles:
            title = [name_one[0]]
            name_one = name_one[1:]
            return title, name_one
        else:
            title = ''
            return title, name_one
    
    def firstname_gender(self, name_one):
        '''Classify if first_name has gender = 'male' | 'female'
        Called within name class.'''
        #get female likelihood
        female_percent = gender_dicts[0].get(name_one[0])
        if female_percent == None: female_percent = 0

        #get male likelihood
        male_percent = gender_dicts[1].get(name_one[0])
        if male_percent == None: male_percent = 0

        #Check which likelihood is higher
        if female_percent >= male_percent: gender = 'female'
        else: gender = 'male'
        return gender

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
        

    def lastname_token_perc(self, name):
        '''return prob/percentage of name from surname'''
   
        if name in surname_dict:
            last_name_perc = surname_dict1.get(name)
            if last_name_perc == None: return 0.000001
            else: return last_name_perc
        else:
            return 0.000001
    
    def has_lastname_n(self, name_one, rank_thresh, pos):
        '''Checks if last word in name is a last_name
        rank_thresh (int) - the rank threshold under which to consider valid last names
        NOTE: There are around 162K last names in total'''
        if len(name_one) == 1:
            return 0
        else:
            if name_one[pos] in surname_dict:
                last_name_rank = surname_dict.get(name_one[pos])
                if last_name_rank < rank_thresh:
                    return 1
                else: return 0 
            else: return 0

#FUNCTIONS - OUTCOMES TO APPLY
add_last_name = lambda name_one, name_two : ' '.join(name_one + [name_two[-1]])
add_last_two_name = lambda name_one, name_two : ' '.join(name_one + name_two[-2:])
add_nothing = lambda name_one : ' '.join(name_one)


def predict1(name_one, name_two, gender_dicts, surname_dict):
    result = add_nothing(name_one.name)
    # CASE-1
    if len(name_one.name) == 1:
        # max of name1[-1] name2[-1], name1[-1] name2[-2] name2[-1] OR
        # name2[-2] is firstName or lastName. If firstName% >=  lastName% then add_last_only else add_last_two
        #print("NAME1 and NAME2 : ",name_one.full_name, name_two.full_name)
        #print(name_two.firstname_nametoken_perc(name_two.full_name[-2]))
        #print(name_two.lastname_token_perc(name_two.full_name[-2]))

        if len(name_two.name) == 4:
            result = add_last_two_name(name_one.name, name_two.name)
            return result
        elif len(name_two.name) == 3:
            result = add_last_name(name_one.name, name_two.name)
            return result
            
        elif name_two.firstname_nametoken_perc(name_two.full_name[-2]) >= name_two.lastname_token_perc(name_two.full_name[-2]):
            result = add_last_name(name_one.name, name_two.name)
            return result
        else:
            result = add_last_two_name(name_one.name, name_two.name)
            return result

    # CASE-2
    result = name_one.full_name    #default
    epsilon = 0.0000002

    if len(name_one.name) == 2:
        
        a = name_one.lastname_token_perc(name_one.full_name[-1])
    
        b = name_two.lastname_token_perc(name_two.full_name[-2]) * \
            name_two.lastname_token_perc(name_two.full_name[-1])
           
        c = name_two.lastname_token_perc(name_two.full_name[-1])

        print("argmax : ", a,b,c)
        #abc_list = [a,c]
        #idx = np.argmax(abc_list)
        if len(name_two.name) == 4:
            result = add_last_two_name(name_one.name, name_two.name)
            """
            if a > 0.03:
                result = add_nothing(name_one.name)
            else:    
                result = add_last_two_name(name_one.name, name_two.name)
            """    
        elif len(name_two.name) == 2:
            if a > 0.03:
                result = add_nothing(name_one.name)
            else:
                result = add_last_name(name_one.name, name_two.name)
        elif len(name_two.name) == 3:
            if a > 0.03:
                result = add_nothing(name_one.name)
            else:    
                result = add_last_name(name_one.name, name_two.name)
            
            
        elif a > c:
            result = add_nothing(name_one.name)
        else:
            if b < c:
                result = add_last_name(name_one.name, name_two.name)
            else:
                result = add_last_two_name(name_one.name, name_two.name)         
        
    """
    if len(name_one.name) == 2:
        print("NAME1 and NAME2 : ",name_one.full_name, name_two.full_name)
        
        if len(name_two.name) == 4: 
                result = add_last_two_name(name_one.name, name_two.name) 
        if len(name_two.name) == 3:
            # max of name1[-1].SN, name1[-1].FN * name2[-2].SN * name2[-1].SN, name1[-1].FN * name2[-1].SN
            ""
            a = math.log(name_one.lastname_token_perc(name_one.full_name[-1])+epsilon,2)
            b = math.log(name_one.firstname_nametoken_perc(name_one.full_name[-1])+epsilon,2) + \
                math.log(name_two.lastname_token_perc(name_two.full_name[-2])+epsilon,2) + \
                math.log(name_two.lastname_token_perc(name_two.full_name[-1])+epsilon,2)
            c = math.log(name_one.firstname_nametoken_perc(name_one.full_name[-1])+epsilon,2) + \
                math.log(name_two.lastname_token_perc(name_two.full_name[-1])+epsilon,2)
            ""
            a = name_one.lastname_token_perc(name_one.full_name[-1])
            b = name_one.firstname_nametoken_perc(name_one.full_name[-1]) * \
                name_two.lastname_token_perc(name_two.full_name[-2]) * \
                name_two.lastname_token_perc(name_two.full_name[-1])
            c = name_one.firstname_nametoken_perc(name_one.full_name[-1]) * \
                name_two.lastname_token_perc(name_two.full_name[-1])
            print("argmax : ", a,b,c)
            abc_list = [a,b,c]
            idx = np.argmax(abc_list)                      
            if idx == 0:
                result = add_nothing(name_one.name)
            elif idx == 1:
                result = add_last_two_name(name_one.name, name_two.name)
            elif idx == 2:
                result = add_last_name(name_one.name, name_two.name)   

        if len(name_two.name) == 2:
            # max of name1[-1].SN, name1[-1].FN * name2[-1].SN
            a = name_one.lastname_token_perc(name_one.full_name[-1])
            ""
            c = name_one.firstname_nametoken_perc(name_one.full_name[-1]) * \
                name_two.lastname_token_perc(name_two.full_name[-1])
            ""   
            c = name_two.lastname_token_perc(name_two.full_name[-1])
            print("argmax : ", a,c)
            abc_list = [a,c]
            idx = np.argmax(abc_list)                      
            if idx == 0:
                result = add_nothing(name_one.name)
            elif idx == 1:
                result = add_last_name(name_one.name, name_two.name)
    """            
    return result       


#FUNCTIONS - RULES
def predict(name_one, name_two, gender_dicts, surname_dict):
    '''Rules used to predict the full name of name_one
    name_one <obj> - represented as a class_obj
    name_two <obj> - represented as a class_obj'''
    result = add_nothing(name_one.name)
    # CASE-1
    if len(name_one.name) == 1:
        # max of name1[-1] name2[-1], name1[-1] name2[-2] name2[-1] OR
        # name2[-2] is firstName or lastName. If firstName% >=  lastName% then add_last_only else add_last_two
        #print("NAME1 and NAME2 : ",name_one.full_name, name_two.full_name)
        #print(name_two.firstname_nametoken_perc(name_two.full_name[-2]))
        #print(name_two.lastname_token_perc(name_two.full_name[-2]))

        if len(name_two.name) == 4:
            result = add_last_two_name(name_one.name, name_two.name)
            return result
        elif len(name_two.name) == 3:
            result = add_last_name(name_one.name, name_two.name)
            return result
            
        elif name_two.firstname_nametoken_perc(name_two.full_name[-2]) >= name_two.lastname_token_perc(name_two.full_name[-2]):
            result = add_last_name(name_one.name, name_two.name)
            return result
        else:
            result = add_last_two_name(name_one.name, name_two.name)
            return result

    # CASE-2
    result = name_one.full_name    #default
    epsilon = 0.0000002

    if len(name_one.name) == 2:
        
        a = name_one.lastname_token_perc(name_one.full_name[-1])
    
        b = name_two.lastname_token_perc(name_two.full_name[-2]) * \
            name_two.lastname_token_perc(name_two.full_name[-1])
           
        c = name_two.lastname_token_perc(name_two.full_name[-1])

        print("argmax : ", a,b,c)
        #abc_list = [a,c]
        #idx = np.argmax(abc_list)
        if len(name_two.name) == 4:
            result = add_last_two_name(name_one.name, name_two.name)
            return result
            """
            if a > 0.03:
                result = add_nothing(name_one.name)
                return result
            else:    
                result = add_last_two_name(name_one.name, name_two.name)
                return result
            """    
        elif len(name_two.name) == 2:
            if a > 0.03:
                result = add_nothing(name_one.name)
                return result
            else:
                result = add_last_name(name_one.name, name_two.name)
                return result
        elif len(name_two.name) == 3:
            if a > 0.05: #predict-2-3-case
                result = add_nothing(name_one.name)
                return result
            else:    
                result = add_last_name(name_one.name, name_two.name)
                return result
        """    
        elif len(name_two.name) == 3:
            b = name_two.lastname_token_perc(name_two.full_name[-2])
            if a > 0.05: #predict-2-3-case
                result = add_nothing(name_one.name)
                return result
            elif b > 0.01 and b > c:
                result = add_last_two_name(name_one.name, name_two.name)
                return result
            else:    
                result = add_last_name(name_one.name, name_two.name)
                return result
        """            


    elif len(name_one.name) >= 3: #Accuracy =  96.11650485436894, Total =  206
        result = add_nothing(name_one.name)
        #print('rule 3.1')
        return result

#DRIVER - PREPROCESSING
#Create dicts of male and female names with key = name, value = percent

#PARAMETERS
female_file = 'dist.female.first.txt'
male_file = 'dist.male.first.txt'
surname_file = 'Names_2010Census.csv'

gender_files = [female_file, male_file]
gender_dicts = [dict(), dict()]

for file, d in zip(gender_files, gender_dicts):
    fd = open(file, 'r')
    lines = fd.readlines()
    for line in lines:
        line = line.split()
        name = line[0]
        percent = float(line[1])
        d[name] = percent

#Create surname_dict where key = lastname, value = rank
surname_dict = {}
fd = open(surname_file, 'r')
lines = fd.readlines()
for line in lines[1:]:
    line = line.split(',')
    surname_dict[line[0]] = int(line[1])

#Create surname_dict where key = lastname, value = rank
surname_dict1 = {}
surname_file1 = 'dist.all.last.txt'
fd = open(surname_file1, 'r')
lines = fd.readlines()
for line in lines:
    line = line.split()
    surname_dict1[line[0]] = float(line[1])    
    

#DRIVER - MAIN
#PARAMETERS
rank_thresh = 320
titles = {'REVEREND', 'DOCTOR', 'PROFESSOR'}

#Pull out arguments from command line
test_file = sys.argv[1]
output_file = 'full-name-output.csv'

#Open the test file
fd = open(test_file, 'r')
lines = fd.readlines()

#PREDICT
with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    for line in lines:
        #Parse each name into a list, combine into a list of lists
        line = line.strip()
        name_list_str = line.split(' AND ')

        #Create a name object for name_one and name_two
        #Name object consists of: full_name, title, name, first_name, gender, lastname_yn
        name_objects = []
        for idx, name in enumerate(name_list_str):
            name_list = name.split(' ')
            name_object = name_obj(name_list, rank_thresh)
            name_objects.append(name_object)

        name_one = name_objects[0]
        name_two = name_objects[1]
        result = predict(name_one, name_two, gender_dicts, surname_dict)
        result_final = [line, result]
        #print("result_final : ", result_final)
        writer.writerow(result_final)

printPartAccuracy(1, 0,False) #1,2=96 1,3=94 1,4=95 == 95
printPartAccuracy(2, 3, True) #2,2=82 2-3=72(316) 2,4=72(42) == 75
printPartAccuracy(3, 0, False)
printPartAccuracy(4, 0, False)
printAccuracy(False)
