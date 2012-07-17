'''
Created on Jul 16, 2012

@author: mchrzanowski
'''

import CorpusAccess
import Constants
import Litigation10KParsing
import re
import multiprocessing
import os.path
import time
import traceback
import Utilities

def _get_results(cik, start_year, end_year):
    
    results = dict()

    cik = Utilities.format_CIK(cik)

    for year in xrange(start_year, end_year + 1):

        year = str(year)
        
        print "Processing %s %s" % (cik, year)
        
        lfp_path = os.path.join(Constants.PATH_TO_LEGAL_FOOTNOTE_CORPUS, cik, year + '.txt')
        lpp_path = os.path.join(Constants.PATH_TO_LEGAL_PROCEEDING_CORPUS, cik, year + '.txt')

        processed_data = CorpusAccess.get_processed_website_data_from_corpus(cik, year)    
        company_name = CorpusAccess.get_company_name_from_corpus(cik)

        get_lpp_only = False
        get_lfp_only = False

        if os.path.exists(lfp_path):
            get_lpp_only = True

        if os.path.exists(lpp_path):
            get_lfp_only = True

        try:
            result = Litigation10KParsing.parse(cik, year, company_name, processed_website_data=processed_data, \
                get_legal_proceeding_only=get_lpp_only, get_litigation_footnotes_only=get_lfp_only)

            if get_lpp_only:
                with open(lfp_path) as f:
                    result.legal_note_mentions = f.read()
            else:
                if result.legal_note_mentions is not None:
                    try:
                        CorpusAccess.write_to_litigation_footnote_corpus(result.legal_note_mentions, result.CIK, result.filing_year)
                    except Exception as exception:
                        print "Exception: ", exception
                        traceback.print_exc()
            if get_lfp_only:
                with open(lpp_path) as f:
                    result.legal_proceeding_mention = f.read()
            else:
                if result.legal_proceeding_mention is not None:
                    try:
                        CorpusAccess.write_to_legal_proceeding_corpus(CIK=result.CIK, \
                            data=result.legal_proceeding_mention, filing_year=result.filing_year)
                    except Exception as exception:
                        print "Exception: ", exception
                        traceback.print_exc()

            if company_name is None and result.company_name is not None:
                try:
                    CorpusAccess.write_company_name_and_cik_mapping_to_corpus(result.CIK, result.company_name)
                except Exception as exception:
                    print "Exception: ", exception
                    traceback.print_exc()

            if processed_data is None and result.processed_text is not None:  
                try:      
                    CorpusAccess.write_processed_url_data_to_file(data=result.processed_text, CIK=result.CIK, filing_year=result.filing_year)
                except Exception as exception:
                    print "Exception: ", exception
                    traceback.print_exc()
            
            results[year] = result

        except Exception as exception:
            print "Exception: ", exception
            traceback.print_exc()

    return results

def _write_all_file(cik_path, results):
    all_file = os.path.join(cik_path, 'ALL.txt')
    with open(all_file, 'w') as f:
        for year in sorted(results):
            f.write("\n" + year + ":\n")
            if results[year].legal_proceeding_mention is not None:
                f.writelines(results[year].legal_proceeding_mention)
            f.write("\n\n")
            if results[year].legal_note_mentions is not None:
                f.writelines(results[year].legal_note_mentions)
            f.write("\n====================================================\n")

def _write_year_files(path, results):
    for year in sorted(results):
        with_year = os.path.join(path, year + '.txt')
        with open(with_year, 'w') as f:
            if results[year].legal_proceeding_mention is not None:
                f.writelines(results[year].legal_proceeding_mention)
            f.write("\n\n")
            if results[year].legal_note_mentions is not None:
                f.writelines(results[year].legal_note_mentions)

def _write_files_to_corpus(root_path, cik):

    cik = Utilities.format_CIK(cik)
    results = _get_results(cik, 2004, 2012)

    name = CorpusAccess.get_company_name_from_corpus(cik)

    name = re.sub("\/", "", name)

    folder_name = cik + " - " + name

    cik_path = os.path.join(root_path, folder_name)
    if not os.path.exists(cik_path):
        os.makedirs(cik_path)

    _write_year_files(cik_path, results)
    _write_all_file(cik_path, results)


def pretty_print(ciks):
    if not os.path.exists(Constants.PATH_TO_DROPBOX_DIRECTORY):
        os.makedirs(Constants.PATH_TO_DROPBOX_DIRECTORY)

    
    pool = multiprocessing.Pool(maxtasksperchild=2)

    for cik in ciks:
        pool.apply_async(_write_files_to_corpus, args=(Constants.PATH_TO_DROPBOX_DIRECTORY, cik))

    pool.close()
    pool.join()

def _go_through_corpus():
    ciks = set()
    with open("../etc/cik_mike_5june2012.csv") as f:
        for line in f:
            line = line.strip()
            if re.match("\+", line):
                line = re.sub("\+", "", line)
                ciks.add(line)
            
    return ciks

def _get_ciks_to_print():
    ciks = set()
    with open("../etc/cik_mike_5june2012.csv") as f:
        for line in f:
            line = line.strip()
            if re.match("^0", line):
                ciks.add(line)
            if len(ciks) == 50:
                break

    return ciks

def main():
    ciks = _go_through_corpus()

    print "CIKs:"
    for cik in ciks:
        print cik
    
    pretty_print(ciks)

if __name__ == '__main__':
    main()