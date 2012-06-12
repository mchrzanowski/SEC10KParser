'''
Created on Jun 7, 2012

@author: mchrzanowski
'''

from __future__ import division

import Constants
import CorpusAccess
import Litigation10KParsing
import multiprocessing
import os
import re
import time
import Utilities

def run():
    start = time.time()
    CorpusAccess.wipe_existing_failed_unit_tests()
    run_test_suite()
    end = time.time()
    print "Regression Runtime:%r seconds." % (end - start) 

def __unit_test(CIK, filing_year, corpus_file):
    
    with open(corpus_file, 'r') as f:
        
        text_from_file = f.read()
        file_alpha_numeric_count = Utilities.get_alpha_numeric_count(text_from_file)
        
    processed_website_data = CorpusAccess.get_processed_website_data_from_corpus(CIK, filing_year)
    result = Litigation10KParsing.parse(CIK, filing_year, processed_website_data)
    parser_alpha_numeric_count =  Utilities.get_alpha_numeric_count(result.legal_proceeding_mention)
        
    change = (parser_alpha_numeric_count - file_alpha_numeric_count) / file_alpha_numeric_count
    result = abs(change) < Constants.REGRESSION_CHAR_COUNT_CHANGE_THRESHOLD
    
    print "CIK:%r, Year:%r, New Count:%r, " % (CIK, filing_year, parser_alpha_numeric_count),
    print "Corpus Count:%r, Passed:%r" % (file_alpha_numeric_count, result)
    
    if result is False:
        CorpusAccess.write_comparison_to_file(result.legal_proceeding_mention, text_from_file, CIK, filing_year)
    
def run_test_suite():
    ''' 
        go through every single CIK,Year pair and instantiate new 10KParser classes
        for all of them. check their results against what is in the corpus. the new blob
        that the object would have written should be no more than a few percentage points
        different than what is in the corpus. 
    '''
    
    path = Constants.PATH_TO_LEGAL_PROCEEDING_CORPUS
    
    pool = multiprocessing.Pool()
    
    get_filing_year_from_corpus_file = re.compile("\.txt", re.I)
    
    for potential_cik in os.listdir(path):
        if os.path.isdir(os.path.join(path, potential_cik)):
            for filing_year_file in os.listdir(os.path.join(path, potential_cik)):
                path_to_test = os.path.join(path, potential_cik, filing_year_file)
                filing_year = re.sub(get_filing_year_from_corpus_file, "", filing_year_file)
                pool.apply_async(__unit_test, args=(potential_cik, filing_year, path_to_test))   
    
    pool.close()
    pool.join()
                    
if __name__ == '__main__':
    run()
