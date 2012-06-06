'''
Created on Jun 6, 2012

@author: polak
'''

import re

if __name__ == '__main__':
    with open("/Users/polak/omg") as f:
        x = ''.join(line for line in f)
                
        y = re.findall("^\s*Item.*number.*Legal.*\n^\s*Item.*number", x, re.M | re.I | re.S)
        
        for num, lol in enumerate(y):
            print num, lol
                
        