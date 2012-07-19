'''
Created on Jun 3, 2012

@author: mchrzanowski
'''

from __future__ import division
from bs4 import BeautifulSoup
from HTMLTagStripper import HTMLTagStripper

import Constants
import CorpusAccess
import LegalProceedingParsing
import litigationfootnoteparsing.parser
import lxml.html.clean
import re
import TextSanitizer
import urllib2
import Utilities

_url_cache = dict()
def _pull_edgar_search_page(CIK):
    if CIK not in _url_cache:
        data = urllib2.urlopen(Constants.SEC_WEBSITE + "/cgi-bin/browse-edgar?action=getcompany&CIK=" + CIK + "&type=10-K").read()
        _url_cache[CIK] = data
    
    return _url_cache[CIK]

def get_name_of_company_from_cik(CIK):
    ''' given a CIK, return the company's name '''
    source = _pull_edgar_search_page(CIK)
    soup = BeautifulSoup(source, "html.parser")
    
    # looks like:
    # u'DOLLAR GENERAL CORP CIK#: 0000029534 (see all company filings)'
    text = soup.find("span", "companyName").get_text()
    text = re.sub("\s+CIK.*", "", text, flags=re.I | re.M | re.S)
    
    return text

def get_10k_url(filing_year, CIK):
    ''' 
        the SEC EDGAR website is extremely to manipulate to get a list of all the index sites for 10-K for a given company:
             website/gunk?action=getcompany&CIK=CIK_YOU_NEED&type=10-K
        once you get the contents of that webpage, you can parse and get all the URLs. those go to index websites for each year.
        you can change the ending of the index website to get the link to the comany's full text submission - exhibits and all -
        for this year's 10-K.
    '''
    
    filing_year = filing_year[2:4]   # always 4 digits long.
    
    source = _pull_edgar_search_page(CIK)
    
    # remove 10-K/A URLs
    source = re.sub("10-K\/A.*?</a>", " ", source, flags=re.M | re.I | re.S)
    soup = BeautifulSoup(source, "html.parser")

    for link in soup.find_all('a', href=re.compile("/Archives/.*\-" + filing_year + "\-.*\-index\.html?$")):
        url = link['href']
        url = re.sub("\-index\.html?$", ".txt", url, re.I)       # replace the last portion with ".txt" for the full 10-K filing.
        return Constants.SEC_WEBSITE + url

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
        results.company_name = get_name_of_company_from_cik(results.CIK)
    
    if results.processed_text is None:

        if raw_website_data is None:

            url = get_10k_url(CIK=results.CIK, filing_year=results.filing_year)
        
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
        self.filing_year = self._sanitize_filing_year(filing_year)
        self.company_name = company_name
        self.legal_proceeding_mention = None
        self.legal_note_mentions = None
        self.processed_text = processed_text
    
    def _sanitize_filing_year(self, year):
        year = str(year)
        if len(year) == 2:
            if year < '50':
                year = '19' + year
            else:
                year = '20' + year
        if len(year) == 1:
            year = '200' + year
             
        return year
        
    def __str__(self):
        return "ParsingResults object. " + \
            "CIK:%s Company Name:%s Filing Year:%s Have Legal Proceeding Mention:%r " + \
            "Have Legal Note Mention:%r" % (self.CIK, self.company_name, self.filing_year, \
                                            self.legal_proceeding_mention, self.legal_note_mention)

    
    
