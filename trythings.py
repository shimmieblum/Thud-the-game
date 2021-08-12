import csv

from dataclasses import replace


with open('mctsData.txt', 'r') as o:
    lines = [[x.replace(' ','').replace('\n','') for x in line.split(',')] for line in o.readlines()]

with open('results.csv', 'w', newline='') as o:
       writer = csv.writer(o, delimiter = ',', )
       writer.writerows(lines)
       
       

    