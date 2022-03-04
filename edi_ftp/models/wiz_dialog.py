# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError


class Wizard_dialog(models.TransientModel):
    _name = "wiz.dialog"
    _description = "Wizard for dialog"
    
    confirm_message = fields.Text(string="Information")
    code_message = fields.Text(string="Code Message")
    id_edi = fields.Text(string="ID EDI")
    filename_edi = fields.Text(string="File name EDI")
        
#    @api.multi
    def wiz_write_file_invoice(self):
        action = {
                    'name': 'miadi_invoice_edi',
                    'type': 'ir.actions.act_url',
                    'url': "web/content/?model=wiz.edi.ftp&id=" + str(self.id_edi) + "&filename_field=filename&field=edi_data&download=true&filename=" + self.filename_edi,
                    'target': 'self',
                    
                    }
        return action 
    
    def wiz_write_file_sale(self):
        action = {
                    'name': 'miadi_sale_edi',
                    'type': 'ir.actions.act_url',
                    'url': "web/content/?model=wiz.edi.ftp&id=" + str(self.id_edi) + "&filename_field=filename&field=edi_data&download=true&filename=" + self.filename_edi,
                    'target': 'self',
                    
                    }
        return action 
    
    def show_dialog(self, mess="FTP", codemess="file-invoice", idedi =0, fileedi=""):
        return {
            'name':'Export EDI file',            
            'code_message': codemess,
            'id_edi': idedi , 
            'filename_edi': fileedi, 
            'context':{'default_confirm_message': mess, 
                            'default_code_message': codemess,
                            'default_id_edi':idedi,
                            'default_filename_edi':fileedi },
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wiz.dialog',
            'target':'new' 
        }    
        