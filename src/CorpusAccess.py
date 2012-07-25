'''
Created on Jun 8, 2012

@author: mchrzanowski
'''

import Constants
import lockfile
import os.path
import re
import shutil
import Utilities


def get_CIK_from_corpus(company_name):
    
    if os.path.exists(Constants.PATH_TO_COMPANY_NAME_AND_CIK_MAPPING_FILE):
        with open(Constants.PATH_TO_COMPANY_NAME_AND_CIK_MAPPING_FILE, 'r') as f:
            for line in f:
                data = re.split(Constants.COMPANY_NAME_AND_CIK_MAPPING_FILE_DELIMITER, line)
                if len(data) != 2:
                    continue
                if data[1] == company_name:
                    return data[0]

def get_company_name_from_corpus(CIK):
    
    CIK = Utilities.format_CIK(CIK)
    if os.path.exists(Constants.PATH_TO_COMPANY_NAME_AND_CIK_MAPPING_FILE):
        with open(Constants.PATH_TO_COMPANY_NAME_AND_CIK_MAPPING_FILE, 'r') as f:
            for line in f:
                data = re.split(Constants.COMPANY_NAME_AND_CIK_MAPPING_FILE_DELIMITER, line)
                if len(data) != 2:
                    continue
                if data[0] == CIK:
                    return data[1]

def write_company_name_and_cik_mapping_to_corpus(CIK, company_name):
    
    company_name = company_name.strip("\n\r\t\s")
    CIK = Utilities.format_CIK(CIK)
        
    if CIK is None or company_name is None:
        return None
    
    mapping = {CIK : company_name}

    if os.path.exists(Constants.PATH_TO_COMPANY_NAME_AND_CIK_MAPPING_FILE):        
        with open(Constants.PATH_TO_COMPANY_NAME_AND_CIK_MAPPING_FILE, 'r') as f:
            for line in f:
                data = re.split(Constants.COMPANY_NAME_AND_CIK_MAPPING_FILE_DELIMITER, line)
                if len(data) != 2:
                    continue
                if data[0] != CIK:
                    mapping[data[0]] = data[1]
    
    with lockfile.FileLock(Constants.PATH_TO_COMPANY_NAME_AND_CIK_MAPPING_FILE), \
    open(Constants.PATH_TO_COMPANY_NAME_AND_CIK_MAPPING_FILE, 'w') as f:
        for key in mapping:
            f.write(key + Constants.COMPANY_NAME_AND_CIK_MAPPING_FILE_DELIMITER + mapping[key] + '\n')

def _walk_directory(corpus_root):
    get_filing_year_from_corpus_file = re.compile("\.txt", re.I)
    
    for potential_cik in os.listdir(corpus_root):
        if os.path.isdir(os.path.join(corpus_root, potential_cik)):
            for filing_year_file in os.listdir(os.path.join(corpus_root, potential_cik)):
                path_to_file = os.path.join(corpus_root, potential_cik, filing_year_file)
                filing_year = re.sub(get_filing_year_from_corpus_file, "", filing_year_file)
                yield potential_cik, filing_year, path_to_file

def access_every_file_in_legal_footnotes_corpus():
    corpus_root = Constants.PATH_TO_LEGAL_FOOTNOTE_CORPUS
    for CIK, filing_year, filepath in _walk_directory(corpus_root):
        yield CIK, filing_year, filepath 

def access_every_file_in_legal_proceeding_corpus():
    
    corpus_root = Constants.PATH_TO_LEGAL_PROCEEDING_CORPUS
    for CIK, filing_year, filepath in _walk_directory(corpus_root):
        yield CIK, filing_year, filepath 
                

def get_processed_website_data_from_corpus(CIK, filing_year):
    
    CIK = Utilities.format_CIK(CIK)
    filing_year = Utilities.sanitize_filing_year(filing_year)
       
    candidate_path = os.path.join(Constants.PATH_TO_PROCESSED_URL_DATA, CIK, str(filing_year) + ".txt")
    
    if os.path.exists(candidate_path):
        with open(candidate_path, 'r') as f:
            return f.read()
    
    return None

