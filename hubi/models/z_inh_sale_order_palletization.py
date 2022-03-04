# -*- coding: utf-8 -*-
from odoo import models, fields, api, _,  SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import date, timedelta, datetime   
from itertools import groupby
import base64


class HubiSaleOrderPal(models.Model):
    _inherit = "sale.order"

    def action2_palletization2(self):
        action = self.env.ref('hubi.action_hubi_palletization').read()[0]
        action['views'] = [(self.env.ref('hubi.hubi_palletization_form').id, 'form')]
        action['res_id'] = self.id

        return action
        #return {'type': 'ir.actions.act_window_close'} 
       
    def create_pallet_sale(self):        
        res = super(HubiSaleOrderPal, self).create_pallet_sale()
        company_code = self.env['sale.order'].search([('id', '=', self.id)]).company_id.id
        id_order = self.id
        
        palletization_ids = self.env['di.palletization'].search([('order_id', '=', id_order),  ('company_id', '=', company_code)])
        for pallets in palletization_ids:
            lines = self.env['sale.order.line'].search([('order_id', '=', id_order), ('product_id', '=', pallets.product_id.id),  ('company_id', '=', company_code)])
            for line in lines:
                batch_number = lines.di_no_lot
                date_limit = lines.di_date_dluo
                
            pallets.update({
                            'batch_number': batch_number,
                            'date_limit': date_limit,
                    
                        })
   
   
    def create_print_etiquet_pallet(self, id_order= False):        
        id_order = self.id
        res = super(HubiSaleOrderPal, self).create_print_etiquet_pallet(id_order)
        company_code = self.env['sale.order'].search([('id', '=', self.id)]).company_id.id
        
        etab_exp_no = self.partner_id.di_sender_establishment.id
        sending_date = ""
        packaging_date = ""
        if self.di_sending_date:
           sending_date = fields.Date.from_string(self.di_sending_date).strftime('%d/%m/%Y')
        if self.di_packaging_date:    
           packaging_date = fields.Date.from_string(self.di_packaging_date).strftime('%d/%m/%Y')
                
        palletization_ids = self.env['wiz.print.pallet'].search([('sale_order_id', '=', id_order),  ('company_id', '=', company_code)])
        for pallets in palletization_ids:
            
                
            pallets.update({
                'etab_exped_id' : etab_exp_no,
                'sending_date' : sending_date,
                'packaging_date' : packaging_date,          
                        })

class HubiSaleOrderPalletization(models.Model):
    _inherit = "di.palletization"
    
    def calc_new_pallet(self, cnuf=False, order_id=False, no_pallet=False, supp=False):
        cnuf_p = self.env['sale.order'].search([('id', '=', order_id)]).partner_id.di_sender_establishment.di_cnuf or ""
        if cnuf_p != "":
            cnuf = cnuf_p
        
        res = super(HubiSaleOrderPalletization, self).calc_new_pallet(cnuf, order_id, no_pallet, supp)
        return res
