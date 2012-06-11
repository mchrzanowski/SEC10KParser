'''
Created on Jun 8, 2012

@author: mchrzanowski
'''

from time import time

from Litigation10KParser import Litigation10KParser

import os.path
import shutil
import Constants

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

def write_processed_url_data_to_file(text, CIK, filing_year):
    
    path = os.path.join(Constants.PATH_TO_PROCESSED_URL_DATA, CIK) 
    
    if not os.path.exists(path): 
        os.mkdir(path)
    
    path_with_file = os.path.join(path, filing_year + ".txt")
    
    if not os.path.exists(path_with_file):
        with open(path_with_file, 'w') as f:
            f.writelines(text)

def write_to_corpus(mentions, CIK, filing_year):
    ''' 
    we'll dump our resulting data to a text file.
    it will be structured thusly:
       corpus
            CIK_1
                filing_year_1.txt
                filing_year_2.txt
    and so on. 
    '''
    
    if len(mentions) == 0:
        raise Exception("Nothing to write!")
                
    # this is normally 10 digits. make it 10 for consistent directory grammar
    while len(CIK) < Constants.CIK_CODE_LENGTH: 
        CIK = '0' + CIK
    
    path = os.path.join(Constants.PATH_TO_CORPUS, CIK)
    
    if not os.path.exists(path):
        os.makedirs(path)
        
    path_with_file = os.path.join(path, filing_year + ".txt")
    
    if not os.path.exists(path_with_file):
        with open(path_with_file, 'w') as f:
            f.writelines(mentions)

def main():
    
    CIK = '0000812348'
    
    for i in xrange(2004, 2012 + 1):
                
        print "Begin:\tCIK:%s\t%s" % (CIK, i)
        
        try:
            
            l = Litigation10KParser(CIK, i)
            l.parse()   
            
            #for mention in l.mentions: print mention            
            write_processed_url_data_to_file(text=l.text, CIK=l.CIK, filing_year=l.filing_year)
            
            write_to_corpus(CIK=l.CIK, mentions=l.mentions, filing_year=l.filing_year)

            
        except Exception as exception:
            print "Exception: ", exception
    
if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print "Runtime:%r seconds" % (end - start)