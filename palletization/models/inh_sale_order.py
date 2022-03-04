# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class DiSaleOrderPalletization(models.Model):
    _inherit = 'sale.order'

    """
    @api.depends('palletization_line_ids')
    def _compute_pallet(self):
        for line in self:
            pallet_count = len(line.palletization_line_ids)
            line.update({
                'di_pallet_count': pallet_count
                
            })
    """     

    def _get_type_pallet(self):
        lst = []
        type_pallet_1 = self.env['ir.config_parameter'].sudo().get_param("palettization.di_pallet_type_1")
        lst.append(("1" ,type_pallet_1))
        
        type_pallet_2 = self.env['ir.config_parameter'].sudo().get_param("palettization.di_pallet_type_2")
        lst.append(("2" ,type_pallet_2))

        type_pallet_3 = self.env['ir.config_parameter'].sudo().get_param("palettization.di_pallet_type_3")
        lst.append(("3" ,type_pallet_3))
        
        return lst
    
    def _get_default_type_pallet(self):
        
        default_type_pallet = self.env['ir.config_parameter'].sudo().get_param("palettization.di_pallet_type_default_id") or 0
        
        return default_type_pallet
        
    di_pallet_number = fields.Integer(string = 'Number of pallet')
    #di_type_pallet = fields.Selection(_get_type_pallet, string="Pallet type", default="1" )
    di_type_pallet = fields.Many2one('di.pallet.type', string="Pallet type")#, default='_get_default_type_pallet' )
    
    palletization_ids = fields.One2many('di.palletization', 'order_id', string='Palletization Lines', copy=True, auto_join=True)
    palletization_line_ids = fields.One2many('di.palletization.line', 'order_id', string='Palletization Pallets')

    palletization_print_ids = fields.One2many('wiz.print.pallet', 'sale_order_id', string='Palletization Print')
    #di_pallet_count = fields.Integer(string = 'Quantity of pallet', stored = True, readonly=True, compute ='_compute_pallet')

    def _get_query_create_pallet_sale(self):
        return """SELECT  order_id, sale_order_line.product_id, di_paltyp_id, 
                coalesce(pack_num,0) AS default_pallet_qty,
                sum(product_uom_qty)  AS uom_qty,
                ''  AS batch_number,
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
#         self.env['di.logbook'].create({'message' : "test"})
        self.env.cr.commit()
        company_code = self.env['sale.order'].search([('id', '=', self.id)]).company_id.id
        id_order = self.id
        
#         if self.di_type_pallet.id==False: # SC normalement ce n'est plus utile
#             default_type = self._get_default_type_pallet() or False
#             if default_type:
#                 self.update({
#                     'di_type_pallet': default_type, 
#                         })
                    
        query_args = {'id_order' : id_order, 'company_code' : company_code}
    
        #Modif SC 01/04/2021, ajout du type de palette à la ligne
        query= self._get_query_create_pallet_sale()
#         _logger.debug("ids")            

        self.env.cr.execute(query, query_args)
        ids = [(r[0],r[1],r[2],r[3],r[4],r[5],r[6]) for r in self.env.cr.fetchall()]
#         _logger.debug(ids)
#         self.env['di.logbook'].create({'message' : str(ids)})    
        for  order_id, prod_id, type_pallet, max_qty, uom_qty, batch_number,line_id in ids:
#             self.env['di.logbook'].create({'message' : str(order_id)+ str(prod_id)+ str(type_pallet)+ str(max_qty)+ str(uom_qty)+ str(batch_number)})
#             _logger.debug(str(order_id)+ str(prod_id)+ str(type_pallet)+ str(max_qty)+ str(uom_qty)+ str(batch_number))
#             if max_qty >0:
            palletization_ids = self.env['di.palletization'].search([('order_id', '=', order_id), ('product_id', '=', prod_id),  ('line_id', '=', line_id), ('batch_number', '=', batch_number), ('company_id', '=', company_code)])
            if not palletization_ids:
                # Create palletization 
                _logger.debug(str(max_qty))
                name_line = ('Order : %s ') % (order_id)
                pallet_vals = {
                    'name': name_line,
                    'company_id': company_code,
                    'order_id': order_id,
                    'product_id': prod_id,
                    'uom_qty': uom_qty,
                    'default_pallet_qty': max_qty,
                    'pallet_qty': 0,
                    'paltyp_id':type_pallet, #SC
                    'batch_number':batch_number,
                    'line_id':line_id,
                    }
                self.env['di.palletization'].create(pallet_vals)  
                self.env.cr.commit()
            else:
                
                palletization_ids = self.env['di.palletization'].search([('order_id', '=', order_id),('paltyp_id', '=', type_pallet), ('product_id', '=', prod_id),  ('line_id', '=', line_id), ('batch_number', '=', batch_number), ('company_id', '=', company_code)])
                for pallets in palletization_ids:
                    _logger.debug(str(max_qty))
                    pallets.update({
                        'uom_qty': uom_qty,
                        'default_pallet_qty': max_qty,
                
                    })
                    
            

    def create_pallet(self):
        self.env.cr.commit()
        # Find the last pallet
        company_code = self.env['sale.order'].search([('id', '=', self.id)]).company_id.id
        cnuf = self.company_id.di_cnuf or ""
        id_order = self.id

        no_pallet = ""
        query_args = {'id_order' : id_order, 'company_code' : company_code}
        query = """SELECT pallet_no FROM di_palletization_line 
                    WHERE order_id=%(id_order)s  and company_id=%(company_code)s  
                    order by pallet_no desc LIMIT 1"""

        self.env.cr.execute(query, query_args)
        ids = [(r[0]) for r in self.env.cr.fetchall()]
            
        for last_no in ids:
            no_pallet=last_no  
        

        # Update pallet_qty on di_palletization
        self.create_pallet_sale()
                    
        # Create palletization line    
        #query="""SELECT id, order_id, product_id,
        #        coalesce(default_pallet_qty,0) AS default_pallet_qty,
        #        coalesce(uom_qty,0)  AS uom_qty,
        #        coalesce(pallet_qty,0)  AS pallet_qty, batch_number, date_limit   
        #        FROM di_palletization
        #        where order_id = %(id_order)s  and company_id=%(company_code)s 
        #        order by order_id, product_id"""    

        #self.env.cr.execute(query, query_args)
        #ids = [(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7]) for r in self.env.cr.fetchall()]
            
        #for  palletization_id, order_id, prod_id, max_qty, uom_qty, pallet_qty, batch_number, date_limit in ids:
            
        palletization_ids = self.env['di.palletization'].search([('order_id', '=', id_order), ('company_id', '=', company_code)]) 
        for pallets in palletization_ids: 
            palletization_id = pallets.id
            order_id = pallets.order_id
            prod_id = pallets.product_id 
            max_qty = pallets.default_pallet_qty or 0
            uom_qty = pallets.uom_qty or 0
            pallet_qty = pallets.pallet_qty or 0 
            batch_number = pallets.batch_number or False
            date_limit = pallets.date_limit or False
            paltyp_id = pallets.paltyp_id.id #SC
              
            reste = uom_qty - pallet_qty
            qty_a_pl= uom_qty - pallet_qty
            _logger.debug(str(max_qty))
