XMLDIR = '/Users/christopherli/Documents/AMPLab/data/'
TRAINING = '/Users/christopherli/Documents/AMPLab/training_tester.csv'
DOT = '/Users/christopherli/Documents/AMPLab/data_test.dot'
XML_SUFFIX = '.xml'

import os
from xml.dom import minidom
import numpy as np
from scipy import stats
import csv

def main(args):
    xmldir = args.xmldir
    training = args.training
    dot = args.dot
    
    # compute and write tuples to training file, then create decision tree
    run(xmldir,training,dot)
    
def run(xmldir, training, dot):
    xmlfiles = find_xmlfiles(xmldir)
    tuples = []
    for f in xmlfiles:
        tuples = tuples + process_variables(f)
    
    # create numpy.ndarray from tuples
    data.data = np.ndarray(tuples)
    print data.data
    
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
        if there_are(variables):
            variable_number = 0
            for variable in variables[0].childNodes:
                if is_valid_variable(variable):
                    variable_number += 1
                    features.append(evaluate_features(variable_number, records)
    return features
    
def there_are(things):
    # returns if there are any "things"
    return len(things) != 0
    
def is_valid_variable(variable):
    # checks if variable is a valid variable (element node, not a counter, not a randomuniform)
    return (variable.nodeType == 1 and variable.nodeName != 'countervariable' and variable.nodeName != 'randomuniformvariable')
    
def evaluate_features(variable_number, records):
    # runs each feature test and returns the results for the variable
    missing = get_missing_value(records)
    distincts, total_missing = get_distinct_values(variable_number, records, missing)
    var_type = get_var_type(distincts.keys()[0])
    total_distincts = len(distincts)
    no_repeated_values = no_repeated_values(records, total_distincts, total_missing)
    equal_occurrences = equal_occurrences(distincts)
    regular_intervals = regular_intervals(distincts)
    if regular_intervals:
        interval_divides_range = interval_divides_range(distincts)
    else:
        interval_divides_range = 0
    return [no_repeated_values, equal_occurrences, regular_intervals, interval_divides_range, var_type]
    
def get_missing_value(records):
    # returns the string attached with missing values in the data
    # if no missing value in data, will return 'space_filler'
    try:
        return records.attributes["missingValue"].value
    except:
        return 'space_filler'
        
def get_distinct_values(variable_number, records, missing):
    # gets all distinct values for the given variable
    distincts = {}
    total_missing = 0
    for record in range(len(records.childNodes)):
        if record % 2 and is_valid_nodeType(records.childNodes[record]):
            try:
                distincts, total_missing = split_one_string(distincts, records, record, variable_number, missing, total_missing)
                return distincts, total_missing
            except:
                distincts = multiple_strings(distincts, records, record, variable_number)
                return distincts, 0
            
def is_valid_nodeType(record):
    # checks if nodetype is valid (element node, not text or etc.)
    return (record.nodeType is 1)
    
def split_one_string(distincts, records, record, variable_number, missing, total_missing):
    # data is given in one long string - splits that data to get to the given variable
    data = records.childNodes[record].firstChild.nodeValue
    data = [str(x) for x in info.split()]
    this_variable = data[variable_number-1]
    if this_variable not in distincts:
        if this_variable != missing: 
            distincts = add_variable(this_variable, distincts)
        else:
            total_missing += 1
    else: 
        distincts = increment_variable(this_variable, distincts)
    return distincts, total_missing
        
def add_variable(variable, distincts):
    # adds variable to dictionary of distincts - value starts at 1
    distincts[variable] = 1
    return distincts
    
def increment_variable(variable, distincts):
    # increments value of the variable in the distincts dict
    distincts[variable] += 1
    return distincts
    
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
            add_variable(this_variable, distincts)
        else:
            increment_variable(this_variable, distincts)
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
    if set(list_distincts) == set(np.arange(list_distincts[0],list_distincts[-1]+1,interval)):
        return 1
    else:
        return 0
        
def sort_list(distincts):
    # sorts distinct values of the variable in order
    return sorted(list([float(x) for x in distincts.keys()]))
    
if __name__ == "__main__":
    # parse arguments
    import argparse

    parser = argparse.ArgumentParser(description='Takes in directory with .xml files and writes tuples to training file.')
    parser.add_argument("-x","--xmldir", dest="xmldir", nargs='?', default=XMLDIR,
                        help='directory containing all .xml files from which to read in data')
    parser.add_argument("-t", "--training", dest="training", nargs='?',
                        type=argparse.FileType('a'), default=TRAINING,
                        help='.csv file to which to write the feature tuples')
    parser.add_argument("-d", "--dot", dest="dot", nargs='?', default=DOT,
                        help='.dot file on which to create the decision tree') 
    args = parser.parse_args()
    
    main(args)