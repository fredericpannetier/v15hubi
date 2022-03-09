# -*- coding: utf-8 -*-

from odoo import models, fields, api

def replace_accent(self,s):
    if s:
        s = s.replace('ê', 'e') \
             .replace('è', 'e') \
             .replace('é', 'e') \
             .replace('à', 'a') \
             .replace('â', 'a') \
             .replace('á', 'a') \
             .replace('ô', 'o') \
             .replace('ö', 'o') \
             .replace('î', 'i') \
             .replace('É', 'E') \
             .replace('È', 'E') \
             .replace('Ê', 'E') \
             .replace('À', 'A') \
             .replace('Â', 'A') \
             .replace('Á', 'A') \
             .replace('Ô', 'O') \
             .replace('Ö', 'O') \
             .replace('Î', 'I')
    return s                 

def replace_car(self,s):
    if s:
        s = s.replace('/', '') \
             .replace('-', '') \
             .replace('+', '') \
             .replace('.', '') \
             .replace(' ', '') \
             .replace('&', '') \
             .replace('_', '')
    return s  
                      
def left(aString, howMany):
    if howMany <1:
        return ''
    else:
        return aString[:howMany]

def right(aString, howMany):
    if howMany <1:
        return ''
    else:
        return aString[-howMany:]

def mid(aString, startChar, howMany):
    if howMany < 1:
        return ''
    else:
        return aString[startChar:startChar+howMany]
 