'''
Created on Jun 3, 2012

@author: mchrzanowski
'''

from __future__ import division
import nltk
import re
from bs4 import BeautifulSoup
from urllib2 import urlopen
from time import time
 

remove_html_tags = lambda text: nltk.clean_html(text)
remove_monetary_figures = lambda text: re.sub("\$[^\s]+", "dollar", text)
remove_numbers = lambda text: re.sub("[0-9]+", "number", text)
remove_email_addresses = lambda text: re.sub("[^\s]+@[^\s]+", 'emailaddr', text)

def remove_urls(text):
    text = re.sub("https?://[^\s]", 'httpaddr', text)
    text = re.sub("www[^\s]", "httpaddr", text)
    return text

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

def get_10k_url_for_a_given_company_and_fiscal_year(CIK, fiscal_year):
    
    SEC_WEBSITE = "http://www.sec.gov/"

    filing_year = get_filing_year_from_fiscal_year(fiscal_year, 2)
    
    if len(filing_year) == 4:
        filing_year = filing_year[2:4]
        
        
    source = urlopen(SEC_WEBSITE + "/cgi-bin/browse-edgar?action=getcompany&CIK=" + str(CIK) + "&type=10-K").read()
    soup = BeautifulSoup(source, "html.parser")
        
    matching_urls = set()

    for link in soup.find_all('a', href=re.compile("/Archives/.*\-" + filing_year + "\-.*\-index\.html?$")):
        url = link['href']
                        
        url = re.sub("\-index\.html?$", ".txt", url, re.I)       # replace the last portion with ".txt" for the full 10-K filing.
        matching_urls.add(url)

    for first_filing in sorted(matching_urls):                  # get first url; these things are numbered.
        return SEC_WEBSITE + first_filing

def sanitize_html_into_working_text(html):
    
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
        text = re.sub("TABLE\s+?OF\s+?CONTENTS.*?^\s*Signature", "", text, count=1, flags=re.M | re.I | re.S)
    
    return text

def get_litigation_footnotes(text):
    
    print "get_litigation_footnotes"
        
    if re.search("Items", text, re.I):
        
        hits = re.finditer("^\s*?Item.*?[0-9]+.*?\n(?=^\s*?Item.*?[0-9]+)", text, re.M | re.I | re.S)
                
        for hit in hits:
            
            # legal proceeding is always mentioned very, very close to the start of the real section
            # dealing with legal proceedings. so, check the first 5 lines for the phrase.
            if re.search("^\s*?Item.*?\n{0,5}?\s*?Legal\s+Proceeding", hit.group(0), re.I | re.M):
                return hit.group(0)
        
        
    
def main():
    
    url = get_10k_url_for_a_given_company_and_fiscal_year(fiscal_year = '2011', CIK = '0001466593') 
    print url
    
    response = urlopen(url).read()

    response = sanitize_html_into_working_text(response)
    response = remove_irrelevant_text(response)
    footnote = get_litigation_footnotes(response)
    
    
    with open("./lol.txt", 'w') as f:
        print "Writing"
#        for num, lol in enumerate(footnotes): f.write("\nNEW: " + str(num) + "\n" + lol)
        f.write(footnote)
#        f.write(response)
        
if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print "Runtime:%r seconds" % (end - start)