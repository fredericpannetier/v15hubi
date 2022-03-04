# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    di_auxiliary_account_customer = fields.Char(string='Auxiliary Account Customer')
    di_auxiliary_account_supplier = fields.Char(string='Auxiliary Account Supplier')

    @api.onchange('name', 'property_account_receivable_id')
    def _onchange_auxiliary(self):
       
        val_company_id = self.company_id.id or self._context.get('force_company', self.env.user.company_id.id)
        val_name = 'General Settings'
        name_partner = ""
        if self.name:
            name_partner = self.name.replace('\\','') \
                     .replace('"','') \
                     .replace('\n', '') \
                     .replace(' ', '') \
                     .replace('-', '') \
                     .replace('_', '') \
                     .replace("'", '') \
                     .replace('.', '') \
                     .replace('ê', 'e') \
                     .replace('è', 'e') \
                     .replace('é', 'e') \
                     .replace('à', 'a') \
                     .replace('ô', 'o') \
                     .replace('ö', 'o') \
                     .replace('î', 'i') 
                     
        settings = self.env['di.accounting.parameter'].search([('name','=', val_name), ('company_id','=', val_company_id)])                
        if settings:
            root_customer = settings.root_account_auxiliary_customer
            root_supplier = settings.root_account_auxiliary_supplier
            length_auxiliary = settings.length_account_auxiliary or 0
            complete_0_auxiliary = settings.complete_0_account_auxiliary or False
            
            if (root_customer and not self.di_auxiliary_account_customer ):
                account_customer = root_customer + name_partner
                if length_auxiliary != 0:
                    if (complete_0_auxiliary):
                        account_customer = account_customer.ljust(length_auxiliary,'0')
                    else:    
                        account_customer = account_customer[0:length_auxiliary]
                        
                self.di_auxiliary_account_customer = account_customer

            if (root_customer and not self.di_auxiliary_account_supplier ):
                account_supplier = root_supplier + name_partner
                if length_auxiliary != 0:
                    if (complete_0_auxiliary):
                        account_supplier = account_supplier.ljust(length_auxiliary,'0')
                    else:    
                        account_supplier = account_supplier[0:length_auxiliary]
            
                self.di_auxiliary_account_supplier = account_supplier
    
