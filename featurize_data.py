XMLDIR = '/Users/christopherli/Documents/AMPLab/data/'
TRAINING = '/Users/christopherli/Documents/AMPLab/data/training4.csv'
DOT = '/Users/christopherli/Documents/AMPLab/data_test.dot'
XML_SUFFIX = '.xml'

import os
from xml.dom import minidom
import numpy as np
import csv
import StringIO
from sklearn import tree

def main(args):
    xmldir = args.xmldir
    training = args.training
    dot = args.dot
    
    # computes tuples, imports target classification from training file, then creates decision tree
    data, target = run(xmldir,training,dot)
    return data, target
    
def run(xmldir, training, dot):
    xmlfiles = find_xmlfiles(xmldir)
    tuples = []
    for f in xmlfiles:
        tuples = tuples + process_variables(f)
        
    # create data array from tuples
    data = np.array(tuples)
    
    # designate feature names
    feature_names = get_feature_names()
        
    # import target classification from training file and create target array
    target = create_target(training)
    
    # create decision tree
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(data, target)
    
    # change to pdf format
    with open(dot,'w') as f:
        f = tree.export_graphviz(clf,out_file=f,feature_names=feature_names)
        
    return data, target
    
def find_xmlfiles(xmldir):
    # returns list of .xml files in the given directory "xmldir"
    for (dirpath, dirnames, filenames) in os.walk(xmldir):
        for filename in filenames:
            if is_xml(filename):
                yield dirpath + filename
                
def is_xml(f):
    # returns if file "f" is an .xml file
    return (f[-4:] == XML_SUFFIX)
    
def process_variables(f):
    # returns tuples of features for each variable in the .xml file "f"
    xmldoc = minidom.parse(f)
    features = []
    data = xmldoc.getElementsByTagName('data')
    for dataset in range(len(data)):
        variables = data[dataset].getElementsByTagName('variables')
        records = data[dataset].getElementsByTagName('records')[0]
        has_id = has_ids(records)
        if has_id == 'id' or has_id == 'label' or has_id == 'source':
            features.append(evaluate_features(has_id, 0, records))
            if has_id == 'source':
                features.append(evaluate_features('destination', 0, records))
        if there_are(variables):
            variable_number = 0
            for variable in variables[0].childNodes:
                if is_valid_variable(variable):
                    variable_number += 1
                    features.append(evaluate_features(variable, variable_number, records))
    return features
    
def has_ids(records):
    i=1
    try:
        while records.childNodes[i].nodeType is not 1: i += 1
        records.childNodes[i].attributes["source"].value
        return 'source'
    except:
        pass
    try:
        while records.childNodes[i].nodeType is not 1: i += 1
        records.childNodes[i].attributes["label"].value
        return 'label'
    except:
        pass
    try:
        while records.childNodes[i].nodeType is not 1: i += 1
        records.childNodes[i].attributes["id"].value
        return 'id'
    except:
        pass
    return ''
    
def there_are(things):
    # returns if there are any "things"
    return len(things) != 0
    
def is_valid_variable(variable):
    # checks if variable is a valid variable (element node, not a counter, not a randomuniform)
    return (variable.nodeType == 1 and variable.nodeName != 'countervariable' and variable.nodeName != 'randomuniformvariable')
    
def evaluate_features(variable, variable_number, records):
    # runs each feature test and returns the results for the variable
    missing = get_missing_value(records)
    distincts = {}
    distincts, total_missing = get_distinct_values(variable, variable_number, records, missing)
    
    var_type = get_var_type(distincts.keys()[0])
    total_distincts = len(distincts)
    no_rep_vals = no_repeated_values(records, total_distincts, total_missing)
    eq_occur = equal_occurrences(distincts)
    reg_ints = regular_intervals(distincts)
    if reg_ints:
        int_div_range = interval_divides_range(distincts)
    else:
        int_div_range = 0
    if variable_number is not 0: # if this is a variable, not an id, then test for levels
        has_lvls = has_levels(variable)
    else:
        has_lvls = 0
    return [no_rep_vals, eq_occur, reg_ints, int_div_range, has_lvls, var_type]
    
def get_feature_names():
    # based on function above, evaluate_features, returns array to store feature names
    return ['no_rep_vals', 'eq_occur', 'reg_ints', 'int_div_range', 'has_lvls', 'var_type']
    
def get_missing_value(records):
    # returns the string attached with missing values in the data
    # if no missing value in data, will return 'space_filler'
    try:
        return records.attributes["missingValue"].value
    except:
        return 'space_filler'
        
