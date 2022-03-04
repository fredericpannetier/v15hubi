# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MIADI_EtiquetteModel(models.Model):
    _name = "di.printing.etiqmodel"
    _description = "Etiquette model"
    _order = "name"
    
    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    #di_file = fields.Char(sting="Path File", required=False, help="Path of the etiquette file")
    text_etiq = fields.Text(string="Etiquette text", required=False, help="Paste here copy of etiquette text")
    commentary = fields.Text(string="Comment")
    with_ean128 = fields.Boolean(string='Label with EAN128', default=False)
    langage_print = fields.Selection([("ZPL", "ZPL"), ("EPL", "EPL"),
                              ("Toshiba", "Toshiba")], string="Langage Printing")
   
    _sql_constraints = [("uniq_id","unique(code)","A etiquette model already exists with this code. It must be unique !"),]