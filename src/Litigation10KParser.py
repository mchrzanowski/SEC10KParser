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
import LegalProceedingRegexCollection as LPRC
import nltk
import os.path
import re

import Utilities

class Litigation10KParser(object):
    
    SEC_WEBSITE = Constants.SEC_WEBSITE
    
    def __init__(self, CIK, filing_year):
        self.CIK = CIK
        self.filing_year = self.__sanitize_filing_year(filing_year)
        self.mentions = []
        self.text = ""
        
    def __str__(self):
        return "Litigation10KParser object. CIK:%s Filing Year:%s Number of Mentions:%s" % (self.CIK, self.filing_year, len(self.mentions))
    
    def __get_litigaton_mentions(self):
        ''' the bread and butter of this class. '''
        # first, check for LEGAL PROCEEDINGS
        mentions = self.__get_legal_proceeding_mention(self.text)
        
        if mentions is not None:
            self.mentions.append(mentions)
        
    def parse(self):
        url = self.__get_10k_url()
        
        if url is not None:
            response = urlopen(url).read()
            self.text = TextSanitizer.sanitize(HTMLTagStripper.strip(response))
            self.__get_litigaton_mentions()
        
        else:
            raise Exception("Error encountered in:" + self.__str__() + "\n" + "No URL to parse for data.")

    
    def __get_legal_proceeding_mention(self, text):
        
        def check_if_valid_hit(hit):
            ''' 
                a checker to validate whether a given piece of context could
                conceivably be a real litigation mention and not just some detritus 
                picked up by the regexes from the table of contents or something
            '''
            # check to see whether it belongs to the table of contents
            hit_is_acceptable = False
            for token in nltk.word_tokenize(hit):
                
                if re.match(LPRC.is_hit_valid(), token):
                    hit_is_acceptable = True
                    break
                
            return hit_is_acceptable
        
        results = set()
        
        for regex, anti_regex in LPRC.get_relevant_regexes():
                                                
            for hit in re.finditer(regex, text):
                
                candidate = hit.group(0) 
                
                if anti_regex is not None and re.search(anti_regex, candidate):
                    continue
                                                                                                                                    
                if not check_if_valid_hit(candidate):
                    continue
                
                # legal proceeding is always mentioned very, very close to the start of the real section
                heading = ''.join(word for word in nltk.word_tokenize(candidate)[:10])
                                                        
                # dealing with legal proceedings. so, check the first 5 lines for the phrase.
                if re.search("LEGAL", heading, re.I) and re.search("PROCEEDING", heading, re.I):
                    results.add(candidate)
                    
        if len(results) > 0:
            min_count = 0
            return_result = None
            
            for result in results:
                
                count = Utilities.get_alpha_numeric_count(result)
                
                if min_count == 0:
                    min_count = count
                    return_result = result
                
                elif count < min_count:
                    min_count = count
                    return_result = result
            
            return return_result
                
                
    def __get_10k_url(self):
        ''' 
            the SEC EDGAR website is extremely to manipulate to get a list of all the index sites for 10-K for a given company:
                 website/gunk?action=getcompany&CIK=CIK_YOU_NEED&type=10-K
            once you get the contents of that webpage, you can parse and get all the URLs. those go to index websites for each year.
            you can change the ending of the index website to get the link to the comany's full text submission - exhibits and all -
            for this year's 10-K.
        '''
        
        filing_year = self.filing_year[2:4]   # always 4 digits long.
        
        source = urlopen(self.SEC_WEBSITE + "/cgi-bin/browse-edgar?action=getcompany&CIK=" + self.CIK + "&type=10-K").read()
        
        # remove 10-K/A URLs
        source = re.sub("10-K\/A.*?</a>", " ", source, count=0, flags=re.M | re.I | re.S)
        soup = BeautifulSoup(source, "html.parser")
            
    
        for link in soup.find_all('a', href=re.compile("/Archives/.*\-" + filing_year + "\-.*\-index\.html?$")):
            url = link['href']
            url = re.sub("\-index\.html?$", ".txt", url, re.I)       # replace the last portion with ".txt" for the full 10-K filing.
            return self.SEC_WEBSITE + url
        
    @staticmethod
    def __sanitize_filing_year(year):
        year = str(year)
        if len(year) == 2:
            if year < '50':
                year = '19' + year
            else:
                year = '20' + year
        
        if len(year) == 1:
            year = '200' + year
             
        return year
    
    def write_to_corpus(self):
        ''' 
        we'll dump our resulting data to a text file.
        it will be structured thusly:
           corpus
                CIK_1
                    filing_year_1.txt
                    filing_year_2.txt
        and so on. 
        '''
        
        if len(self.mentions) == 0:
            raise Exception("Nothing to write!")
        
        CIK = self.CIK
                
        # this is normally 10 digits. make it 10 for consistent directory grammar
        while len(CIK) < Constants.CIK_CODE_LENGTH: 
            CIK = '0' + CIK
        
        path = os.path.join(Constants.PATH_TO_CORPUS, CIK)
        
        if not os.path.exists(path):
            os.makedirs(path)
        
        with open(path + "/" + self.filing_year + ".txt", 'w') as f:
            f.writelines(self.mentions)