def get_distinct_values(variable, variable_number, records, missing):
    # gets all distinct values for the given variable
    distincts = {}
    total_missing = 0
    for record in range(len(records.childNodes)):
        if record % 2 and is_valid_nodeType(records.childNodes[record]):
            if variable_number is not 0:
                try:
                    distincts, total_missing = split_one_string(distincts, records, record, variable_number, missing, total_missing)
                except:
                    distincts = multiple_strings(distincts, records, record, variable_number)
            else: 
                distincts = get_ids(distincts, variable, records, record)
    return distincts, total_missing
            
def is_valid_nodeType(record):
    # checks if nodetype is valid (element node, not text or etc.)
    return (record.nodeType is 1)
    
def split_one_string(distincts, records, record, variable_number, missing, total_missing):
    # data is given in one long string - splits that data to get to the given variable
    data = records.childNodes[record].firstChild.nodeValue
    data = [str(x) for x in data.split()]
    this_variable = data[variable_number-1]
    if this_variable not in distincts:
        if this_variable != missing: 
            distincts[this_variable] = 1
        else:
            total_missing += 1
    else: 
        distincts[this_variable] += 1
    return distincts, total_missing
    
def multiple_strings(distincts, records, record, variable_number):
    # data is given in multiple strings, one per variable - gets data for given variable by going through those multiple strings
    count = 0
    for i in range(len(records.childNodes[record].childNodes)):
        if is_valid_nodeType(records.childNodes[record].childNodes[i]):
            count += 1
        else: continue
        if count == variable_number:
            this_variable = records.childNodes[record].childNodes[i].firstChild.nodeValue
            break
    if this_variable != []:
        if this_variable not in distincts:
            distincts[this_variable] = 1
        else:
            distincts[this_variable] += 1
    return distincts
    
def get_ids(distincts, variable, records, record):
    data = records.childNodes[record].attributes[variable].value
    if data not in distincts:
        distincts[data] = 1
    else: 
        distincts[data] += 1
    return distincts

def get_var_type(item):
    # returns variable type
    try:
        int(item)
        return 0 # 'int'
    except ValueError:
        pass
    try:
        float(item)
        return 1 # 'float'
    except ValueError:
        pass
    try:
        complex(item)
        return 2 # 'complex'
    except ValueError:
        pass
    return 3 # 'str'
        
    
def no_repeated_values(records, total_distincts, total_missing):
    # checks if there are no repeated values
    total = int(records.attributes["count"].value)
    if total-total_missing == total_distincts:
        return 1
    else: 
        return 0
    
def equal_occurrences(distincts):
    # checks if all distinct values occur equally often
    if len(set(distincts.values())) == 1:
        return 1
    else:
        return 0
    
def regular_intervals(distincts):
    # checks if intervals are all the same size
    try:
        list_distincts = sort_list(distincts)
        interval = list_distincts[1]-list_distincts[0]
        same_interval = True
        for i in range(len(list_distincts)-2):
            if list_distincts[i+2]-list_distincts[i+1] != interval:
                same_interval = False
                break
        if same_interval == True:
            return 1
        else:
            return 0
    except IndexError:
        print 'index error?'
    except ValueError:
        return 0
        
def interval_divides_range(distincts):
    # checks if interval width divides range
    list_distincts = sort_list(distincts)
    interval = list_distincts[1]-list_distincts[0]
    if set(list_distincts) == set(np.arange(list_distincts[0],list_distincts[-1]+1,interval)):
        return 1
    else:
        return 0
        
def has_levels(variable):
    # checks if variable has "levels", which are usually strings to describe their integer indicators
    if not variable.childNodes:
        return 0
    else:
        return 1
        
def sort_list(distincts):
    # sorts distinct values of the variable in order
    return sorted(list([float(x) for x in distincts.keys()]))
    
def create_target(training):
    target = []
    datareader = csv.reader(open(training,'rU'))
    for row in datareader:
        if row[2] != '' and row[2] != 'category':
            target.append(classify(row[2]))
    target = np.array(target)
    return target
    
def classify(variable):
    # returns numerical classification of variable type (nominal, ordinal, real, id, time)
    if variable == 'nominal':
        return 0
    if variable == 'ordinal':
        return 1
    if variable == 'real':
        return 2
    if variable == 'id':
        return 3
    if variable == 'time':
        return 4
    
if __name__ == "__main__":
    # parse arguments
    import argparse

    parser = argparse.ArgumentParser(description='Takes in directory with .xml files and writes tuples to training file.')
    parser.add_argument("-x","--xmldir", dest="xmldir", nargs='?', default=XMLDIR,
                        help='directory containing all .xml files from which to read in data')
    parser.add_argument("-t", "--training", dest="training", nargs='?', default=TRAINING,
                        help='.csv file to which to write the feature tuples')
    parser.add_argument("-d", "--dot", dest="dot", nargs='?', default=DOT,
                        help='.dot file on which to create the decision tree') 
    args = parser.parse_args()
    
    main(args)