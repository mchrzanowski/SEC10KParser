'''
Created on Jun 8, 2012

@author: mchrzanowski
'''

import CIKFormatter
import Constants
import os.path
import shutil

def _separate_items_with_delimiters(data):
    formatted_data = list()
    for datum in data:
        formatted_data.append(datum)
        formatted_data.append('\n======================================\n')
    
    return formatted_data

def get_processed_website_data_from_corpus(CIK, filing_year):
    
    CIK = CIKFormatter.format_CIK(CIK)
       
    candidate_path = os.path.join(Constants.PATH_TO_PROCESSED_URL_DATA, CIK, str(filing_year) + ".txt")
    
    if os.path.exists(candidate_path):
        with open(candidate_path, 'r') as f:
            return f.read()
    
    return None

def wipe_existing_failed_unit_tests():
    if os.path.exists(Constants.PATH_TO_FAILED_UNIT_TESTS):
        for sub_folder in os.listdir(Constants.PATH_TO_FAILED_UNIT_TESTS):
            shutil.rmtree(os.path.join(Constants.PATH_TO_FAILED_UNIT_TESTS, sub_folder))
        print "Previous failed unit tests deleted."

def write_comparison_to_file(new_output, old_output, CIK, filing_year):
    
    CIK = CIKFormatter.format_CIK(CIK)
    
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

def write_processed_url_data_to_file(data, CIK, filing_year):
    
    CIK = CIKFormatter.format_CIK(CIK)
    
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
                
    CIK = CIKFormatter.format_CIK(CIK)

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
    CIK = CIKFormatter.format_CIK(CIK)
    
    path = os.path.join(Constants.PATH_TO_LEGAL_FOOTNOTE_CORPUS, CIK)
    write_data_to_corpus(_separate_items_with_delimiters(data), CIK, filing_year, path)

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
    CIK = CIKFormatter.format_CIK(CIK)
    
    path = os.path.join(Constants.PATH_TO_LEGAL_PROCEEDING_CORPUS, CIK)
    write_data_to_corpus(_separate_items_with_delimiters(data), CIK, filing_year, path)
    

