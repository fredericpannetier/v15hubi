# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MIADI_Tools(models.Model):
    _name = "di.tools"
    _description = "Tools"
    
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
             .replace('ï', 'i') \
             .replace('É', 'E') \
             .replace('È', 'E') \
             .replace('Ê', 'E') \
             .replace('À', 'A') \
             .replace('Â', 'A') \
             .replace('Á', 'A') \
             .replace('Ô', 'O') \
             .replace('Ö', 'O') \
             .replace('Î', 'I') \
             .replace('Ï', 'I')
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
                      
    def left(self, aString, howMany):
        if howMany <1:
            return ''
        else:
            return aString[:howMany]

    def right(self, aString, howMany):
        if howMany <1:
            return ''
        else:
            return aString[-howMany:]

    def mid(self, aString, startChar, howMany):
        if howMany < 1:
            return ''
        else:
            return aString[startChar:startChar+howMany]
 
    def calcul_cle_code_ean13(self, ean):
        # Calcul cle code ean13
        somme = 0
        coeff = "131313131313"

        for i in range(0,12):
            somme = somme + int(ean[i])*int(coeff[i])

        reste = somme % 10
        if reste == 0:
            cle = 0
        else: 
            cle = 10 - reste
        
        return "%s" % (cle) 