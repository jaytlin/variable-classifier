# Loads training data from a .csv file and creates the decision tree for the dataset.
# Uses test data to calculate error of the decision tree.

import csv
import numpy as np
from sklearn.datasets import load_iris
from sklearn import tree

# read data in from .csv file
datafile = open('/Users/christopherli/Documents/AMPLab/data/training4.csv', 'rU')
datareader = csv.reader(datafile)
data = load_iris()
our_data = []
our_target = []

for row in datareader:
    if row != ['', '', '', '', '', '', '', ''] and row != ['name', 'dataset', 'category', '1_{no repeated values}', '1_{distinct values occur equally often}', '1_{regularly spaced intervals}', '1_{interval width divides range}', 'type']:
        our_data.append([row[3],row[4],row[5],row[6],row[7]])
        our_target.append(row[2])

# transfer data into ndarray
our_target_array = np.ndarray(shape=(len(our_data)))
our_data_array = np.ndarray(shape=(len(our_data),5))
data.target_names.resize(5,)
for i in range(len(our_data)):
    for j in range(5):

        # converting category to numerical label and recording respective target name
        # 0 is nominal
        # 1 is ordinal
        # 2 is real
        # 3 is id
        # 4 is time
        if our_target[i] == 'nominal':
            our_target_array[i] = 0
            data.target_names[0] = 'nominal'
        elif our_target[i] == 'ordinal':
            our_target_array[i] = 1
            data.target_names[1] = 'ordinal'
        elif our_target[i] == 'real':
            our_target_array[i] = 2
            data.target_names[2] = 'real'
        elif our_target[i] == 'id':
            our_target_array[i] = 3
            data.target_names[3] = 'id'
        elif our_target[i] == 'time':
            our_target_array[i] = 4
            data.target_names[4] = 'time'

            
        # converting type to numerical label
        # 0 is int
        # 1 is float
        # 2 is str
        if our_data[i][j] == 'int':
            our_data_array[i][j] = 0
        elif our_data[i][j] == 'float':
            our_data_array[i][j] = 1
        elif our_data[i][j] == 'str':
            our_data_array[i][j] = 2
        else:
            our_data_array[i][j] = our_data[i][j]

data.target = our_target_array
data.data = our_data_array
data.feature_names = ['1_{no repeated values}', '1_{distinct values occur equally often}', '1_{regularly spaced intervals}', '1_{interval width divides range}', 'type']

# create decision tree
clf = tree.DecisionTreeClassifier()
clf = clf.fit(data.data, data.target)

# change to pdf format
import StringIO
import os
with open('/Users/christopherli/Documents/AMPLab/data4.0.dot','w') as f:
    f = tree.export_graphviz(clf,out_file=f,feature_names=data.feature_names)

# use decision tree for testing 
# data.data[2,0] = 1.
# data.data[2,1] = 1.
# data.data[2,2] = 0.
# data.data[2,3] = 0.
# data.data[2,4] = 2.
# print clf.predict([data.data[2,:]])


