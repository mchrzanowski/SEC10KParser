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


def contains_numbers(s):

    for char in s:
        if char.isdigit():
            return True
    return False


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


def sanitize_filing_year(year):
    year = str(year)
    if len(year) == 2:
        if year < '50':
            year = '19' + year
        else:
            year = '20' + year
    if len(year) == 1:
        year = '200' + year

    return year


def is_CIK_valid(CIK):
    ''' check whether the CIK value is valid '''
    if len(CIK) == 0:
        return False
    if int(CIK) == 0:
        return False

    return True