#             palletization_line_ids = self.env['di.palletization.line'].search([('palletization_id', '=', palletization_id), ('company_id', '=', company_code)])
            palletization_line_ids = self.env['di.palletization.line'].search([('palletization_id', '=', palletization_id), ('company_id', '=', company_code),('paltyp_id','=',paltyp_id)])#SC
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
                        new_no_pallet = self.env['di.palletization'].calc_new_pallet(cnuf, order_id.id, no_pallet)
                    
#                         product = self.env['product.product'].search([('id','=', prod_id.id), ('company_id','=', company_code)])
                        # Create palletization line
                        name_line = ('Order : %s / Pallet : %s') % (order_id.name, new_no_pallet)
                        p_weight = prod_id.get_pack_weight()
                        pallet_line_vals = {
                            'name': name_line,
                            'company_id': company_code,
                            'palletization_id': palletization_id,
                            'order_id': order_id.id,
                            'product_id': prod_id.id,
                            'quantity': qty,
                            'weight': qty * p_weight,                            
                            'pallet_no': new_no_pallet,
                            'batch_number': batch_number,
                            'date_limit': date_limit,
                            'paltyp_id': paltyp_id, #SC
                            
                            }
                        self.env['di.palletization.line'].create(pallet_line_vals)  
                        no_pallet = new_no_pallet
                        
                    # Update pallet_qty on di_palletization
                    #self._cr.execute("UPDATE di_palletization set pallet_qty = %s, input_qty = %s WHERE id=%s ", (uom_qty, reste, palletization_id))
                    #self.env.cr.commit()
                    pallets.update({
                            'pallet_qty': uom_qty,
                            'input_qty': reste,
                    
                        })
                  
        self.env['di.palletization'].compute_pallet(id_order)             

    