def wipe_existing_failed_unit_tests():
    if os.path.exists(Constants.PATH_TO_FAILED_UNIT_TESTS):
        for sub_item in os.listdir(Constants.PATH_TO_FAILED_UNIT_TESTS):
            item = os.path.join(Constants.PATH_TO_FAILED_UNIT_TESTS, sub_item)
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)
        print "Previous failed unit tests deleted."

def write_comparison_to_file(new_output, old_output, CIK, filing_year):
    
    CIK = Utilities.format_CIK(CIK)
    
    path = os.path.join(Constants.PATH_TO_FAILED_UNIT_TESTS, CIK)
    
    if not os.path.exists(path): 
        os.makedirs(path)
        
    log_file = os.path.join(path, filing_year + '.txt')
    
    with open(log_file, 'w') as f:
        
        print "Writing log of failed unit test to %s" % log_file
        
        f.write("OLD:\n")
        f.writelines(old_output)
        f.write("\n")
        f.write("================================================")
        f.write("\n")
        f.write("NEW:\n")
        f.writelines(new_output)

def write_raw_url_data_to_file(data, CIK, filing_year):
    CIK = Utilities.format_CIK(CIK)
    filing_year = Utilities.sanitize_filing_year(filing_year)
    
    path = os.path.join(Constants.PATH_TO_RAW_URL_DATA, CIK) 
    
    if not os.path.exists(path): 
        os.mkdir(path)
    
    path_with_file = os.path.join(path, filing_year + ".txt")
    
    if not os.path.exists(path_with_file):
        with open(path_with_file, 'w') as f:
            f.writelines(data)

def get_raw_website_data_from_corpus(CIK, filing_year):
    
    CIK = Utilities.format_CIK(CIK)
    filing_year = Utilities.sanitize_filing_year(filing_year)
    
    candidate_path = os.path.join(Constants.PATH_TO_RAW_URL_DATA, CIK, str(filing_year) + ".txt")
    
    if os.path.exists(candidate_path):
        with open(candidate_path, 'rb') as f:
            return f.read()
    

def write_processed_url_data_to_file(data, CIK, filing_year):
    
    CIK = Utilities.format_CIK(CIK)
    filing_year = Utilities.sanitize_filing_year(filing_year)
    
    path = os.path.join(Constants.PATH_TO_PROCESSED_URL_DATA, CIK) 
    
    if not os.path.exists(path): 
        os.mkdir(path)
    
    path_with_file = os.path.join(path, filing_year + ".txt")
    
    if not os.path.exists(path_with_file):
        with open(path_with_file, 'w') as f:
            f.writelines(data)
          
            
def write_data_to_corpus(data, CIK, filing_year, path):
    
    if data is None or len(data) == 0:
        raise Exception("Nothing to write!")
                    
    CIK = Utilities.format_CIK(CIK)
    filing_year = Utilities.sanitize_filing_year(filing_year)

    if not os.path.exists(path):
        os.makedirs(path)
        
    path_with_file = os.path.join(path, filing_year + ".txt")
    
    if os.path.exists(path_with_file) or not os.path.exists(path_with_file):
        with open(path_with_file, 'w') as f:
            f.writelines(data)     
    
def write_to_litigation_footnote_corpus(data, CIK, filing_year):
    ''' 
    we'll dump our resulting data to a text file.
    it will be structured thusly:
       legal_proceeding
            CIK_1
                filing_year_1.txt
                filing_year_2.txt
    and so on. 
    '''
    CIK = Utilities.format_CIK(CIK)
    filing_year = Utilities.sanitize_filing_year(filing_year)
    
    path = os.path.join(Constants.PATH_TO_LEGAL_FOOTNOTE_CORPUS, CIK)
    write_data_to_corpus(data, CIK, filing_year, path)

def write_to_legal_proceeding_corpus(data, CIK, filing_year):
    ''' 
    we'll dump our resulting data to a text file.
    it will be structured thusly:
       legal_foonotes
            CIK_1
                filing_year_1.txt
                filing_year_2.txt
    and so on. 
    '''
    CIK = Utilities.format_CIK(CIK)
    filing_year = Utilities.sanitize_filing_year(filing_year)
    
    path = os.path.join(Constants.PATH_TO_LEGAL_PROCEEDING_CORPUS, CIK)
    write_data_to_corpus(data, CIK, filing_year, path)
    

