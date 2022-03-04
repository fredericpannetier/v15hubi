# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
#from . import tools_hubi

import logging

_logger = logging.getLogger(__name__)

class DiPalletization(models.Model):
    _name = 'di.palletization'
    _description = "Palletization"
    _order = 'name'
 
    def _get_qty(self):
        return (self.uom_qty or 0) - (self.pallet_qty  or 0)
    
    def _get_default_company_id(self):
        #return self._context.get('force_company', self.env.user.company_id.id)
        return self.env['sale.order'].search([('id', '=', self.order_id.id)]).company_id.id
   
   
    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=_get_default_company_id, required=True)
    order_id = fields.Many2one('sale.order', string='Order Reference', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    default_pallet_qty = fields.Float(string='Default Quantity on the Pallet')
    uom_qty = fields.Float(string='Order Quantity')
    pallet_qty = fields.Float(string='Quantity on the Pallet')
    residual_qty = fields.Float(string='Residual Quantity', compute='_residual_qty')
    input_pallet_id = fields.Many2one('di.palletization.line', string='Complete No Pallet')
    line_id = fields.Integer("Line id")
    #input_pallet_id = fields.Many2one('di.palletization.line', string='Complete No Pallet', domain="[('order_id', '=', order_id)]")
    
    input_qty = fields.Float(string='Complete Quantity', default=_get_qty)
    batch_number = fields.Char(string='Batch number')
    date_limit = fields.Date(string='Date limit')
    #Modif SC 01/04/2021, ajout du type de palette à la ligne                                                                  
    paltyp_id = fields.Many2one('di.pallet.type', string='Pallet type', help="Type of the pallet for the line")
  
#    @api.one
#     def _default_qty(self):
#         for line in self:
#             line.default_pallet_qty = line.product_id.di_default_pallet_qty_1
 
 
    @api.onchange('paltyp_id')
    def onchange_paltyp_id(self):
        pack_num = self.env['di.pallet.product'].search([ ('pallet_type_id', '=', self.paltyp_id.id), ('company_id', '=', self.company_id.id), ('product_id', '=', self.product_id.id) ]).pack_num
#         self.default_pallet_qty = pack_num
        self.update({'default_pallet_qty': pack_num})
        self.env.cr.commit()
        
        
#    @api.one
    def _residual_qty(self):
        for line in self:
            line.residual_qty = (line.uom_qty or 0) - (line.pallet_qty  or 0)

    def new_pallet(self):
        self.env.cr.commit() 
        
        #company_code = self.env['sale.order'].search([('id', '=', self.id)]).company_id.id or self._context.get('company_id') or self.env['res.users']._get_company().id
        company_code = self.env['sale.order'].search([('id', '=', self.order_id.id)]).company_id.id
        cnuf = self.order_id.company_id.di_cnuf or ""
        id_order = self.order_id.id
        
        max_qty = self.default_pallet_qty
        if self.residual_qty != 0 and max_qty > 0:
            # Find the last pallet
            no_pallet = ""
            query_args = {'id_order' : id_order, 'company_code' : company_code}
            query = """SELECT pallet_no FROM di_palletization_line 
                    WHERE order_id=%(id_order)s and company_id=%(company_code)s 
                    order by pallet_no desc LIMIT 1"""

            self.env.cr.execute(query, query_args)
            ids = [(r[0]) for r in self.env.cr.fetchall()]
            
            for last_no in ids:
                no_pallet=last_no
            
            reste = self.residual_qty
            qty_a_pl= self.residual_qty
            new_qty_pallet = self.pallet_qty + self.residual_qty
     
#             palletization_line_ids = self.env['di.palletization.line'].search([('palletization_id', '=', self.id), ('company_id', '=', company_code)])
            palletization_line_ids = self.env['di.palletization.line'].search([('palletization_id', '=', self.id), ('company_id', '=', company_code), ('paltyp_id', '=', self.paltyp_id.id)])
            if (not palletization_line_ids) or (qty_a_pl != 0):
                qty = 0
 
                if max_qty > 0:
                    while qty_a_pl !=0:
                        if qty_a_pl >= max_qty:
                            qty = max_qty
                            reste = qty_a_pl - max_qty
                        else:
                            qty = qty_a_pl
                            reste = 0
                
                        qty_a_pl = reste
                        new_no_pallet = self.calc_new_pallet(cnuf, self.order_id.id, no_pallet, False)
                    
                        # Create palletization line
                        # 'company_id': self._context.get('force_company', self.env.user.company_id.id),
                        p_weight = self.product_id.get_pack_weight() or 0
                        p_batch_number = self.batch_number or False
                        p_date_limit = self.date_limit or False
                        name_line = ('Order : %s / Pallet : %s') % (self.order_id.name,new_no_pallet)
                        pallet_line_vals = {
                            'name': name_line,
                            'company_id': company_code,
                            'palletization_id':self.id,
                            'order_id': self.order_id.id,
                            'product_id': self.product_id.id,
                            'quantity': qty,
                            'weight': qty * p_weight,
                            'pallet_no': new_no_pallet,
                            'batch_number': p_batch_number,
                            'date_limit': p_date_limit,
                            'paltyp_id': self.paltyp_id.id,
                            
                            }
                        self.env['di.palletization.line'].create(pallet_line_vals)  
                        no_pallet = new_no_pallet
                        
                    # Update pallet_qty on di_palletization
                    #self._cr.execute("UPDATE di_palletization set pallet_qty = %s, input_qty = %s WHERE id=%s ", (new_qty_pallet, reste, self.id))
                    #self.env.cr.commit()
                    self.update({
                        'pallet_qty': new_qty_pallet,
                        'input_qty': reste,
                        
                        })
        
            self.compute_pallet(self.order_id.id)
            
            
    def complete_pallet(self):
        self.env.cr.commit() 
        if self.input_pallet_id == False or len(self.input_pallet_id) == 0:
            raise UserError(_("You must select a pallet."))
            return
            #title = ("Warning")
            #message = 'Error. Select a pallet.'
            #warning = {
            #        'title': title,
            #        'message': message, }
            #return {'warning': warning}
        
        #company_code = self.env['sale.order'].search([('id', '=', self.id)]).company_id.id or self._context.get('company_id') or self.env['res.users']._get_company().id
        company_code = self.env['sale.order'].search([('id', '=', self.order_id.id)]).company_id.id
        id_order = self.order_id.id
        
        max_qty = self.default_pallet_qty
        no_pallet = self.input_pallet_id.pallet_no
        no_product = self.product_id.id
        p_weight = self.product_id.get_pack_weight() or 0
        p_batch_number = self.batch_number or False
        p_date_limit = self.date_limit or False
        paltyp_id = self.paltyp_id.id
        
        if self.input_qty != 0 and self.input_pallet_id != 0 and self.residual_qty != 0 and max_qty > 0:
            if self.input_qty > self.residual_qty:
                qty_a_pl = self.residual_qty
            else:    
                qty_a_pl = self.input_qty 
            
            new_qty_pallet = self.pallet_qty + qty_a_pl  
            reste = self.residual_qty - qty_a_pl
            
            # Update pallet_qty on di_palletization
            #self._cr.execute("UPDATE di_palletization set pallet_qty = %s, input_qty = %s, input_pallet_id= null WHERE id=%s ", (new_qty_pallet, reste, self.id))
            self.update({
                'pallet_qty': new_qty_pallet,
                'input_qty': reste,
                'input_pallet_id': False,
            })
            
            # Find the line in di_palletization_line for this pallet_id and this product_id
            palletization_line_ids = self.env['di.palletization.line'].search([('palletization_id', '=', self.id), ('pallet_no', '=', no_pallet), ('product_id', '=', no_product),('batch_number', '=', p_batch_number), ('company_id', '=', company_code) ])
            if (not palletization_line_ids):
                # Create palletization line
                name_line = ('Order : %s / Pallet : %s') % (self.order_id.name, no_pallet)
                pallet_line_vals = {
                    'name': name_line,
                    'company_id': company_code,
                    'palletization_id':self.id,
                    'order_id': self.order_id.id,
                    'product_id': no_product,
                    'quantity': qty_a_pl,
                    'weight': qty_a_pl * p_weight,
                    'pallet_no': no_pallet,
                    'batch_number': p_batch_number,
                    'date_limit': p_date_limit,
                    'paltyp_id':paltyp_id,
                    }
                self.env['di.palletization.line'].create(pallet_line_vals)  
            else:
                # Update quantity on di_palletization_line
                new_qty = palletization_line_ids.quantity + qty_a_pl
                new_weight = new_qty * p_weight  
                #self._cr.execute("UPDATE di_palletization_line set quantity = %s WHERE palletization_id=%s and pallet_no=%s and product_id=%s  and company_id=%s  ", 
                #                 (new_qty, self.id, no_pallet, no_product, company_code))
                for pallets in palletization_line_ids:
                        pallets.update({
                            'quantity': new_qty,
                            'weight' : new_weight,
                        })


            #self.env.cr.commit() 
            
        self.compute_pallet(self.order_id.id)    

    def delete_all_pallet(self):
        self.env.cr.commit() 
        company_code = self.env['sale.order'].search([('id', '=', self.order_id.id)]).company_id.id
        id_order = self.order_id.id
        palletization_line_ids = self.env['di.palletization.line'].search([('palletization_id', '=', self.id), ('company_id', '=', company_code)])
        if (palletization_line_ids) :
            #self.env['di.palletization.line'].search([('palletization_id', '=', self.id), ('company_id', '=', company_code)]).unlink
            msg = _('For this line, you must delete all the pallet lines before')
            raise UserError(_('Delete Line !\n' + msg))
        else:   
            self.env['di.palletization'].search([('id', '=', self.id)]).unlink()
            
    def write(self, vals):
        result = super(DiPalletization, self).write(vals)
        """
        if vals.get('palletization_line_ids'):
            pallet_count = len(order_line.palletization_line_ids)
            
            saleorder = self.env['sale.order'].search([('id', '=', self.order_id.id)])
            saleorder.write({'di_pallet_number':pallet_count})
        """    
        return result  
              
    def compute_pallet(self, numorder):
        saleorder = self.env['sale.order'].browse(numorder)
        pallet_count = 0
        if saleorder.palletization_line_ids:
            pallet_count = len(saleorder.palletization_line_ids)
        saleorder.update({
                'di_pallet_number': pallet_count
            })
         
    def calc_new_pallet(self, cnuf=False, order_id=False, no_pallet=False, supp=False):
        #cnuf = company_id.di_cnuf
        cnuf = str(cnuf)
        no_pallet=str(no_pallet)
        if no_pallet != "":
            no_pallet = no_pallet[14:17]
            
        order_id = str(order_id)
        if supp:
            if no_pallet !="001":           
                num_pallet =  int(no_pallet) - 1
            else:
                num_pallet =1   
        else:    
            if no_pallet != "":
                num_pallet = int(no_pallet[-3:]) + 1
            else:
                num_pallet = 1
            
        #num_pallet =  int(der_no_pallet) + 1  
        
        lg = 17-(len(cnuf) + 3)
        order_id = order_id.zfill(lg)
        
        new_no_pallet = cnuf
        new_no_pallet+= order_id
        new_no_pallet+= "{:03.0f}".format(num_pallet)
        
        # Calcul Clé
        result=0
        t=1
        num = new_no_pallet
        
        for i in num:
            if t%2==1:
                result += 3*int(i)
            else:
                result += int(i)
            t += 1
 
        if result%10==0:
            rest=0
        else:
            rest=10 -result%10 
            
        new_no_pallet+= "{:01.0f}".format(rest)      
        return new_no_pallet
             
class DiPalletizationLine(models.Model):
    _name = "di.palletization.line"
    _description = "Palletization Line"
    _order = 'name'
     
    def _get_default_company_id(self):
        #return self.env['sale.order'].search([('id', '=', self.id)]).company_id.id or self._context.get('force_company', self.env.user.company_id.id)
        return self.env['sale.order'].search([('id', '=', self.order_id.id)]).company_id.id
   
    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=_get_default_company_id, required=True)
    palletization_id = fields.Many2one('di.palletization', string='Palletization Reference', required=True)
    #order_id = fields.Char(string='sale.order')
    order_id = fields.Many2one('sale.order', string='Order Reference', required=True)
    #pallet_no = fields.Float(string='Pallet Number', digits=(20,0))
    pallet_no = fields.Char(string='Pallet Number')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity of the product')
    weight = fields.Float(string='Weight of the product')
    batch_number = fields.Char(string='Batch number')
    date_limit = fields.Date(string='Date limit')
    #Modif SC 01/04/2021, ajout du type de palette à la ligne                                                                  
    paltyp_id = fields.Many2one('di.pallet.type', string='Pallet type', help="Type of the pallet for the line")

    def delete_pallet(self):
        self.env.cr.commit() 

        # delete in di.palletization.line
        #company_code = self.env['sale.order'].search([('id', '=', self.id)]).company_id.id or self._context.get('company_id') or self.env['res.users']._get_company().id
        company_code = self.env['sale.order'].search([('id', '=', self.order_id.id)]).company_id.id
        id_order = self.order_id.id

        qty = self.quantity
        palletization_id = self.palletization_id.id
        no_pallet_supp = self.pallet_no
        order_id = self.order_id.id
        order_name = self.order_id.name
        no_product = self.product_id.id
        
        cnuf = self.order_id.company_id.di_cnuf or ""
        
        #self._cr.execute("DELETE FROM di_palletization_line  WHERE id=%s ", (self.id,))
        self.env['di.palletization.line'].search([('id', '=', self.id)]).unlink()
 
 
        # update in di.palletization : pallet_qty
        palletization_ids = self.env['di.palletization'].search([('id', '=', palletization_id)])
        if (palletization_ids) :
            qty_p =(palletization_ids.pallet_qty or 0) - qty
            qty_r =(palletization_ids.uom_qty or 0) - (qty_p  or 0)
            #palletization_ids.write({"pallet_qty":[(4, qty_p)]})
            palletization_ids.write({'pallet_qty': qty_p})
            palletization_ids.write({'input_qty': qty_r})
        
        
        no_pallet_exist = False
        pallets = self.env['di.palletization.line'].search([('order_id', '=', order_id), ('company_id', '=', company_code), ('pallet_no', '=', no_pallet_supp)] , order='pallet_no asc')
        for pallet in pallets:
            no_pallet_exist = True
            
        if (not no_pallet_exist):
            # rename No pallet : 
            pallets = self.env['di.palletization.line'].search([('order_id', '=', order_id), ('company_id', '=', company_code), ('pallet_no', '>=', no_pallet_supp)] , order='pallet_no asc')
            for pallet in pallets:
                der_no_pallet = pallet.pallet_no
                
                #new_no_pallet = self.calc_new_pallet(cnuf, self.order_id.id, der_no_pallet)
                new_no_pallet = self.env['di.palletization'].calc_new_pallet(cnuf, order_id, der_no_pallet, True)
                
                
                """
                if der_no_pallet !="001":           
                    num_pallet =  int(der_no_pallet) - 1
                else:
                    num_pallet =1      
                new_no_pallet = str(cnuf)
                new_no_pallet+= "{:04.0f}".format(order_id)
                new_no_pallet+= "{:03.0f}".format(num_pallet)
                """  
                name_line = ('Order : %s / Pallet : %s') % (order_name, new_no_pallet)
                pallet.write({'name': name_line, 'pallet_no': new_no_pallet})
            
            #new_no_pallet += 1
                
        self.env.cr.commit()
        
        self.env['di.palletization'].compute_pallet(order_id) 

    """
    def calc_new_pallet(self, cnuf=False, order_id=False, no_pallet=False):
        
        no_pallet=str(no_pallet)
        if no_pallet !="001":           
            num_pallet =  int(no_pallet) - 1
        else:
            num_pallet =1   
               
        new_no_pallet = str(cnuf)
        new_no_pallet+= "{:04.0f}".format(order_id)
        new_no_pallet+= "{:03.0f}".format(num_pallet)
                
        return new_no_pallet
    """

