'''
Created on Jun 7, 2012

@author: mchrzanowski
'''

from __future__ import division

import argparse
import Constants
import CorpusAccess
import Litigation10KParsing
import multiprocessing
import time
import Utilities

def run(legal_footnotes_only, legal_proceeding_only):
    start = time.time()    
    run_regression_test_suite(legal_footnotes_only, legal_proceeding_only)
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
    company_name = CorpusAccess.get_company_name_from_corpus(CIK)

    result = Litigation10KParsing.parse(CIK, filing_year, company_name, processed_website_data, get_litigation_footnotes_only=True)
    
    if processed_website_data is None:
        CorpusAccess.write_processed_url_data_to_file(data=result.processed_text, CIK=result.CIK, filing_year=result.filing_year)

    if company_name is None:
        CorpusAccess.write_company_name_and_cik_mapping_to_corpus(result.CIK, result.company_name)    
    
    _character_count_test(CIK, filing_year, result.legal_note_mentions, corpus_file)

def _legal_proceeding_unit_test(CIK, filing_year, corpus_file):
                
    processed_website_data = CorpusAccess.get_processed_website_data_from_corpus(CIK, filing_year)
    company_name = CorpusAccess.get_company_name_from_corpus(CIK)
    
    result = Litigation10KParsing.parse(CIK, filing_year, company_name, processed_website_data, get_legal_proceeding_only=True)
    
    if processed_website_data is None:
        CorpusAccess.write_processed_url_data_to_file(data=result.processed_text, CIK=result.CIK, filing_year=result.filing_year)
    
    if company_name is None:
        CorpusAccess.write_company_name_and_cik_mapping_to_corpus(result.CIK, result.company_name)    

    _character_count_test(CIK, filing_year, result.legal_proceeding_mention, corpus_file)

def _walk_corpus_file_directory_and_call_unit_test(unit_test, corpus_walker):    
    ''' 
        go through every single CIK,Year pair and instantiate new 10KParser classes
        for all of them. check their results against what is in the corpus. the new blob
        that the object would have written should be no more than a few percentage points
        different than what is in the corpus. 
    '''
    
    pool = multiprocessing.Pool(maxtasksperchild=10)    # number set arbitrarily. key point is that processes *must* exit
                                                        # eventually as they end up accumulating so much memory that Linux kills them eventually!
    for CIK, filing_year, file_path in corpus_walker():
        pool.apply_async(unit_test, args=(CIK, filing_year, file_path))   
    
    pool.close()
    pool.join()

def run_regression_test_suite(legal_footnotes_only, legal_proceeding_only):
    CorpusAccess.wipe_existing_failed_unit_tests()
    if not legal_footnotes_only:
        _run_legal_proceeding_test_suite()
    if not legal_proceeding_only:
        _run_legal_footnotes_test_suite()
    
def _run_legal_footnotes_test_suite():
    _walk_corpus_file_directory_and_call_unit_test(_litigation_footnote_unit_test, CorpusAccess.access_every_file_in_legal_footnotes_corpus)

def _run_legal_proceeding_test_suite():
    _walk_corpus_file_directory_and_call_unit_test(_legal_proceeding_unit_test, CorpusAccess.access_every_file_in_legal_proceeding_corpus)
    
                    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='A script that compares the output from the parsing engine against what is expected.')
    parser.add_argument('-lpo', action='store_true', help="run for the legal proceeding corpus only")
    parser.add_argument('-lfo', action='store_true', help="run for the legal footnotes corpus only")
    
    args = vars(parser.parse_args())
    
    run(legal_footnotes_only=args['lfo'], legal_proceeding_only=args['lpo'])
