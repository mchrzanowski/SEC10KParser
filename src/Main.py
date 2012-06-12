'''
Created on Jun 11, 2012

@author: mchrzanowski
'''

import CorpusAccess
import Litigation10KParsing
import time

def main():
    
    CIK = '0000028917'
    
    for i in xrange(2004, 2012 + 1):
                
        print "Begin:\tCIK:%s\t%s" % (CIK, i)
        
        try:
            
            processed_data = CorpusAccess.get_processed_website_data_from_corpus(CIK, i)
            
            results = Litigation10KParsing.parse(CIK=CIK, filing_year=i, processed_data)   
            
            #for mention in l.mentions: print mention    
            if processed_data is None:        
                CorpusAccess.write_processed_url_data_to_file(data=results.processed_text, CIK=results.CIK, filing_year=results.filing_year)
            
            CorpusAccess.write_to_legal_proceeding_corpus(CIK=results.CIK, data=results.legal_proceeding_mention, filing_year=results.filing_year)

            
        except Exception as exception:
            print "Exception: ", exception
    
if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print "Runtime:%r seconds" % (end - start)
