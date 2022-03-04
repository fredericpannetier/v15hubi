
# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError
from odoo.exceptions import Warning


class DiWizPopup(models.TransientModel):
    _name = "di.wiz.popup"
    _description = "Popup show"
    
    name = fields.Char('Message')    
    button_ok = fields.Boolean(default=True)
    button_yes = fields.Boolean(default=False)
    button_no = fields.Boolean(default=False)
    button_cancel = fields.Boolean(default=False)
    
    
    def yes(self):
        return "yes"
        
    def no(self):
        return "no"
    
    
    
    def show_message(self,mess="End",button_ok=True,button_yes=False,button_no=False,button_cancel=False):
        return {
            'name':mess,            
            'button_ok':button_ok,
            'button_yes':button_yes,
            'button_no':button_no,
            'button_cancel':button_cancel,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'di.wiz.popup',
            'target':'new' 
        }