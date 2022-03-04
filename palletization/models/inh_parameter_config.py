# -*- coding: utf-8 -*-
from odoo import api, fields, models, modules, _

class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']
    
    di_pallet_type_1 = fields.Char(string="Pallet Type 1")
    di_pallet_type_2 = fields.Char(string="Pallet Type 2")
    di_pallet_type_3 = fields.Char(string="Pallet Type 3")
    
    di_pallet_type_default_id = fields.Many2one('di.pallet.type', 
                                             string='Default pallet type', 
                                             config_parameter='palettization.di_pallet_type_default_id')
                                      
    di_etiq_pallet_printer_id = fields.Many2one('di.printing.printer', 
                                             string='Printer For Pallet Etiquette', 
                                             domain=[('isimpetiq', '=', True)],
                                             config_parameter='palettization.di_etiq_pallet_printer_id')
    di_etiq_pallet_model_id =  fields.Many2one('di.printing.etiqmodel', 
                                            string='Etiquette model For Pallet Etiquette',
                                            config_parameter='palettization.di_etiq_pallet_model_id')
 

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            di_pallet_type_1 = self.env['ir.config_parameter'].sudo().get_param('palettization.di_pallet_type_1'),
            di_pallet_type_2 = self.env['ir.config_parameter'].sudo().get_param('palettization.di_pallet_type_2'),
            di_pallet_type_3 = self.env['ir.config_parameter'].sudo().get_param('palettization.di_pallet_type_3'),
            #di_etiq_pallet_printer = self.env['ir.config_parameter'].sudo().get_param('palettization.default_etiq_pallet_printer_id'),
            #di_etiq_pallet_model = self.env['ir.config_parameter'].sudo().get_param('palettization.di_etiq_pallet_model'),
        )
        return res

    #@api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        _pallet_type_1 = self.di_pallet_type_1 and self.di_pallet_type_1 or False
        _pallet_type_2 = self.di_pallet_type_2 and self.di_pallet_type_2 or False
        _pallet_type_3 = self.di_pallet_type_3 and self.di_pallet_type_3 or False
        
        _etiq_pallet_printer = self.di_etiq_pallet_printer_id and self.di_etiq_pallet_printer_id or False
        _etiq_pallet_model = self.di_etiq_pallet_model_id and self.di_etiq_pallet_model_id or False
        
        param.set_param('palettization.di_pallet_type_1', _pallet_type_1)
        param.set_param('palettization.di_pallet_type_2', _pallet_type_2)
        param.set_param('palettization.di_pallet_type_3', _pallet_type_3)
        #param.set_param('palettization.default_etiq_pallet_printer_id', _etiq_pallet_printer)
        
        #param.set_param('palettization.di_etiq_pallet_printer', _etiq_pallet_printer)
        #param.set_param('palettization.di_etiq_pallet_model', _etiq_pallet_model)
        
    def open_type_pallet(self):
        self.ensure_one()
        try:
            pallet_type_form_id = self.env['ir.model.data'].get_object_reference('palletization', 'view_pallet_type_form')[1]
            
        except ValueError:
            pallet_type_form_id = False
        
        try:
            pallet_type_tree_id = self.env['ir.model.data'].get_object_reference('palletization', 'view_pallet_type_tree')[1]
            
        except ValueError:
            pallet_type_tree_id = False    
        
        return {
            'name': _('Type Pallet'),
            'view_mode': 'tree,form',
            #'views': [(self.env.ref('palletization.view_pallet_type_tree').id, 'tree'), (False, 'form')],
            #'views': [('view_pallet_type_tree', 'tree'), ('view_pallet_type_form', 'form')],
            #'view_id': 'view_pallet_type_form',
            'views': [(pallet_type_tree_id, 'tree'), (pallet_type_form_id, 'form')],
            'view_id': pallet_type_form_id,
            'res_model': 'di.pallet.type',
            'type': 'ir.actions.act_window',
            'target': 'current',
            
        }    
              