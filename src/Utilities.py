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

def count_parentheses(data):
    left_parens = 0
    right_parens = 0
    for char in data:
        if char == '(':
            left_parens += 1
        elif char == ')':
            right_parens += 1
            
    return left_parens, right_parens