#     def create_pallet_old(self):
#         self.env.cr.commit()
#         #if self.palletization_line_ids:
#         #    return
#         
#         # Find the last pallet
#         #company_code = self.env['sale.order'].search([('id', '=', self.id)]).company_id.id or self._context.get('company_id') or self.env['res.users']._get_company().id
#         company_code = self.env['sale.order'].search([('id', '=', self.id)]).company_id.id
#         id_order = self.id
# 
#         no_pallet = 0
#         query_args = {'id_order' : id_order, 'company_code' : company_code}
#         query = """SELECT pallet_no FROM di_palletization_line 
#                     WHERE order_id=%(id_order)s  and company_id=%(company_code)s  
#                     order by pallet_no desc LIMIT 1"""
# 
#         self.env.cr.execute(query, query_args)
#         ids = [(r[0]) for r in self.env.cr.fetchall()]
#             
#         for last_no in ids:
#             no_pallet=last_no 
#         
# 
#         # Update pallet_qty on di_palletization
#         # Find the sale.order.line
#         self.create_pallet_sale()
#         
#         #query="""SELECT  order_id, product_id, di_type_pallet, 
#         #        case  
#         #             when di_type_pallet = '3' then coalesce(product_template.di_default_pallet_qty_3,0) 
#         #             when di_type_pallet = '2' then coalesce(product_template.di_default_pallet_qty_2,0) 
#         #             else coalesce(product_template.di_default_pallet_qty_1,0)  
#         #             END  AS default_pallet_qty,
#         #        sum(product_uom_qty)  AS uom_qty   
#         #        FROM sale_order_line 
#         #        inner join sale_order on sale_order_line.order_id = sale_order.id
#         #        inner join product_product on product_id = product_product.id
#         #        inner join product_template on product_template.id = product_product.product_tmpl_id
#         #        where order_id = %(id_order)s  and sale_order_line.company_id=%(company_code)s 
#         #        group by order_id, product_id, di_type_pallet, 
#         #        case  
#         #             when di_type_pallet = '3' then coalesce(product_template.di_default_pallet_qty_3,0) 
#         #             when di_type_pallet = '2' then coalesce(product_template.di_default_pallet_qty_2,0) 
#         #             else coalesce(product_template.di_default_pallet_qty_1,0)  
#         #             END
#         #        order by order_id, product_id"""    
# 
#         
#         #self.env.cr.execute(query, query_args)
#         #ids = [(r[0],r[1],r[2],r[3],r[4]) for r in self.env.cr.fetchall()]
#             
#         #for  order_id, prod_id, type_pallet, max_qty, uom_qty in ids:
#         #    if max_qty >0:
#         #        palletization_ids = self.env['di.palletization'].search([('order_id', '=', order_id), ('product_id', '=', prod_id), ('company_id', '=', company_code)])
#         #        if not palletization_ids:
#         #            # Create palletization 
#         #            name_line = ('Order : %s ') % (order_id)
#         #            pallet_vals = {
#         #                'name': name_line,
#         #                'company_id': company_code,
#         #                'order_id': order_id,
#         #                'product_id': prod_id,
#         #                'uom_qty': uom_qty,
#         #                'default_pallet_qty': max_qty,
#         #                'pallet_qty': 0,
#         #                }
#         #            palletization = self.env['di.palletization'].create(pallet_vals)  
#         #        else:
#         #            #query_maj = """UPDATE di_palletization set uom_qty = %s, default_pallet_qty = %s  
#         #            #WHERE order_id=%s AND product_id=%s  and company_id=%s """
#         #            #self._cr.execute(query_maj, (uom_qty, max_qty, order_id, prod_id, company_code))
#         #            #self.env.cr.commit()
#         #            for pallets in palletization_ids:
#         #                pallets.update({
#         #                    'uom_qty': uom_qty,
#         #                    'default_pallet_qty': max_qty,
#                     
#         #                })
#                     
#             
#         # Create palletization line    
#         query="""SELECT id, order_id, product_id,
#                 coalesce(default_pallet_qty,0) AS default_pallet_qty,
#                 coalesce(uom_qty,0)  AS uom_qty,
#                 coalesce(pallet_qty,0)  AS pallet_qty, batch_number, date_limit   
#                 FROM di_palletization
#                 where order_id = %(id_order)s  and company_id=%(company_code)s 
#                 order by order_id, product_id"""    
# 
#         self.env.cr.execute(query, query_args)
#         ids = [(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7]) for r in self.env.cr.fetchall()]
#             
#         for  palletization_id, order_id, prod_id, max_qty, uom_qty, pallet_qty, batch_number, date_limit in ids:
#             reste = uom_qty - pallet_qty
#             qty_a_pl= uom_qty - pallet_qty
#                 
#             palletization_line_ids = self.env['di.palletization.line'].search([('palletization_id', '=', palletization_id), ('company_id', '=', company_code)])
#             if (not palletization_line_ids) or (qty_a_pl != 0):
#                 qty = 0
#  
#                 if max_qty > 0:
#                     while qty_a_pl !=0:
#                         if qty_a_pl >= max_qty:
#                             qty = max_qty
#                             reste = qty_a_pl - max_qty
#                         else:
#                             qty = qty_a_pl
#                             reste = 0
#                 
#                         qty_a_pl = reste
#                         no_pallet += 1
#                     
#                         product = self.env['product.product'].search([('id','=', prod_id), ('company_id','=', company_code)])
#                         # Create palletization line
#                         name_line = ('Order : %s / Pallet : %s') % (order_id, no_pallet)
#                         p_weight = product.weight
#                         pallet_line_vals = {
#                             'name': name_line,
#                             'company_id': company_code,
#                             'palletization_id': palletization_id,
#                             'order_id': order_id,
#                             'product_id': prod_id,
#                             'quantity': qty,
#                             'weight': qty * p_weight,
#                             'pallet_no': no_pallet,
#                             'batch_number': batch_number,
#                             'date_limit': date_limit,
#                             
#                             }
#                         palletization_line = self.env['di.palletization.line'].create(pallet_line_vals)  
#                 
#                     # Update pallet_qty on di_palletization
#                     self._cr.execute("UPDATE di_palletization set pallet_qty = %s, input_qty = %s WHERE id=%s ", (uom_qty, reste, palletization_id))
#                     self.env.cr.commit()
#                   
#         self.env['di.palletization'].compute_pallet(order_id)             
                    
