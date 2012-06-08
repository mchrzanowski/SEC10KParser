'''
Created on Jun 7, 2012

@author: mchrzanowski
'''

from __future__ import division
from Litigation10KParser import Litigation10KParser

import Constants
import multiprocessing
import os
import re
import time


def run():
    start = time.time()
    run_test_suite()
    end = time.time()
    print "Regression Runtime:%r seconds." % (end - start) 

def unit_test(CIK, filing_year, corpus_file):
    
    file_alpha_numeric_count = 0
    with open(corpus_file) as f:
        for line in f:
            for char in line:
                if char.isalpha() or char.isdigit():
                    file_alpha_numeric_count += 1
    
    parser = Litigation10KParser(CIK, filing_year)
    parser.parse()
    parser_alpha_numeric_count = parser.character_count_of_mentions()
    
    change = (parser_alpha_numeric_count - file_alpha_numeric_count) / file_alpha_numeric_count
    
    THRESHOLD = Constants.REGRESSION_CHAR_COUNT_CHANGE_THRESHOLD
            
    if abs(change) < THRESHOLD:
        result = "PASS"
    else:
        result = "FAIL"
    
    print "CIK:%r, Year:%r, New Count:%r, " % (CIK, filing_year, parser_alpha_numeric_count),
    print "Corpus Count:%r, Result:%r" % (file_alpha_numeric_count, result)
        
        

def run_test_suite():
    ''' 
        go through every single CIK,Year pair and instantiate new Litigation10KParser classes
        for all of them. check their results against what is in the corpus. the new blob
        that the object would have written should be no more than a few percentage points
        different than what is in the corpus. 
    '''
    
    path = Constants.PATH_TO_CORPUS
    
    pool = multiprocessing.Pool()
    
    contains_non_numeric_chars_test = re.compile("[^0-9]")
    get_filing_year_from_corpus_file = re.compile("\.txt")
    
    for potential_cik in os.listdir(path):
        if not re.search(contains_non_numeric_chars_test, potential_cik):
            for filing_year_file in os.listdir(os.path.join(path, potential_cik)):
                path_to_test = os.path.join(path, potential_cik, filing_year_file)
                filing_year = re.sub(get_filing_year_from_corpus_file, "", filing_year_file)
                pool.apply_async(unit_test, args=(potential_cik, filing_year, path_to_test,))                
                
    pool.close()
    pool.join()
                    
if __name__ == '__main__':
    run()
