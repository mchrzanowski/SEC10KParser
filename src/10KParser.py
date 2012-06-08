'''
Created on Jun 3, 2012

@author: mchrzanowski
'''


import os.path
import re

from bs4 import BeautifulSoup

from time import time
from urllib2 import urlopen

from HTMLTagStripper import HTMLTagStripper
from TextSanitizer import TextSanitizer
import LegalProceedingRegexCollection as LPRC
    
def main():
    
    CIK = '0000731939'
    
    for i in xrange(2012, 2012 + 1):
        
        filing_year = str(i)
        
        print "Begin:\tCIK:%s\t%s" % (CIK, filing_year)
        
        try:
            l = Litigation10KParser(CIK, filing_year)
            l.parse()
            l.write_to_file()
        except Exception as exception:
            print exception

class Litigation10KParser(object):
    
    SEC_WEBSITE = "http://www.sec.gov/"
    
    def __init__(self, CIK, filing_year):
        self.CIK = CIK
        self.filing_year = self.sanitize_filing_year(filing_year)
        self.mentions = []
    
    def __str__(self):
        return "Litigation10KParser object. CIK:%s Filing Year:%s Number of Mentions:%s" % (self.CIK, self.filing_year, len(self.mentions))
    
    def get_litigaton_mentions(self, text):
        ''' the bread and butter of this class. '''
        # first, check for LEGAL PROCEEDINGS
        self.mentions.append(self.get_legal_proceeding_mention(text))
    
    def parse(self):
        url = self.get_10k_url(self)
        if url is not None:
            response = urlopen(url).read()
            response = TextSanitizer.sanitize(HTMLTagStripper.strip(response))
            self.get_litigaton_mentions(response)
        
        else:
            raise Exception("ERROR:\n" + self.__str__() + "\n" + "No URL to parse for data.")

    
    def get_legal_proceeding_mention(self, text):
        
        def check_if_valid_hit(hit):
            ''' a checker to validate whether a given piece of context could
            conceivably be a real litigation mention and not just some detritus 
            picked up by the regexes '''
            
            # check to see whether it belongs to the table of contents
            hit = re.sub("\s+", "", hit)
            if len(hit) < 100: return False
            return True
        
        for regex in (LPRC.default(), LPRC.try_all_numbers_after_4()):
        
            hits = re.finditer(regex, text, re.M | re.I | re.S)
            
            for hit in hits:
                                        
                if not check_if_valid_hit(hit.group(0)):
                    continue
                
                # legal proceeding is always mentioned very, very close to the start of the real section
                heading = ''.join(group for group in hit.group(0))[:200]
                                        
                # dealing with legal proceedings. so, check the first 5 lines for the phrase.
                if re.search("Legal\s+?Proceeding", heading, re.I | re.M):
                    return hit.group(0) 
                
    @classmethod
    def get_10k_url(cls, parser):
        ''' 
            the SEC EDGAR website is extremely to manipulate to get a list of all the index sites for 10-K for a given company:
                 website/gunk?action=getcompany&CIK=CIK_YOU_NEED&type=10-K
            once you get the contents of that webpage, you can parse and get all the URLs. those go to index websites for each year.
            you can change the ending of the index website to get the link to the comany's full text submission - exhibits and all -
            for this year's 10-K.
        '''
        
        filing_year = parser.filing_year[2:4]   # always 4 digits long.
        
        source = urlopen(cls.SEC_WEBSITE + "/cgi-bin/browse-edgar?action=getcompany&CIK=" + parser.CIK + "&type=10-K").read()
        
        # remove 10-K/A URLs
        source = re.sub("10-K\/A.*?</a>", " ", source, count=0, flags=re.M | re.I | re.S)
        soup = BeautifulSoup(source, "html.parser")
            
    
        for link in soup.find_all('a', href=re.compile("/Archives/.*\-" + filing_year + "\-.*\-index\.html?$")):
            url = link['href']
            url = re.sub("\-index\.html?$", ".txt", url, re.I)       # replace the last portion with ".txt" for the full 10-K filing.
            return cls.SEC_WEBSITE + url
        
    @classmethod
    def sanitize_filing_year(cls, year):
        year = str(year)
        if len(year) == 2:
            if year < '50':
                year = '19' + year
            else:
                year = '20' + year
        
        if len(year) == 1:
            year = '200' + year
             
        return year
    
    def write_to_file(self):
        ''' 
        we'll dump our resulting data to a text file.
        it will be structured thusly:
           corpus
                CIK_1
                    filing_year_1.txt
                    filing_year_2.txt
        and so on. 
        '''
        
        CIK = self.CIK
                
        # this is normally 10 digits. make it 10 for consistent directory grammar
        while len(CIK) < 10: 
            CIK = '0' + CIK
        
        path = "./corpus/" + CIK
        
        if not os.path.exists(path):
            os.makedirs(path)
        
        with open(path + "/" + self.filing_year + ".txt", 'w') as f:
            for mention in self.mentions:
                f.write(mention)


if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print "Runtime:%r seconds" % (end - start)