#    @api.multi
    def action_palletization(self):
        self.env.cr.commit()
        #self.create_pallet()  
        self.create_pallet_sale()
        
        self.ensure_one()
        view_id = self.env["ir.model.data"].get_object_reference("palletization", "di_palletization_form")
        
        action = self.env.ref('palletization.action_di_palletization').read()[0]
        ##action['views'] = [(self.env.ref('palletization.di_palletization_form').id, 'form')]
        action['views'] = [(view_id[1], 'form')]
        action['res_id'] = self.id
        action['res_model'] = "sale.order"
        
        return action
    
    def print_etiquet_pallet(self):  
        self.env.cr.commit()
        no_id = self.id
        nom_table = "sale_order"
        #self.env['wiz.print.pallet'].create_print_etiquet_pallet(no_id)
        
        #tools_hubi.prepareprintetiqcarrier(self, nom_table, no_id)
        #return {'type': 'ir.actions.act_window_close'}
        #return self.env.ref('palletization.action_report_pallet').report_action(self)   
        if no_id:        
            self.create_print_etiquet_pallet(no_id)
            return self.env.ref('palletization.action_report_pallet').report_action(self) 
        
    def create_print_etiquet_pallet(self, no_id):
        if no_id:
            company_code = self.env['sale.order'].search([('id', '=', self.id)]).company_id.id
            #req = "DELETE FROM wiz_print_pallet WHERE sale_order_id=" + str(no_id) + " and company_id=" + str(company_code)
            #self._cr.execute(req)
            self.env.cr.commit()
            
            self.env['wiz.print.pallet'].search([('sale_order_id', '=', no_id), ('company_id', '=', company_code)]).unlink()
            
            saleorder = self.env['sale.order'].search([('id', '=', no_id), ])         
            for sale in saleorder:
                
                """
                type_pallet = self.env['ir.config_parameter'].sudo().get_param("palettization.di_pallet_type_1")
                if sale.di_type_pallet == "3":
                   type_pallet = self.env['ir.config_parameter'].sudo().get_param("palettization.di_pallet_type_3")
                if sale.di_type_pallet == "2":
                   type_pallet = self.env['ir.config_parameter'].sudo().get_param("palettization.di_pallet_type_2")   
              
                client_name1 = sale.partner_id.di_customer_name_etiq or sale.partner_id.name
                client_name2 = sale.partner_id.di_customer_city_etiq or sale.partner_id.state_id.name
                
                etab_exp1 = sale.partner_id.di_sender_establishment.di_company_name_etiq or ""
                etab_exp2 = sale.partner_id.di_sender_establishment.di_company_city_etiq or ""
                sending_date = ""
                packaging_date = ""
                
                if sale.di_sending_date:
                    sending_date = fields.Date.from_string(sale.di_sending_date).strftime('%d/%m/%Y')
                if sale.di_packaging_date:    
                    packaging_date = fields.Date.from_string(sale.di_packaging_date).strftime('%d/%m/%Y')
                etab_exp_no = sale.partner_id.di_sender_establishment.id
                """
                
                carrier_name = sale.carrier_id.name
                commitment_date = ""
                if sale.commitment_date:
                    commitment_date = fields.Date.from_string(sale.commitment_date).strftime('%d/%m/%Y')
                
                order_no = sale.id
                partner_no = sale.partner_id.id
                carrier_no = sale.carrier_id.id
                
                code_barre = ""
