'''
Created on Jun 8, 2012

@author: mchrzanowski
'''
import Constants

def get_alpha_numeric_count(text):
    count = 0
    for char in text:
        if char.isalpha() or char.isdigit():
            count += 1
    
    return count  

 
def format_CIK(data):
    data = str(data)
    while len(data) < Constants.CIK_CODE_LENGTH:
        data = '0' + data

    return data

def character_counter(data, *chars):
    
    results = dict()  
    
    for char_arg in chars:
        results[char_arg] = 0
    
    for char in data:
       for index, char_arg in enumerate(chars):
           if char == char_arg:
               results[char_arg] += 1
            
    return results