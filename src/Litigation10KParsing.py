'''
Created on Jun 3, 2012

@author: mchrzanowski
'''

from __future__ import division
from bs4 import BeautifulSoup
from HTMLTagStripper import HTMLTagStripper
from TextSanitizer import TextSanitizer
from urllib2 import urlopen

import Constants
import LegalProceedingParsing
import lxml.html.clean
import re


def get_10k_url(filing_year, CIK):
    ''' 
        the SEC EDGAR website is extremely to manipulate to get a list of all the index sites for 10-K for a given company:
             website/gunk?action=getcompany&CIK=CIK_YOU_NEED&type=10-K
        once you get the contents of that webpage, you can parse and get all the URLs. those go to index websites for each year.
        you can change the ending of the index website to get the link to the comany's full text submission - exhibits and all -
        for this year's 10-K.
    '''
    
    filing_year = filing_year[2:4]   # always 4 digits long.
    
    source = urlopen(Constants.SEC_WEBSITE + "/cgi-bin/browse-edgar?action=getcompany&CIK=" + CIK + "&type=10-K").read()
    
    # remove 10-K/A URLs
    source = re.sub("10-K\/A.*?</a>", " ", source, count=0, flags=re.M | re.I | re.S)
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
    # step 5: remove terms that are not regularized (eg, email addresses) 
    #         and replace with a regularized token (eg, emailaddr)
    data = HTMLTagStripper.strip(data)            
    data = TextSanitizer.sanitize(data) 
    
    return data

def _get_litigaton_mentions(result):
    
    # first, check for the LEGAL PROCEEDINGS section
    legal_proceeding_mention = LegalProceedingParsing.get_best_legal_proceeding_hit(result.processed_text)
    result.legal_proceeding_mention = legal_proceeding_mention
    
    # now, get the note sections dealing with legal contingencies
    
    

def parse(CIK, filing_year, processed_website_data=None):
    
    results = ParsingResults(CIK, filing_year)
    
    if processed_website_data is not None:
        results.processed_text = processed_website_data
    
    else:
        url = get_10k_url(CIK=CIK, filing_year=filing_year)
        
        if url is not None:
            response = urlopen(url).read()
            results.processed_text = convert_html_into_clean_text(response)
                    
        else:
            raise Exception("Error: No URL to parse for data.")
    
    _get_litigaton_mentions(results)
    
    return results

class ParsingResults(object):
    
    def __init__(self, CIK, filing_year):
        self.CIK = CIK
        self.filing_year = self._sanitize_filing_year(filing_year)
        self.legal_proceeding_mention = None
        self.legal_note_mention = None
        self.processed_text = None
    
    @staticmethod
    def _sanitize_filing_year(year):
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
            "CIK:%s Filing Year:%s Have Legal Proceeding Mention:%r " + \
            "Have Legal Note Mention:%r" % (self.CIK, self.filing_year, \
                                            self.legal_proceeding_mention, self.legal_note_mention)

    
    
