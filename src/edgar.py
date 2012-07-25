from __future__ import division

import bs4
import CorpusAccess
import Constants
import multiprocessing
import re
import urllib2

_manager = multiprocessing.Manager()
_url_cache = _manager.dict()
_processed_cache = _manager.dict()

_url_mutex= multiprocessing.Lock()
_processed_mutex = multiprocessing.Lock()

def _transform_company_name_into_edgar_grammar(name):
    ''' 
        remove common sources of problems when 
        mapping company names to EDGAR CIKs 
    '''

    name = re.sub("\.", "", name)
    name = re.sub("\'", "", name)

    name = re.sub("-CL.*", "", name)
    name = re.sub("/.*", "", name)

    name = re.sub("INTL", "International", name)

    name = re.sub("\s+", "+", name)
    name = re.sub("-", "+", name)

    return name

def _pull_edgar_search_page(CIK=None, company_name=None):
    '''
        get the EDGAR search page for a passed in CIK or company name. 
        used cached data when possible.
    '''

    # maintain an exclusive zone so that one process doesn't
    # try to access the cache while another is deleting 
    # data from it.
    _url_mutex.acquire()

    result = None

    if CIK is not None:
        if CIK not in _url_cache:
            website = Constants.SEC_WEBSITE + "/cgi-bin/browse-edgar?action=getcompany&CIK=" + CIK + "&type=10-K"
            data = urllib2.urlopen(website).read()
            _url_cache[CIK] = data

        result = _url_cache[CIK]

    elif company_name is not None:

        company_name = _transform_company_name_into_edgar_grammar(company_name)
        if company_name not in _url_cache:

            website = Constants.SEC_WEBSITE + "/cgi-bin/browse-edgar?action=getcompany&company=" + company_name + "&type=10-K"
            data = None
            
            if website is not None:
                data = urllib2.urlopen(website).read()
            
            _url_cache[company_name] = data
        
        result = _url_cache[company_name]

    if len(_url_cache) > 1024:
        for key in _url_cache.keys():
            del _url_cache[key]

    _url_mutex.release()
    
    return result

def _process_url_into_soup_and_get_data(url, text_editing=None):
    ''' 
        soupify the raw URL data. if a text manipulator function
        is passed in, apply it
    '''

    # maintain an exclusive zone so that one process doesn't
    # try to access the cache while another is deleting 
    # data from it.
    _processed_mutex.acquire()

    data = None
    if len(_processed_cache) > 1024:
        for key in _processed_cache.keys():
            del _processed_cache[key]

    if url not in _processed_cache:
        soup = bs4.BeautifulSoup(url, "html.parser")
        _processed_cache[url] = soup

    data = _processed_cache[url]
    
    _processed_mutex.release()

    if text_editing is not None:
        return text_editing(data)

    return data

def _get_company_name_from_soup(soup):
    ''' from the beautifulsoup output, get the company name '''

    text = soup.find("span", "companyName").get_text()

    # looks like:
    # u'DOLLAR GENERAL CORP CIK#: 0000029534 (see all company filings)'
    text = re.sub("\s+CIK.*", "", text, flags=re.I | re.M | re.S)

    return text

def get_name_of_company_from_cik(CIK):
    ''' given a CIK, return the company's name '''
    url_data = _pull_edgar_search_page(CIK)
    company_name = _process_url_into_soup_and_get_data(url_data, _get_company_name_from_soup)
    
    if company_name is not None and re.search("[A-Za-z]+", company_name):
        CorpusAccess.write_company_name_and_cik_mapping_to_corpus(CIK, name)
    
    return text

def _get_cik_from_soup(soup):
    
    fragments = soup.find("span", "companyName")

    if fragments is not None:
        
        text = fragments.get_text()

        # looks like:
        # u'DOLLAR GENERAL CORP CIK#: 0000029534 (see all company filings)'
        CIK = re.sub(".*CIK:\s*", "", text, flags=re.I | re.M | re.S)
        CIK = re.sub("[^0-9]", "", CIK, flags=re.I | re.M | re.S)

        return CIK

def get_cik_of_company_from_name(name):
    ''' given a company name, return the company's name '''

    url_data = _pull_edgar_search_page(company_name=name)

    CIK = _process_url_into_soup_and_get_data(url_data, _get_cik_from_soup)
    
    if CIK is not None:
        CorpusAccess.write_company_name_and_cik_mapping_to_corpus(CIK, name)

    return CIK


def get_10k_url(filing_year, CIK):
    ''' 
        the SEC EDGAR website is extremely easy to manipulate to get a list of all the index sites for 10-K for a given company:
             website/gunk?action=getcompany&CIK=CIK_YOU_NEED&type=10-K
        once you get the contents of that webpage, you can parse and get all the URLs. those go to index websites for each year.
        you can change the ending of the index website to get the link to the comany's full text submission - exhibits and all -
        for this year's 10-K.
    '''
    filing_year = str(filing_year)
    filing_year = filing_year[2:4]   # always 4 digits long.
    
    source = _pull_edgar_search_page(CIK)
    
    # remove 10-K/A URLs
    source = re.sub("10-K\/A.*?</a>", " ", source, flags=re.M | re.I | re.S)
    soup = bs4.BeautifulSoup(source, "html.parser")

    for link in soup.find_all('a', href=re.compile("/Archives/.*\-" + filing_year + "\-.*\-index\.html?$")):
        url = link['href']
        url = re.sub("\-index\.html?$", ".txt", url, re.I)       # replace the last portion with ".txt" for the full 10-K filing.
        return Constants.SEC_WEBSITE + url
