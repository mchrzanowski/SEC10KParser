'''
Created on Jun 8, 2012

@author: mchrzanowski
'''

import os.path
import shutil
import Constants

def get_processed_website_data_from_corpus(CIK, filing_year):
       
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
    
    path = os.path.join(Constants.PATH_TO_PROCESSED_URL_DATA, CIK) 
    
    if not os.path.exists(path): 
        os.mkdir(path)
    
    path_with_file = os.path.join(path, filing_year + ".txt")
    
    if not os.path.exists(path_with_file):
        with open(path_with_file, 'w') as f:
            f.writelines(data)

def write_to_legal_proceeding_corpus(data, CIK, filing_year, force_write=True):
    ''' 
    we'll dump our resulting data to a text file.
    it will be structured thusly:
       legal_proceeding
            CIK_1
                filing_year_1.txt
                filing_year_2.txt
    and so on. 
    '''
    
    if len(data) == 0:
        raise Exception("Nothing to write!")
                
    # this is normally 10 digits. make it 10 for consistent directory grammar
    while len(CIK) < Constants.CIK_CODE_LENGTH: 
        CIK = '0' + CIK
    
    path = os.path.join(Constants.PATH_TO_LEGAL_PROCEEDING_CORPUS, CIK)
    
    if not os.path.exists(path):
        os.makedirs(path)
        
    path_with_file = os.path.join(path, filing_year + ".txt")
    
    if os.path.exists(path_with_file) and force_write or not os.path.exists(path_with_file):
        with open(path_with_file, 'w') as f:
            f.writelines(data)

