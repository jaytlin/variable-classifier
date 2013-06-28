def numtype(item):
    # add binary?
    try:
        int(item)
        return 'int'
    except ValueError:
        pass
    try:
        float(item)
        return 'float'
    except ValueError:
        pass
    try:
        complex(item)
        return 'complex'
    except ValueError:
        pass
    return 'str'

from xml.dom import minidom
import numpy as np
from scipy import stats
import csv

# open and parse xml
xmldoc = minidom.parse('morsecodes.xml')

# open csv write file
test = open('training2.csv','a')
wr = csv.writer(test)
columns = ['name','dataset','category','1_{no repeated values}','1_{distinct values occur equally often}','1_{regularly spaced intervals}','1_{interval width divides range}','type']
######### [  0   ,    1    ,     2    ,           3            ,                    4                    ,               5                ...           
# wr.writerow(columns)
wr.writerow([])
wr.writerow([])

# for each data set
for data in range(len(xmldoc.getElementsByTagName('data'))):
    
    dataset = xmldoc.getElementsByTagName('data')
    # get all variable groups in dataset
    variables = dataset[data].getElementsByTagName('variables')
    records = dataset[data].getElementsByTagName('records')[0]
    
    try:
        columns[1] = dataset[data].attributes["name"].value # DATASET
    except:
        columns[1] = "no name"
    total = int(records.attributes["count"].value) # TOTAL NUMBER OF ROWS
     
    i = 1  
    try:
        i = 1
        while records.childNodes[i].nodeType is not 1: i += 1
        records.childNodes[i].attributes["id"].value
        columns[0] = 'id'
        repeat = 1
    except:
        pass
    try:
        while records.childNodes[i].nodeType is not 1: i += 1
        records.childNodes[i].attributes["label"].value
        columns[0] = 'label'
        repeat = 1
    except:
        pass
    try:
        while records.childNodes[i].nodeType is not 1: i += 1
        records.childNodes[i].attributes["source"].value
        columns[0] = 'source'
        repeat = 2
    except:
        pass
    
    ### FIRST add id or label or source and destination as a variable(s) ###
    if columns[0] == 'id' or columns[0] == 'label' or columns[0] == 'source':
        
        for rep in range(repeat):
            
            if rep == 1:
                columns[0] = 'destination'
            
            # calculate distinct values
            distincts = {}
            for record in range(len(records.childNodes)):
                if record % 2 and records.childNodes[record].nodeType is 1:
                    info = records.childNodes[record].attributes[columns[0]].value
                    if info not in distincts:
                        distincts[info] = 1
                    else: 
                        distincts[info] += 1
            total_distincts = len(distincts) # TOTAL DISTINCT VALUES
    
            # if no repeated values
            if total == total_distincts:
                columns[3] = 1
            else:
                columns[3] = 0
        
            # if all distinct values occur equally often
            if len(set(distincts.values())) == 1:
                columns[4] = 1
            else:
                columns[4] = 0
        
            # if intervals are regularly spaced
            try:
                columns[7] = numtype(distincts.keys()[0])
                list_distincts = sorted(list([float(x) for x in distincts.keys()]))
                interval = list_distincts[1]-list_distincts[0]
                same_interval = True
                for i in range(len(list_distincts)-2):
                    if list_distincts[i+2]-list_distincts[i+1] != interval:
                        same_interval = False
                        break
                if same_interval == True:
                    columns[5] = 1
                else:
                    columns[5] = 0
            except: # strings?
                columns[5] = 0
            
            # if interval width divides range
            if columns [5] == 1:
                if set(list_distincts) == set(np.arange(list_distincts[0],list_distincts[-1]+1,interval)):
                    columns[6] = 1
                else:
                    columns[6] = 0
            else:
                columns[6] = 0
    
            wr.writerow(columns)

    try:
        missing = records.attributes["missingValue"].value # string label for missing value
    except:
        missing = 'space_filler' # if no missing value, just use "space_filler"

    ### THEN for each variable in the data set ###
    for d_set in range(len(variables)):
        total_variables = 0
        for variable in variables[d_set].childNodes:
            if variable.nodeType is 1 and variable.nodeName != 'countervariable' and variable.nodeName != 'randomuniformvariable':
    
                total_variables += 1
                columns[0] = variable.attributes["name"].value # NAME
                columns[7] = 'type' # initialize type
                missing_vals = 0 # initialize missing values

                if not variable.childNodes:
                    row = 1
                    try:
                        info = records.childNodes[row].firstChild.nodeValue
                        info = [str(x) for x in info.split()]
                        while info[total_variables-1] == missing:
                            row += 2
                            info = records.childNodes[row].firstChild.nodeValue
                            info = [str(x) for x in info.split()]
                    except:
                        info = []
                    if info == []:
                        count = 0
                        for i in range(len(records.childNodes[row].childNodes)):
                            if records.childNodes[row].childNodes[i].nodeType is 1:
                                count +=1
                            else: continue
                            if count == total_variables:
                                info = records.childNodes[row].childNodes[i].firstChild.nodeValue
                                while info == missing:
                                    row += 2
                                    info = records.childNodes[row].childNodes[i].firstChild.nodeValue
                                break
                    else:
                        info = info[total_variables-1]
                    try:
                        columns[7] = numtype(info) # TYPE (int or float)
                    except:
                        columns[7] = 'str' # TYPE (string)
                    try:
                        time = variable.attributes["time"].value
                        columns[2] = "real" # for now, time is always real
                    except:
                        columns[2] = "" # temporary
                else:                
                    levels = {}
                    for level in variable.childNodes[1].childNodes:
                        if level.nodeType is 1:
                            levels[level.attributes["value"].value] = level.firstChild.nodeValue
                            try: 
                                columns[7] = numtype(level.firstChild.nodeValue) # TYPE (int or float)
                            except:
                                columns[7] = 'str' # TYPE (string)
                    if columns[7] == 'type':
                        info = records.childNodes[1].firstChild.nodeValue
                        info = [str(x) for x in info.split()]
                        columns[7] = numtype(info[0])
                        columns[2] = "" # temporary
    
        
                # calculate distinct values for this variable
                distincts = {}
                for record in range(len(records.childNodes)):
                    if record % 2 and records.childNodes[record].nodeType is 1:
                        try: 
                            info = records.childNodes[record].firstChild.nodeValue
                            info = [str(x) for x in info.split()]
                            if info[total_variables-1] not in distincts:
                                if info[total_variables-1] != missing: # if this row's value for this variable isn't missing, add it
                                    distincts[info[total_variables-1]] = 1
                                else:
                                    missing_vals += 1
                            else: 
                                distincts[info[total_variables-1]] += 1
                        except:
                            count = 0
                            for i in range(len(records.childNodes[record].childNodes)):
                                if records.childNodes[record].childNodes[i].nodeType is 1:
                                    count += 1
                                else: continue
                                if count == total_variables:
                                    info = records.childNodes[record].childNodes[i].firstChild.nodeValue
                                    break
                            if info != []:
                                if info not in distincts:
                                    distincts[info] = 1
                                else:
                                    distincts[info] += 1
                total_distincts = len(distincts) # TOTAL DISTINCT VALUES
    
                # if no repeated values
                if total-missing_vals == total_distincts:
                    columns[3] = 1
                else:
                    columns[3] = 0
        
                # if all distinct values occur equally often
                if len(set(distincts.values())) == 1:
                    columns[4] = 1
                else:
                    columns[4] = 0
        
                # if intervals are regularly spaced
                try:
                    list_distincts = sorted(list([float(x) for x in distincts.keys()]))
                    interval = list_distincts[1]-list_distincts[0]
                    same_interval = True
                    for i in range(len(list_distincts)-2):
                        if list_distincts[i+2]-list_distincts[i+1] != interval:
                            same_interval = False
                            break
                    if same_interval == True:
                        columns[5] = 1
                    else:
                        columns[5] = 0
                except IndexError:
                    print 'index error?'
                except ValueError: # strings?
                    columns[5] = 0
            
                # if interval width divides range
                if columns [5] == 1:
                    if set(list_distincts) == set(np.arange(list_distincts[0],list_distincts[-1]+1,interval)):
                        columns[6] = 1
                    else:
                        columns[6] = 0
                else:
                    columns[6] = 0
        
                # write row to csv
                wr.writerow(columns)
            
    