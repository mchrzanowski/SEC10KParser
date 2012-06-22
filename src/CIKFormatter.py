'''
Created on Jun 22, 2012

@author: mchrzanowski
'''

import Constants

def format_CIK(data):
    data = str(data)
    while len(data) < Constants.CIK_CODE_LENGTH:
        data = '0' + data

    return data