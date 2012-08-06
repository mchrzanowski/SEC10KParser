'''
Created on Jul 23, 2012

@author: mchrzanowski
'''

import argparse
import Constants
import CorpusAccess
import csv
import edgar
import multiprocessing
import re
import time
import urllib2
import Utilities

_name_to_cik_mapping = multiprocessing.Manager().dict()

_corpus_access_mutex = multiprocessing.Lock()

def _get_potential_cik_from_company_name(plaintiff):

    CIK = ''

    # first, try to fish the CIK from previously-observed mappings.
    if plaintiff in _name_to_cik_mapping:
        CIK = _name_to_cik_mapping[plaintiff]

    # didn't work. try using EDGAR.
    else:
        potential_cik = edgar.get_cik_of_company_from_name(plaintiff)
        if potential_cik is not None and len(potential_cik) > 0:
            CIK = potential_cik
            _name_to_cik_mapping[plaintiff] = CIK

    return CIK


def _get_raw_data(CIK, year):
    ''' 
        process-safe way of accessing a given 10-K as indexed
        by CIK and filing year. method will store the data to disk
        if it's not already there 
    '''
    # maintain exclusive zone when acquiring raw data.
    # this section of the code could, based on OS scheduling, easily
    # lead to multiple download attempts of the same data.
    _corpus_access_mutex.acquire()

    raw_data = CorpusAccess.get_raw_website_data_from_corpus(CIK=CIK, filing_year=year)

    if raw_data is None:
        url = edgar.get_10k_url(CIK=CIK, filing_year=year)
    
        if url is not None:
            raw_data = urllib2.urlopen(url, timeout=72000).read()
            CorpusAccess.write_raw_url_data_to_file(raw_data, CIK=CIK, filing_year=year)

    _corpus_access_mutex.release()

    return raw_data

def _perform_check_and_write_to_results_file(case_pattern, index, CIK, original_case_name, original_row, row_holder):

    print "Start:", index, CIK, case_pattern.pattern, original_case_name

    new_row = list(original_row)
    hits = set()

    for year in xrange(2004, 2012 + 1):

        raw_data = _get_raw_data(CIK, year)

        if raw_data is not None:
            if re.search(case_pattern, raw_data):
                hits.add(year)

    print "Hits:", hits

    for year in xrange(2004, 2012 + 1):
        if year in hits:
            new_row.append(1)
        else:
            new_row.append(0)

    row_holder.append(new_row)


def _get_first_word_of_case_name(case_name):

    first_word = ""
    for potential in re.split("\s+", case_name):
        # pass the blacklist of common words
        # I don't care about.

        potential_lc = potential.lower()
        if potential_lc == 'a':
            continue
        if potential_lc == 'an':
            continue
        if potential_lc == 'the':
            continue

        first_word = potential
        break

    # remove commas
    pattern = re.sub(",", "", first_word)

    # remove whitespace
    pattern = pattern.strip()

    # sub periods for a period pattern
    pattern = re.sub("\.", "\.?", pattern)

    # sub parentheses.
    pattern = re.sub("\(", "\(?", pattern)
    pattern = re.sub("\)", "\)?", pattern)

    # sub apostrophes
    pattern = re.sub("'", "'?", pattern)

    # add borders. space the special chars out
    # so that they don't become backspaces.
    pattern = '\\' + 'b' + pattern + '\\' + 'b'

    # if we got a case name that isn't all in caps,
    # then we assume that 10-Ks preserve the correct
    # casing. Otherwise, do an ignore-case match.
    if first_word.isupper():
        return re.compile(pattern, flags=re.I)
    else:
        return re.compile(pattern)

def _read_ouput_file_and_get_finished_indices():
    reader = csv.reader(open(Constants.PATH_TO_NEW_LITIGATION_FILE, 'rb'), delimiter=',')

    results = set()

    for row in reader:
        index = row[0]
        results.add(index)

    return results


def main(items_to_add):

    finished_indices = _read_ouput_file_and_get_finished_indices()

    pool = multiprocessing.Pool(maxtasksperchild=15)

    row_holder = multiprocessing.Manager().list()

    processed_index_counter = 0

    litigationReader = csv.reader(open(Constants.PATH_TO_LITIGATION_FILE, 'rb'), delimiter=',')


    for row in litigationReader:
        
        index, _, original_cik, plaintiff, original_case_name = row

        if index in finished_indices:
            continue
        else:
            processed_index_counter += 1

        if processed_index_counter > items_to_add:
            break

        CIK = Utilities.format_CIK(original_cik)

        # rows always have a plaintiff but not always a CIK.
        if int(CIK) > 0:
            # if this row has the CIK-company name mapping, cache it.
            # update the key-value pairing with each row iteration
            # as company CIKSs can change as time goes on.
            if len(plaintiff) > 0:
                _name_to_cik_mapping[plaintiff] = CIK        
        
        else:
            # this row didnt have a CIK. first, check previous rows for the mapping we want.
            # if that doesn't exist, use the company name and edgar to get the 
            # potential CIK.
            CIK = _get_potential_cik_from_company_name(plaintiff)

        if len(CIK) == 0 or int(CIK) == 0:
            print "Error: No CIK. Index:", index
            continue

        case_pattern = _get_first_word_of_case_name(original_case_name)

        #_perform_check_and_write_to_results_file(case_pattern, index, CIK, original_case_name, row, row_holder)

        pool.apply_async(_perform_check_and_write_to_results_file, \
            args=(case_pattern, index, CIK, original_case_name, row, row_holder))

    pool.close()
    pool.join()

    litigationWriter = csv.writer(open(Constants.PATH_TO_NEW_LITIGATION_FILE, 'ab'), delimiter=',')
    for row in row_holder:
        litigationWriter.writerow(row)

if __name__ == '__main__':
    start = time.time()
    
    parser = argparse.ArgumentParser(description='A script that checks to see whether lawsuits are mentioned in defendant 10-Ks.')
    parser.add_argument('-add', type=int, help="Add more rows to the completed output file")
    args = vars(parser.parse_args())
    main(args['add'])
    
    end = time.time()
    print "Runtime:", end - start, "seconds."
