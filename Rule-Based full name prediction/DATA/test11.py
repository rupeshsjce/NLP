import csv

key_file = 'dev-key.csv'
key_lines = open(key_file, 'r')

for line1 in key_lines:
    names = line1.split(',')
    print(names[0])
    print(len(names[1].split()))
    break
