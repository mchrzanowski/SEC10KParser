'''
Created on Jun 8, 2012

@author: mchrzanowski
'''

from time import time

from Litigation10KParser import Litigation10KParser

import os.path
import Constants


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
    
    with open(path + "/" + filing_year + ".txt", 'w') as f:
        f.writelines(mentions)

def main():
    
    CIK = '0000789073'
    
    for i in xrange(2004, 2012 + 1):
                
        print "Begin:\tCIK:%s\t%s" % (CIK, i)
        
        try:
            
            l = Litigation10KParser(CIK, i)
            l.parse()   
            
            #for mention in l.mentions: print mention
            
            write_to_corpus(CIK=l.CIK, mentions=l.mentions, filing_year=l.filing_year)
            
        except Exception as exception:
            print "Exception: ", exception
    
if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print "Runtime:%r seconds" % (end - start)