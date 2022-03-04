# -*- coding: utf-8 -*-
from odoo import api, fields, models, modules

class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']
    
    di_calcul_lot = fields.Selection([('M', 'Manual'), ('AAAAMMJJ', 'Auto AAAAMMJJ'), ('AAMMJJ', 'Auto AAMMJJ'), ('AAAAQ', 'Auto AAAAQQQ'), ('AAQ', 'Auto AAQQQ'), ('JJ/MM/AAAA', 'Auto JJ/MM/AAAA'), ('JJ/MM/AA', 'Auto JJ/MM/AA')], string="Batch Number Calculation", default='M')  
    di_calcul_lot_date = fields.Selection([('Sale', 'Sale Order Date'), ('Send', 'Send Date'),('Packaging', 'Packaging Date')   ], string="Batch Number on this date", default='Sale')  
    di_default_establishment = fields.Many2one('res.partner', string='Sender establishment',  domain=[('di_is_establishment', '=', True)],
                                               config_parameter='hubi.di_default_establishment')


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            di_calcul_lot = self.env['ir.config_parameter'].sudo().get_param('hubi.di_calcul_lot'),
            di_calcul_lot_date = self.env['ir.config_parameter'].sudo().get_param('hubi.di_calcul_lot_date'),
            #di_default_establishment = self.env['ir.config_parameter'].sudo().get_param('hubi.di_default_establishment'),
        )
        return res

    #@api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        _calcul_lot = self.di_calcul_lot and self.di_calcul_lot or False
        _calcul_lot_date = self.di_calcul_lot_date or False
        _default_establishment = self.di_default_establishment or False
        
        param.set_param('hubi.di_calcul_lot', _calcul_lot)
        param.set_param('hubi.di_calcul_lot_date', _calcul_lot_date)
        #param.set_param('hubi.di_default_establishment', _default_establishment)
              