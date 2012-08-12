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

_manager = multiprocessing.Manager()
_name_to_cik_mapping = _manager.dict()
_corpus_access_mutex = multiprocessing.Lock()


def _get_potential_cik_from_company_name(plaintiff):
    ''' try matching a company name to its CIK. there are several approaches to this. '''

    CIK = None

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
            raw_data = urllib2.urlopen(url, timeout=Constants.URL_DOWNLOAD_TIMEOUT_IN_SECS).read()
            CorpusAccess.write_raw_url_data_to_file(raw_data, CIK=CIK, filing_year=year)

    _corpus_access_mutex.release()

    return raw_data


def _perform_check_and_write_to_results_file(case_pattern, row, row_holder):

    print "Start:", row.index, row.CIK, case_pattern.pattern, row.case_name

    for year in xrange(2004, 2012 + 1):

        raw_data = _get_raw_data(row.CIK, year)

        if raw_data is not None:
            if re.search(case_pattern, raw_data):
                row.case_mentioned_in_a_10k_for_a_year(year)

    row_holder.append(row.construct_row_with_ordered_fields())


def _get_first_word_of_case_name(case_name):
    '''
        checking for the first word is a strategy that produces a high false-positive rate,
        but, importantly and conversely, produces a very low false-negative rate.
        so we'll just need to check the false-positives manually; there aren't too many of them
    '''

    def _is_word_blacklisted(word):
        return word.lower() in ('a', 'an', 'the', 'in', 'de', 'del', 're', 're:', 'el', 'la', 'los', 'las', 'st', 'st.')

    first_word = ''
    for potential in re.split("\s+", case_name):

        # pass the blacklist of common words
        # I don't care about.
        if _is_word_blacklisted(potential):
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
    '''
        read the output file and see which indices exist in there. those are the finished rows.
        also read the rows for the already-learned CIK/plaintiff mapping
    '''
    reader = csv.reader(open(Constants.PATH_TO_NEW_LITIGATION_FILE, 'rb'), delimiter=',')

    results = set()

    for row in reader:
        index = row[0]
        CIK = row[2]
        plaintiff = row[3]

        results.add(index)
        if len(CIK) > 0:
            _name_to_cik_mapping[plaintiff] = CIK

    return results


def main(items_to_add):

    finished_indices = _read_ouput_file_and_get_finished_indices()

    pool = multiprocessing.Pool(maxtasksperchild=15)

    row_holder = _manager.list()

    processed_index_counter = 0

    litigationReader = csv.reader(open(Constants.PATH_TO_LITIGATION_FILE, 'rb'), delimiter=',')

    for row in litigationReader:

        row_object = NewRowGenerator(*row)

        # already processed.
        if row_object.index in finished_indices:
            continue

        # intentionally skip.
        if row_object.CIK == Constants.CIK_CODE_TO_INDICATE_ROW_SHOULD_BE_SKIPPED:
            continue

        processed_index_counter += 1

        if processed_index_counter > items_to_add:
            break

        #print "BEGIN:", row

        # rows always have a plaintiff but not always a CIK.
        if int(row_object.CIK) > 0:
            # if this row has the CIK-company name mapping, cache it.
            # update the key-value pairing with each row iteration
            # as company CIKSs can change as time goes on.
            if len(row_object.plaintiff) > 0:
                _name_to_cik_mapping[row_object.plaintiff] = row_object.CIK

        else:
            # this row didnt have a CIK. first, check previous rows for the mapping we want.
            # if that doesn't exist, use the company name and edgar to get the
            # potential CIK.
            result = _get_potential_cik_from_company_name(row_object.plaintiff)
            if result is not None:
                row_object.CIK = result

        if int(row_object.CIK) == 0:
            print "Error: No CIK. Index:", row_object.index
            continue

        case_pattern = _get_first_word_of_case_name(row_object.case_name)

        #_perform_check_and_write_to_results_file(case_pattern, index, CIK, original_case_name, row, row_holder)

        pool.apply_async(_perform_check_and_write_to_results_file, \
            args=(case_pattern, row_object, row_holder))

    pool.close()
    pool.join()

    litigationWriter = csv.writer(open(Constants.PATH_TO_NEW_LITIGATION_FILE, 'ab'), delimiter=',')
    for row in row_holder:
        litigationWriter.writerow(row)


class NewRowGenerator(object):

    def __init__(self, index, date_field, CIK, plaintiff, case_name):
        self.index = index
        self.CIK = Utilities.format_CIK(CIK)
        self.date_field = date_field
        self.plaintiff = plaintiff
        self.case_name = case_name
        self._years_in_which_litigation_is_mentioned = set()

    def case_mentioned_in_a_10k_for_a_year(self, year):
        '''
            we found this row's case mentioned in a 10-K for a certain year. add that year to the object
        '''
        year = int(year)
        self._years_in_which_litigation_is_mentioned.add(year)

    def construct_row_with_ordered_fields(self):
        '''
            return a list of the fields of this row in the order that we want to see them in the output csv file.
            note that we are interested in 10-Ks from 2004 to 2012, so check for those particular years in
            self._years_in_which_litigation_is_mentioned
        '''
        returnable = [self.index, self.date_field, self.CIK, self.plaintiff, self.case_name]

        for year in xrange(2004, 2012 + 1):
            if year in self._years_in_which_litigation_is_mentioned:
                returnable.append(1)
            else:
                returnable.append(0)

        return returnable

if __name__ == '__main__':
    start = time.time()

    parser = argparse.ArgumentParser(description='A script that checks to see whether lawsuits are mentioned in defendant 10-Ks.')
    parser.add_argument('-add', type=int, help="Add more rows to the completed output file")
    args = vars(parser.parse_args())
    main(args['add'])

    end = time.time()
    print "Runtime:", end - start, "seconds."
