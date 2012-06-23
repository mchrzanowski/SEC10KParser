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
    
    CIK = Utilities.format_CIK('0001035985')
    
    for i in xrange(2004, 2012 + 1):
                
        print "Begin:\tCIK:%s\t%s" % (CIK, i)
        
        try:
            
            processed_data = CorpusAccess.get_processed_website_data_from_corpus(CIK, i)

            results = Litigation10KParsing.parse(CIK, i, processed_website_data=processed_data)   
                        
            #for mention in l.mentions: print mention    
            if processed_data is None:        
                CorpusAccess.write_processed_url_data_to_file(data=results.processed_text, CIK=results.CIK, filing_year=results.filing_year)
                print "Wrote processed url data"
            else:
                print "Skipped writing processed url data."
            
            if results.legal_proceeding_mention is not None:
                CorpusAccess.write_to_legal_proceeding_corpus(CIK=results.CIK, data=results.legal_proceeding_mention, filing_year=results.filing_year)
                print "Wrote legal proceeding data to corpus."
            else:
                print "No Legal Proceeding Section to Write!"
                
            if len(results.legal_note_mentions) > 0:
                CorpusAccess.write_to_litigation_footnote_corpus(results.legal_note_mentions, results.CIK, results.filing_year)
                print "Wrote legal footnotes to corpus."
            else:
                print "No legal footnotes to write!"
            
        except Exception as exception:
            print "Exception: ", exception
            traceback.print_exc()

if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print "Runtime:%r seconds" % (end - start)
