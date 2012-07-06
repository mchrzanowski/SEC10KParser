'''
Created on Jun 11, 2012

@author: mchrzanowski
'''

import CorpusAccess
import Litigation10KParsing
import time
import traceback
import Utilities

def main():
    
    CIK = Utilities.format_CIK('60302')
    
    for year in xrange(2007, 2007 + 1):
                
        print "Begin:\tCIK:%s\t%s" % (CIK, year)
        
        try:
            
            processed_data = CorpusAccess.get_processed_website_data_from_corpus(CIK, year)

            results = Litigation10KParsing.parse(CIK, year, processed_website_data=processed_data)   
            
            print "Wrote Processed URL Data: ",
              
            if processed_data is None:        
                CorpusAccess.write_processed_url_data_to_file(data=results.processed_text, CIK=results.CIK, filing_year=results.filing_year)
                print "\tYES"
            else:
                print "\tNO"
            
            print "Wrote Legal Proceeding Data: ",
            if results.legal_proceeding_mention is not None:
                CorpusAccess.write_to_legal_proceeding_corpus(CIK=results.CIK, data=results.legal_proceeding_mention, filing_year=results.filing_year)
                print "\tYES"
            else:
                print "\tNO"
            
            print "Wrote Legal Footnote Data: ",    
            if len(results.legal_note_mentions) > 0:
                CorpusAccess.write_to_litigation_footnote_corpus(results.legal_note_mentions, results.CIK, results.filing_year)
                print "\tYES"
            else:
                print "\tNO"
            
        except Exception as exception:
            print "Exception: ", exception
            traceback.print_exc()

if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print "Runtime:%r seconds" % (end - start)
