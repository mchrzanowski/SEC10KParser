'''
Created on Jun 11, 2012

@author: mchrzanowski
'''

import CorpusAccess
import Litigation10KParsing
import time

def main():
    
    CIK = '0001163165'
    
    for i in xrange(2010, 2010 + 1):
                
        print "Begin:\tCIK:%s\t%s" % (CIK, i)
        
        try:
            
#            processed_data = CorpusAccess.get_processed_website_data_from_corpus(CIK, i)
            
            processed_data = None                   
            results = Litigation10KParsing.parse(CIK, i, processed_website_data=processed_data)   
                        
            #for mention in l.mentions: print mention    
            if processed_data is None:        
                CorpusAccess.write_processed_url_data_to_file(data=results.processed_text, CIK=results.CIK, filing_year=results.filing_year)
                print "Wrote processed url data"
            else:
                print "skipping writing processed url data."
            
            if results.legal_proceeding_mention is not None:
                CorpusAccess.write_to_legal_proceeding_corpus(CIK=results.CIK, data=results.legal_proceeding_mention, filing_year=results.filing_year)
                print "Wrote legal proceeding data to corpus."
            else:
                print "No Legal Proceeding Section to Write!"
            
        except Exception as exception:
            print "Exception: ", exception
    
if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print "Runtime:%r seconds" % (end - start)
