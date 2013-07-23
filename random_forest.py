XMLDIR = '/Users/christopherli/Documents/AMPLab/data/'
TRAINING = '/Users/christopherli/Documents/AMPLab/data/training4.csv'
DOT = '/Users/christopherli/Documents/AMPLab/data_test.dot'

import featurize_data
from sklearn import cross_validation
from sklearn import ensemble
import numpy as np

def main(args):
    data = args.data
    target = args.target
    folds = args.folds
    
    # trains on (folds-1) of the data to create decision tree and tests on (1) fold to evaluate error
    run(data, target, folds)
    
def run(data, target, folds):
    
    # produce train/test indices to split data in train test sets
    splits = split(target, folds)
    
    # initialize error array so size matches number of folds
    errors = [0]*folds
    
    fold = 0
    for train_index, test_index in splits:
        
        data_train, data_test = data[train_index], data[test_index]
        target_train, target_test = target[train_index], target[test_index]
        
        # create decision tree based on training data
        clf = train_tree(data_train, target_train)
        
        # predict target for test data
        predictions = test_tree(clf, data_test)
        
        # compare target and results for test data and compute error
        errors[fold] = compare_and_compute(predictions, target_test)
        
        fold += 1
    
    # average errors from all folds
    avg_error = np.mean(errors)
    print errors
    print avg_error
    
def split(target, folds):
    # produces train/test indices to split data in train test sets
    
    splits = cross_validation.StratifiedKFold(target, n_folds=folds)
    return splits
    
def train_tree(data_train, target_train):
    clf = ensemble.RandomForestClassifier()
    clf = clf.fit(data_train, target_train)
    return clf
    
def test_tree(clf, data_test):
    predictions = clf.predict(data_test)
    return predictions
    
def compare_and_compute(predictions, target_test):
    total = len(predictions)
    wrong = 0.0
    for i in range(total):
        if predictions[i] != target_test[i]:
            wrong += 1
    return wrong/float(total)

if __name__ == "__main__":
    # parse arguments
    import argparse

    parser = argparse.ArgumentParser(description='Uses decision tree from featurize_data.py for cross-validation testing.')
    parser.add_argument("-x","--xmldir", dest="xmldir", nargs='?', default=XMLDIR,
                        help='directory containing all .xml files from which to read in data')
    parser.add_argument("-train", "--training", dest="training", nargs='?', default=TRAINING,
                        help='.csv file to which to write the feature tuples')
    parser.add_argument("-dot", "--dot", dest="dot", nargs='?', default=DOT,
                        help='.dot file on which to create the decision tree')
    args = parser.parse_args()
    
    data, target = featurize_data.main(args)
    
    parser.add_argument("-f","--folds", dest="folds", nargs='?', default=4,
                        help='number of groups to split data up in for training (folds-1) and testing (1)')
    parser.add_argument("-d","--data", dest="data", nargs='?', default=data,
                        help='training data (tuples)')
    parser.add_argument("-t","--target", dest="target", nargs='?', default=target,
                        help='target classification of training data')
    args = parser.parse_args()

    main(args)