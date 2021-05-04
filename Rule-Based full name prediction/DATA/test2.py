
"""
2. The name lists are strictly optional: you do not need to use them at all.
I wrote a solution that gets around 85% accuracy on the development data without using the name lists.
Using only the first column in the lists of forenames (names only, no numbers, and no surnames) I am able to boost accuracy to 89%.
I have not yet found a way to use the numbers to improve on that result, but I haven't spent much time on this;
I will keep working on the problem, and will let you know if the reference solution goes higher.
"""
import sys
import csv
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


def printPartAccuracy(name1_length, debug):
    key_file = 'dev-key.csv'
    output_file = 'full-name-output.csv'
    key_lines = open(key_file, 'r')
    output_lines = open(output_file, 'r')
    count, total = 0, 0
    for line1, line2 in zip(key_lines, output_lines):
        line1 = line1.strip()
        line2 = line2.strip()
        if len(line1.split(' AND ')[0].split()) == name1_length:
            if debug: print("key file    : ",line1)
            if debug: print("output file : ",line2)
            total = total + 1
            if line1 == line2:
                count = count + 1
                # print("SAME : " + line1, line2)
            else:
                if debug: print("NOT SAME : \n" + line1 +"\n" + line2)
            if debug: print("*"*80)    
                

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

#FUNCTIONS - RULES
def predict(name_one, name_two, gender_dicts, surname_dict):
    '''Rules used to predict the full name of name_one
    name_one <obj> - represented as a class_obj
    name_two <obj> - represented as a class_obj'''
    if len(name_one.name) == 1: # Accuracy =  82.22222222222221, Total =  270
        if len(name_two.name) >= 3 and name_two.lastname_xn == 1:
            result = add_last_two_name(name_one.name, name_two.name)
            return result
        elif len(name_two.name) >= 3 and name_two.lastname_xn == 0:
            result = add_last_name(name_one.name, name_two.name)
            return result 
        elif name_one.gender != name_two.gender or len(name_two.name) == 2:
        #elif len(name_two.name) == 2: #acc=70%
            result = add_last_name(name_one.name, name_two.name)
            #print('rule 1.1, 1.2, or 1.3')
            return result
        else:
            result = add_last_two_name(name_one.name, name_two.name)
            #print('rule 1.N')
            return result

    elif len(name_one.name) == 2: #Accuracy =  71.56488549618321, Total =  524
        #if name_one.lastname_yn == 1:
        if name_one.lastname_yn == 1: # or surname_dict.get(name_one.full_name[-1]):     
            result = add_nothing(name_one.name)
            #print('rule 2.1')
            return result
    
        elif len(name_two.name) == 4: # and name_two.lastname_yn == 1: # New addition (add last two when name2[-1].rank > 150)
            result = add_last_two_name(name_one.name, name_two.name)
            return result
        elif len(name_two.name) == 3 and name_two.lastname_xn == 1: #and name_two.full_name[-2] in surname_dict and surname_dict.get(name_two.full_name[-2])
            result = add_last_two_name(name_one.name, name_two.name)
            return result
        elif len(name_two.name) == 3 and name_two.lastname_xn == 0 and name_two.lastname_yn == 1:
            result = add_last_name(name_one.name, name_two.name)
            return result
        
        else:
            #result = add_nothing(name_one.name)
            result = add_last_name(name_one.name, name_two.name)
            #print('rule 2.N')
            return result
           

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
        writer.writerow(result_final)

printPartAccuracy(1,False)
printPartAccuracy(2, False)
printPartAccuracy(3, False)
printPartAccuracy(4, False)
printAccuracy(False)
