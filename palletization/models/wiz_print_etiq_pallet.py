from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import os, sys
    
class wizard_printetiquetpallet(models.Model):
    _name = "wiz.print.pallet"
    _description = "Wizard print etiquette pallet"
    
    no_pallet = fields.Char(string='No Pallet')
    company_id = fields.Many2one('res.company', string='Company')
    sale_order_id = fields.Many2one("sale.order", string='Sale Order')
    etab_exped_id = fields.Many2one("res.partner", string='Sender')
    partner_id = fields.Many2one("res.partner", string='Partner')
    carrier_id = fields.Many2one("delivery.carrier", string='Carrier')
    
    commitment_date = fields.Char(string="Commitment Date")
    code_barre = fields.Char(string="Code barre")
    type_pallet = fields.Char(string="Type pallet")
    weight_total = fields.Float(string="Weight total")
    package_total = fields.Float(string="Package total")
    sending_date = fields.Char(string="Sending Date")
    packaging_date = fields.Char(string="Packaging Date")
    use_pal_total = fields.Float(string="Use of the pallet total")
    
    line_pallet_ids = fields.One2many('wiz.print.pallet.line', 'print_pallet_id', string='Print pallet lines', copy=True, auto_join=True)
    
#     def z_create_print_etiquet_pallet_old(self, no_id):
#         if no_id:
#             #req = "DELETE FROM wiz_print_pallet WHERE sale_order_id=" + str(no_id)
#             #self._cr.execute(req)
#             self.env.cr.commit()
#             
#             self.env['wiz.print.pallet'].search([('sale_order_id', '=', no_id)]).unlink()
#             
#             saleorder = self.env['sale.order'].search([('id', '=', no_id), ])         
#             for sale in saleorder:
#                 client_name1 = sale.partner_id.di_customer_name_etiq or sale.partner_id.name
#                 client_name2 = sale.partner_id.di_customer_city_etiq or sale.partner_id.state_id.name
#                 carrier_name = sale.carrier_id.name
#                 etab_exp1 = sale.partner_id.di_sender_establishment.di_company_name_etiq or ""
#                 etab_exp2 = sale.partner_id.di_sender_establishment.di_company_city_etiq or ""
#                 sending_date = ""
#                 packaging_date = ""
#                 
#                 commitment_date = ""
#                 if sale.di_sending_date:
#                     sending_date = fields.Date.from_string(sale.di_sending_date).strftime('%d/%m/%Y')
#                 if sale.di_packaging_date:    
#                     packaging_date = fields.Date.from_string(sale.di_packaging_date).strftime('%d/%m/%Y')
#                 if sale.commitment_date:
#                     commitment_date = fields.Date.from_string(sale.commitment_date).strftime('%d/%m/%Y')
#                 
#                 order_no = sale.id
#                 partner_no = sale.partner_id.id
#                 carrier_no = sale.carrier_id.id
#                 #etab_exp_no = sale.partner_id.di_sender_establishment.id
#                 code_barre = ""
#                 type_pallet = ""
#                 
#                 # Lecture des lignes Palettes : 1 étiquette par palette
#                 num_pallet = "999"
#                 linepallet = self.env['di.palletization.line'].search([
#                     ('order_id', '=', sale.id)
#                     
#                      ]) 
#                 
#                 description_item = ""
#                 pallet_qty = 0   
#                 weight_total = 0
#                 package_total = 0
#                              
#                 for line in linepallet:
#                     if num_pallet != line.pallet_no:   # and num_pallet != "999":
#                         # enregistrement des infos en-tete dans la table
#                         num_pallet = line.pallet_no
#                         pallet_vals = {
#                             'no_pallet': num_pallet,
#                             'sale_order_id':order_no,
# #                             'etab_exped_id': etab_exp_no,
#                             'partner_id':partner_no,
#                             'carrier_id': carrier_no,
#                             'commitment_date':commitment_date,
#                             'code_barre':code_barre,                    
#                             'type_pallet_id':type_pallet,
#                             'weight_total': 0,
#                             'package_total': 0,
#                             'sending_date': sending_date,
#                             'packaging_date':packaging_date,        
#                             }
# 
#                         pallet = self.env['wiz.print.pallet'].create(pallet_vals)
#                         print_pallet_id = pallet.id
#                         
#                         #num_pallet = ""
#                         description_item = ""
#                         weight_total = 0
#                         package_total = 0
#                             
#                     num_pallet = line.pallet_no
#                     description_item = line.product_id.pallet_description or line.product_id.name 
#                     qty = line.quantity or 0
#                     package = line.quantity or 0
#                     weight = line.weight or 0
#                     package_total += qty
#                     weight_total += weight
#                     lot_no = ""
#                     lot_name = ""
#                     dlc_date = ""
#                     
#                     # enregistrement des infos ligne dans la table
#                     pallet_line_vals = {
#                             'print_pallet_id' : print_pallet_id,
#                             'no_pallet': num_pallet,
#                             'sale_order_id':order_no,
#                             'product_id': line.product_id.id,
#                             'lot_id':lot_no,
#                             'lot_name': lot_name,
#                             'dlc_date':dlc_date,
#                             'package':package,                    
#                             'quantity':qty,
#                             'weight':weight,
#                             }
# 
#                     pallet_line = self.env['wiz.print.pallet.line'].create(pallet_line_vals)
#         
#                 #if num_pallet != "" and num_pallet != "999":
#                 #    # enregistrement des infos en-tête dans la table
#                 #    pallet = self.env['wiz.print.pallet'].create(pallet_vals)
#             
#             query_args = {'sale_order_id': no_id}
#             query = "SELECT id FROM wiz_print_pallet WHERE sale_order_id=" + str(no_id)
#             self.env.cr.execute(query)
#             
#             ids = [(r[0]) for r in self.env.cr.fetchall()]
#             return self.env.ref('palletization.action_report_pallet').report_action(ids)
        

class wizard_printetiquetpalletline(models.Model):
    _name = "wiz.print.pallet.line"
    _description = "Wizard print etiquette pallet - lines"
    _order = 'print_pallet_id, id'
    
    print_pallet_id = fields.Many2one('wiz.print.pallet', string='No Pallet', required=True, ondelete='cascade', index=True, copy=False)
    no_pallet = fields.Char(string='No Pallet')
    sale_order_id = fields.Many2one("sale.order", string='Sale Order')
    product_id = fields.Many2one("product.product", string='Products to print')
    description_item = fields.Char(string='Description Item')  
    dlc_date = fields.Char(string="DLC Date")
    batch_number = fields.Char(string="Batch Number")
    weight = fields.Float(string="Weight")
    package = fields.Float(string="Package")
    quantity = fields.Float(string="Quantity")    
    use_pal = fields.Float(string="Use of the pallet")
    