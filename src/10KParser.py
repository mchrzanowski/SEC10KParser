'''
Created on Jun 3, 2012

@author: mchrzanowski
'''

from __future__ import division

import os.path
import re

from bs4 import BeautifulSoup
from urllib2 import urlopen
from time import time

from HTMLTagStripper import HTMLTagStripper
 

remove_html_tags = lambda text: HTMLTagStripper.strip(text)
remove_monetary_figures = lambda text: re.sub("\$[^\s]+", "dollar", text)
remove_numbers = lambda text: re.sub("[0-9]+", "number", text)
remove_email_addresses = lambda text: re.sub("[^\s]+@[^\s]+", 'emailaddr', text)

def remove_urls(text):
    text = re.sub("https?://[^\s]+", 'httpaddr', text)
    text = re.sub("www[^\s]+", "httpaddr", text)
    return text

def get_10k_url_for_a_given_company_and_year(CIK, fiscal_year=None, filing_year=None):
    
    def get_filing_year_from_fiscal_year(fiscal_year, minimum_digits_required=2):
        ''' 
            10-K for year X will be filed in year X + 1 
            take a number and return a string to preserve formatting.
        '''
        
        fiscal_year = str(fiscal_year)
        number_of_digits = len(fiscal_year)
        
        if number_of_digits == 2 and fiscal_year == '99':
            return '00'
            
        elif number_of_digits == 4 and fiscal_year == '1999':
            return '2000'
        
        else:
            return_string = str(int(fiscal_year) + 1)
            while len(return_string) < minimum_digits_required:
                return_string = '0' + return_string
            return return_string
    
    SEC_WEBSITE = "http://www.sec.gov/"
    
    if filing_year is None:
        filing_year = get_filing_year_from_fiscal_year(fiscal_year, 2)
    
    if len(filing_year) == 4:
        filing_year = filing_year[2:4]
        
    source = urlopen(SEC_WEBSITE + "/cgi-bin/browse-edgar?action=getcompany&CIK=" + str(CIK) + "&type=10-K").read()
    
    # remove 10-K/A URLs
    source = re.sub("10-K\/A.*?</a>", " ", source, count=0, flags=re.M | re.I | re.S)
    soup = BeautifulSoup(source, "html.parser")
        

    for link in soup.find_all('a', href=re.compile("/Archives/.*\-" + filing_year + "\-.*\-index\.html?$")):
        
        url = link['href']
        url = re.sub("\-index\.html?$", ".txt", url, re.I)       # replace the last portion with ".txt" for the full 10-K filing.
        return SEC_WEBSITE + url


def sanitize_html_into_working_text(html):
    
    print 'sanitize_html_into_working_text'
    html = remove_html_tags(html)
    html = remove_monetary_figures(html)
    html = remove_urls(html)
    html = remove_email_addresses(html)
        
    return html

def remove_irrelevant_text(text):
    
    print "remove_irrelevant_text"
    
    # remove table of contents. this is a nasty piece of data 
    # that obeys all the same rules as the rest of the 10-K, but it has 
    # no information other than headers.
    # this usually has a link to the signature section at the very bottom.
    if re.search("TABLE\s+?OF\s+?CONTENTS", text, re.I):
        new_text = re.sub("TABLE\s+?OF\s+?CONTENTS.*?^\s*?Signature", "", text, count=1, flags=re.M | re.I | re.S)
        if len(text) / 2 < len(new_text):
            text = new_text
    
    return text

def get_litigation_footnotes(text):
    
    def check_if_valid_hit(hit):
        
        # check to see whether it belongs to the table of contents
        hit = re.sub("\s+", " ", hit)
        
        if len(hit) < 200:
            return False
        
        return True
    
    def default_regex():
        ''' so many 10-Ks have the litigation item structured thusly:
        Item 3. LITIGATION PROCEEDING
            blah blah
        Item 4. blah blah
        Item 5. blah blah
        
        take advantage of this by using the numbers as well as the fact that 
        the body is between these two Item headers '''
        
        return "^\s*Item\s*?3.*?(?=Item\s*?4)"
    
    def try_all_numbers_after_4():
        ''' this regex is slightly different than the default regex: it allows
        for more matching on the Item number. Some 10-Ks miss Item 4 for some reason.'''
        return "^\s*Item\s*?3.*?(?=Item\s*?[5-9]+)"
    
    print "get_litigation_footnotes"
        
    if re.search("Item", text, re.I):
        
        for regex in (default_regex(), try_all_numbers_after_4()):
        
        
            hits = re.finditer(regex, text, re.M | re.I | re.S)
            
            for hit in hits:
                                        
                if not check_if_valid_hit(hit.group(0)):
                    continue
                
                # legal proceeding is always mentioned very, very close to the start of the real section
                heading = ''.join(group for group in hit.group(0))[:200]
                                        
                # dealing with legal proceedings. so, check the first 5 lines for the phrase.
                if re.search("Legal\s+?Proceeding", heading, re.I | re.M):
                    return hit.group(0)        


def write_to_file(CIK, filing_year, text):
    ''' 
    we'll dump our resulting data to a text file.
    it will be structured thusly:
       corpus
            CIK_1
                filing_year_1.txt
                filing_year_2.txt
    and so on. 
    '''
    
    print "write_to_file"
    
    # this is normally 10 digits. make it 10 for consistent directory grammar
    while len(CIK) < 10:   
        CIK = '0' + CIK
    
    path = "./corpus/" + CIK
    
    if not os.path.exists(path):
        os.makedirs(path)
    
    with open(path + "/" + filing_year + ".txt", 'w') as f:
        f.write(text)
    
def main():
    
    CIK = '0000001750'
    
    for i in xrange(2004, 2012 + 1):
        
        filing_year = str(i)
    
        url = get_10k_url_for_a_given_company_and_year(filing_year=filing_year, CIK=CIK) 
        print url
        
        if url is not None:
        
            response = urlopen(url).read()
            response = sanitize_html_into_working_text(response)
            
            footnote = get_litigation_footnotes(response)
            
            if footnote is not None:        
                write_to_file(CIK, filing_year, footnote)
            else:
                print "No footnote returned!"
        
        
        
if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print "Runtime:%r seconds" % (end - start)
