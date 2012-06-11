'''
Created on Jun 7, 2012

@author: mchrzanowski
'''

from __future__ import division
from Litigation10KParser import Litigation10KParser

import Constants
import CorpusWriter
import multiprocessing
import os
import re
import time
import Utilities

def run():
    start = time.time()
    CorpusWriter.wipe_existing_failed_unit_tests()
    run_test_suite()
    end = time.time()
    print "Regression Runtime:%r seconds." % (end - start) 

def unit_test(CIK, filing_year, corpus_file):
    
    with open(corpus_file) as f:
        
        text_from_file = f.read()
        
        file_alpha_numeric_count = Utilities.get_alpha_numeric_count(text_from_file)
        
        parser = Litigation10KParser(CIK, filing_year)
        parser.parse()
        
        parser_alpha_numeric_count = 0
        for hit in parser.mentions: 
            parser_alpha_numeric_count += Utilities.get_alpha_numeric_count(hit)
            
        change = (parser_alpha_numeric_count - file_alpha_numeric_count) / file_alpha_numeric_count
                    
        result = abs(change) < Constants.REGRESSION_CHAR_COUNT_CHANGE_THRESHOLD
    
    print "CIK:%r, Year:%r, New Count:%r, " % (CIK, filing_year, parser_alpha_numeric_count),
    print "Corpus Count:%r, Passed:%r" % (file_alpha_numeric_count, result)
    
    if result is False:
        CorpusWriter.write_comparison_to_file(parser.mentions, text_from_file, CIK, filing_year)
    
def run_test_suite():
    ''' 
        go through every single CIK,Year pair and instantiate new Litigation10KParser classes
        for all of them. check their results against what is in the corpus. the new blob
        that the object would have written should be no more than a few percentage points
        different than what is in the corpus. 
    '''
    
    path = Constants.PATH_TO_CORPUS
    
    pool = multiprocessing.Pool()
    
    get_filing_year_from_corpus_file = re.compile("\.txt")
    
    for potential_cik in os.listdir(path):
        if os.path.isdir(os.path.join(path, potential_cik)):
            for filing_year_file in os.listdir(os.path.join(path, potential_cik)):
                path_to_test = os.path.join(path, potential_cik, filing_year_file)
                filing_year = re.sub(get_filing_year_from_corpus_file, "", filing_year_file)
                pool.apply_async(unit_test, args=(potential_cik, filing_year, path_to_test))   
    
    pool.close()
    pool.join()
                    
if __name__ == '__main__':
    run()
