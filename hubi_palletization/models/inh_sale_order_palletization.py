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
     
    def _get_query_create_pallet_sale(self):
        return """SELECT  order_id, sale_order_line.product_id, di_paltyp_id, 
                coalesce(pack_num,0) AS default_pallet_qty,
                sum(product_uom_qty)  AS uom_qty,
                sale_order_line.di_no_lot  AS batch_number,
                sale_order_line.id AS line_id  
                FROM sale_order_line 
                inner join sale_order on sale_order_line.order_id = sale_order.id
                inner join product_product on product_id = product_product.id
                inner join product_template on product_template.id = product_product.product_tmpl_id
                left join di_pallet_product on di_pallet_product.pallet_type_id = di_paltyp_id 
                    and di_pallet_product.product_id = sale_order_line.product_id
                where order_id = %(id_order)s  and sale_order_line.company_id=%(company_code)s 
                group by order_id, sale_order_line.product_id, di_paltyp_id, 
                coalesce(pack_num,0),sale_order_line.id
                order by order_id, sale_order_line.product_id"""
                   
    def create_pallet_sale(self):        
        res = super(HubiSaleOrderPal, self).create_pallet_sale()
        company_code = self.env['sale.order'].search([('id', '=', self.id)]).company_id.id
        id_order = self.id
        batch_number =""
        date_limit = ""
        
        palletization_ids = self.env['di.palletization'].search([('order_id', '=', id_order),  ('company_id', '=', company_code)])
        for pallets in palletization_ids:
            lines = self.env['sale.order.line'].search([('order_id', '=', id_order), ('product_id', '=', pallets.product_id.id),  ('company_id', '=', company_code)])
            for line in lines:
                batch_number = lines.di_no_lot or ""
                date_limit = lines.di_date_dluo or ""
                
            pallets.update({
                            'batch_number': batch_number,
                            'date_limit': date_limit,
                        })
   
   
    def create_print_etiquet_pallet(self, id_order= False):        
        id_order = self.id
        res = super(HubiSaleOrderPal, self).create_print_etiquet_pallet(id_order)
        company_code = self.env['sale.order'].search([('id', '=', self.id)]).company_id.id
        
        etab_exp_no = self.partner_id.di_sender_establishment.id or ""
        sending_date = ""
        packaging_date = ""
        if self.di_sending_date:
           sending_date = fields.Date.from_string(self.di_sending_date).strftime('%d/%m/%Y')
        if self.di_packaging_date:    
           packaging_date = fields.Date.from_string(self.di_packaging_date).strftime('%d/%m/%Y')
                
        palletization_ids = self.env['wiz.print.pallet'].search([('sale_order_id', '=', id_order),  ('company_id', '=', company_code)])
        for pallets in palletization_ids:
            pallets.update({
                'etab_exped_id' : etab_exp_no or "",
                'sending_date' : sending_date or "",
                'packaging_date' : packaging_date or "",          
                        })

class HubiSaleOrderPalletization(models.Model):
    _inherit = "di.palletization"
    
    def calc_new_pallet(self, cnuf=False, order_id=False, no_pallet=False, supp=False):
        cnuf_p = self.env['sale.order'].search([('id', '=', order_id)]).partner_id.di_sender_establishment.di_cnuf or ""
        if cnuf_p != "":
            cnuf = cnuf_p
        
        res = super(HubiSaleOrderPalletization, self).calc_new_pallet(cnuf, order_id, no_pallet, supp)
        return res
