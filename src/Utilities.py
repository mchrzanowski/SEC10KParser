'''
Created on Jun 8, 2012

@author: mchrzanowski
'''

def get_alpha_numeric_count(text):
    count = 0
    for char in text:
        if char.isalpha() or char.isdigit():
            count += 1
    
    return count  

 
