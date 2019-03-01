#!/bin/python3

import csv

"""
TODO: 
1) Encapsulate in class
2) Add parameter for a list of values recognized as "blank" (i.e. "NULL", None, 0, "")
3) Add methods for analyzing and returning more stats than blank columns

"""

headers = dict()

with open('sorted.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        for k, v in row.items():
            if k not in headers.keys():
                headers[k] = 'BLANK COLUMN FOUND'
            if headers[k] == 'BLANK COLUMN FOUND':
                if v:
                    headers[k] = v

total_headers = []
blank_headers = []
used_headers = []

for k, v in headers.items():
    print('{}: {}'.format(k, v))
    total_headers.append(k)
    if v == 'BLANK COLUMN FOUND':
        blank_headers.append(k)
    else:
        used_headers.append(k)

print('-'*120)

print('Number of Total Headers: {}'.format(len(total_headers)))
print('Number of Used Headers: {}'.format(len(used_headers)))
print('Number of Blank Headers: {}'.format(len(blank_headers)))