#                 type_pallet =  sale.di_type_pallet.name # SC ,le type de palette est désormais enregistré sur la palette  
                   
                # Lecture des lignes Palettes : 1 étiquette par palette
                num_pallet = "999"
                linepallet = self.env['di.palletization.line'].search([ ('order_id', '=', sale.id) ]) 
                
                description_item = ""
                pallet_qty = 0   
                weight_total = 0
                package_total = 0
                use_pal_total = 0
                             
                for line in linepallet:
                    if num_pallet != line.pallet_no:   # and num_pallet != "999":
                        # enregistrement des infos en-tete dans la table
                        num_pallet = line.pallet_no
                        pallet_vals = {
                            'no_pallet': num_pallet,
                            'sale_order_id':order_no,
                            'company_id': company_code,
                            #'etab_exped_id': etab_exp_no,
                            'partner_id':partner_no,
                            'carrier_id': carrier_no,
                            'commitment_date':commitment_date,
                            'code_barre':code_barre,                    
#                             'type_pallet':type_pallet,
                            'type_pallet':line.paltyp_id.name and line.paltyp_id.name or "", #SC
                            'weight_total': 0,
                            'package_total': 0,
                            'use_pal_total':0,
                            }

                        pallet = self.env['wiz.print.pallet'].create(pallet_vals)
                        print_pallet_id = pallet.id
                        
                        #num_pallet = ""
                        description_item = ""
                        weight_total = 0
                        package_total = 0
                        use_pal_total = 0
                            
                    num_pallet = line.pallet_no
                    description_item = line.product_id.di_pallet_description or line.product_id.name 
                    qty = line.quantity or 0
                    weight = line.weight or 0
                    package = self.calc_package(sale, line)
#                     use_pal = self.calc_use_pal(sale.company_id.id, sale.di_type_pallet.id , line.product_id.id, package) or 0
                    use_pal = self.calc_use_pal(sale.company_id.id, line.paltyp_id.id , line.product_id.id, package) or 0 #SC
                    
                    package_total += qty
                    weight_total += weight
                    use_pal_total += use_pal
  
                    # enregistrement des infos ligne dans la table
                    pallet_line_vals = {
                            'print_pallet_id' : print_pallet_id,
                            'no_pallet': num_pallet,
                            'sale_order_id':order_no,
                            'product_id': line.product_id.id,
                            'description_item':description_item,
                            'batch_number':line.batch_number,
                            
                            'dlc_date':line.date_limit,
                            'package':package,                    
                            'quantity':qty,
                            'weight':weight,
                            'use_pal':use_pal,
                            }

                    self.env['wiz.print.pallet.line'].create(pallet_line_vals)
                    
                    pallet.update({
                            'weight_total': weight_total,
                            'package_total': package_total,
                            'use_pal_total': use_pal_total,
                        })

    def calc_package(self, sale, line):
        return line.quantity and line.quantity or 0
        
    def calc_use_pal(self, company, type_pallet , product, package, packaging_id=0):
        use_pal = 0
        pack_num = self.env['di.pallet.product'].search([ ('pallet_type_id', '=', type_pallet), ('company_id', '=', company), ('product_id', '=', product) ]).pack_num
        if pack_num != 0:
            use_pal =  round(package / pack_num, 2)                                 
        return use_pal    
    
    
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
                           
        
    def _di_default_paltyp(self):        
        paltyp = self.env['di.pallet.type'].browse(int(self.env['ir.config_parameter'].sudo().get_param('palettization.di_pallet_type_default_id')))                
        return paltyp
                 
    #Modif SC 01/04/2021, ajout du type de palette à la ligne                                                                  
    di_paltyp_id = fields.Many2one('di.pallet.type', string='Pallet type', help="Type of the pallet for the line", default=_di_default_paltyp)