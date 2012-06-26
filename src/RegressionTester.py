'''
Created on Jun 7, 2012

@author: mchrzanowski
'''

from __future__ import division

import Constants
import CorpusAccess
import Litigation10KParsing
import multiprocessing
import time
import Utilities

def run():
    start = time.time()
    run_regression_test_suite()
    end = time.time()
    print "Regression Runtime:%r seconds." % (end - start) 

def _character_count_test(CIK, filing_year, new_data, corpus_file):

    parser_alpha_numeric_count =  Utilities.get_alpha_numeric_count(''.join(blob for blob in new_data))

    with open(corpus_file, 'r') as f:
        
        text_from_file = f.read()
        file_alpha_numeric_count = Utilities.get_alpha_numeric_count(text_from_file)
    
    change = (parser_alpha_numeric_count - file_alpha_numeric_count) / file_alpha_numeric_count
    result = abs(change) < Constants.REGRESSION_CHAR_COUNT_CHANGE_THRESHOLD
    
    print "CIK:%r, Year:%r, New Count:%r, " % (CIK, filing_year, parser_alpha_numeric_count),
    print "Corpus Count:%r, Passed:%r" % (file_alpha_numeric_count, result)
    
    if result is False:
        CorpusAccess.write_comparison_to_file(new_data, text_from_file, CIK, filing_year)


def _litigation_footnote_unit_test(CIK, filing_year, corpus_file):
    processed_website_data = CorpusAccess.get_processed_website_data_from_corpus(CIK, filing_year)
    result = Litigation10KParsing.parse(CIK, filing_year, processed_website_data, get_litigation_footnotes_only=True)
    _character_count_test(CIK, filing_year, result.legal_note_mentions, corpus_file)

def _legal_proceeding_unit_test(CIK, filing_year, corpus_file):
                
    processed_website_data = CorpusAccess.get_processed_website_data_from_corpus(CIK, filing_year)
    result = Litigation10KParsing.parse(CIK, filing_year, processed_website_data, get_legal_proceeding_only=True)
    _character_count_test(CIK, filing_year, result.legal_proceeding_mention, corpus_file)

def _walk_corpus_file_directory_and_call_unit_test(unit_test, corpus_walker):    
    ''' 
        go through every single CIK,Year pair and instantiate new 10KParser classes
        for all of them. check their results against what is in the corpus. the new blob
        that the object would have written should be no more than a few percentage points
        different than what is in the corpus. 
    '''
    
    pool = multiprocessing.Pool()
        
    for CIK, filing_year, file_path in corpus_walker():
        pool.apply_async(unit_test, args=(CIK, filing_year, file_path))   
    
    pool.close()
    pool.join()

def run_regression_test_suite():
    CorpusAccess.wipe_existing_failed_unit_tests()
    #_run_legal_proceeding_test_suite()
    _run_legal_footnotes_test_suite()
    
def _run_legal_footnotes_test_suite():
    _walk_corpus_file_directory_and_call_unit_test(_litigation_footnote_unit_test, CorpusAccess.access_every_file_in_legal_footnotes_corpus)

def _run_legal_proceeding_test_suite():
    _walk_corpus_file_directory_and_call_unit_test(_legal_proceeding_unit_test, CorpusAccess.access_every_file_in_legal_proceeding_corpus)
    
                    
if __name__ == '__main__':
    run()
