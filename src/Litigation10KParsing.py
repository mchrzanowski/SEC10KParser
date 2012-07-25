'''
Created on Jun 3, 2012

@author: mchrzanowski
'''

from HTMLTagStripper import HTMLTagStripper

import edgar
import LegalProceedingParsing
import litigationfootnoteparsing.parser
import lxml.html.clean
import re
import Utilities

def convert_html_into_clean_text(data):
    ''' takes html data and outputs sanitized ascii text '''
    
    # THE PARSING GUIDE:
    # Part 1: Fix horrible HTML code into something proper.
    # Part 2: Parse the tagging and get to the inner text goodness.
    
    # Part 1
    # step 1: go from a string to a lxml-specific object. this is to control the encoding. 
    # step 2: prettify the html.
    # step 3: go from the lxml object to an ascii-encoded string.
    data = lxml.html.fromstring(data)
    data = lxml.html.clean.clean_html(data)
    data = lxml.html.tostring(data, encoding="ascii")
    
    # Part 2
    # step 4: strip the HTML tags.
    data = HTMLTagStripper.strip(data)            
    
    return data

def _get_litigaton_mentions(result, get_legal_proceeding_only, get_litigation_footnotes_only):
    
    # first, check for the LEGAL PROCEEDINGS section
    if not get_litigation_footnotes_only:
        legal_proceeding_mention = LegalProceedingParsing.get_best_legal_proceeding_hit(result.processed_text)
        result.legal_proceeding_mention = legal_proceeding_mention
    
    # now, get the note sections dealing with legal contingencies
    if not get_legal_proceeding_only:
        legal_oriented_notes = litigationfootnoteparsing.parser.get_best_litigation_note_hits(result.processed_text)
        result.legal_note_mentions = legal_oriented_notes
    

def parse(CIK, filing_year, company_name=None, raw_website_data=None, \
    processed_website_data=None, get_legal_proceeding_only=False, get_litigation_footnotes_only=False):
    
    results = ParsingResults(CIK, filing_year, company_name, processed_text=processed_website_data)
    
    if results.company_name is None:
        results.company_name = edgar.get_name_of_company_from_cik(results.CIK)
    
    if results.processed_text is None:

        if raw_website_data is None:

            url = edgar.get_10k_url(CIK=results.CIK, filing_year=results.filing_year)
        
            if url is not None:
                response = urllib2.urlopen(url).read()
                CorpusAccess.write_raw_url_data_to_file(response, results.CIK, results.filing_year)
            else:
                raise Exception("Error: No URL to parse for data.")

        else:
            response = raw_website_data

        results.processed_text = convert_html_into_clean_text(response)                    

    _get_litigaton_mentions(results, get_legal_proceeding_only, get_litigation_footnotes_only)
    
    return results


class ParsingResults(object):
    
    def __init__(self, CIK, filing_year, company_name, processed_text):
        self.CIK = Utilities.format_CIK(CIK)
        self.filing_year = Utilities.sanitize_filing_year(filing_year)
        self.company_name = company_name
        self.legal_proceeding_mention = None
        self.legal_note_mentions = None
        self.processed_text = processed_text
        
    def __str__(self):
        return "ParsingResults object. " + \
            "CIK:%s Company Name:%s Filing Year:%s Have Legal Proceeding Mention:%r " + \
            "Have Legal Note Mention:%r" % (self.CIK, self.company_name, self.filing_year, \
                                            self.legal_proceeding_mention, self.legal_note_mention)

    
    
