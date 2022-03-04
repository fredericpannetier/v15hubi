# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MIADI_EtiquetteParameter(models.Model):
    _name = "di.printing.parameter"
    _description = "Parameters"
    _order = "name"
    
    name = fields.Char(string="Name", required=True)
    value = fields.Char(string="Value", required=True)
    etiquette_model_id =  fields.Many2one('di.printing.etiqmodel', string='Etiquette model')
    printer_id =  fields.Many2one('di.printing.printer', string='Printer')
    
    