# -*- coding: utf-8 -*-
from odoo import api, fields, models, modules

class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']
    
    auxiliary_accounting = fields.Boolean(string='Auxiliary Accounting', default=False)
    root_account_auxiliary_customer = fields.Char(string='Root Account Auxiliary Customer', default='C')
    root_account_auxiliary_supplier = fields.Char(string='Root Account Auxiliary Supplier', default='F')
    length_account_auxiliary = fields.Integer(string='Length for Account Auxiliary')
    length_account_general = fields.Integer(string='Length for Account General')
    complete_0_account_auxiliary = fields.Boolean(string='Complete right with 0 Account Auxiliary')
    complete_0_account_general = fields.Boolean(string='Complete right with 0 Account General')
    account_file_transfer = fields.Char(string='File For Account Transfer')
    writing_file_transfer = fields.Char(string='File For Writing Transfer')
    type_accounting = fields.Selection([('EBP', 'EBP'), ('QUADRA', 'QUADRA'), ('SAGE', 'SAGE')], string="Type of accounting", default='EBP')
    mail_accounting = fields.Boolean(string="Send Email", default=True)
    path_account_transfer = fields.Char(string='Path For Account Transfer')


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            auxiliary_accounting = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.auxiliary_accounting'),
            root_account_auxiliary_customer = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.root_account_auxiliary_customer'),
            root_account_auxiliary_supplier = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.root_account_auxiliary_supplier'),
            length_account_auxiliary = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.length_account_auxiliary'),
            length_account_general = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.length_account_general'),
            complete_0_account_auxiliary = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.complete_0_account_auxiliary'),
            complete_0_account_general = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.complete_0_account_general'),
            account_file_transfer = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.account_file_transfer'),
            writing_file_transfer = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.writing_file_transfer'),
            type_accounting = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.type_accounting'),
            mail_accounting = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.mail_accounting'),
            path_account_transfer = self.env['ir.config_parameter'].sudo().get_param('accounting_transfer.path_account_transfer'),

        )
        return res

    #@api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        _auxiliary_accounting = self.auxiliary_accounting and self.auxiliary_accounting or False
        _root_account_auxiliary_customer = self.root_account_auxiliary_customer and self.root_account_auxiliary_customer or False
        _root_account_auxiliary_supplier = self.root_account_auxiliary_supplier and self.root_account_auxiliary_supplier or False
        _length_account_auxiliary = self.length_account_auxiliary and self.length_account_auxiliary or False
        _length_account_general = self.length_account_general and self.length_account_general or False
        _complete_0_account_auxiliary = self.complete_0_account_auxiliary and self.complete_0_account_auxiliary or False
        _complete_0_account_general = self.complete_0_account_general and self.complete_0_account_general or False
        _account_file_transfer = self.account_file_transfer and self.account_file_transfer or False
        _writing_file_transfer = self.writing_file_transfer and self.writing_file_transfer or False
        _type_accounting = self.type_accounting and self.type_accounting or False
        _mail_accounting = self.mail_accounting and self.mail_accounting or False
        _path_account_transfer = self.path_account_transfer and self.path_account_transfer or False
       
        param.set_param('accounting_transfer.auxiliary_accounting', _auxiliary_accounting)
        param.set_param('accounting_transfer.root_account_auxiliary_customer', _root_account_auxiliary_customer)
        param.set_param('accounting_transfer.root_account_auxiliary_supplier', _root_account_auxiliary_supplier)
        param.set_param('accounting_transfer.length_account_auxiliary', _length_account_auxiliary)
        param.set_param('accounting_transfer.length_account_general', _length_account_general)
        param.set_param('accounting_transfer.complete_0_account_auxiliary', _complete_0_account_auxiliary)
        param.set_param('accounting_transfer.complete_0_account_general', _complete_0_account_general)
        param.set_param('accounting_transfer.account_file_transfer', _account_file_transfer)
        param.set_param('accounting_transfer.writing_file_transfer', _writing_file_transfer)
        param.set_param('accounting_transfer.type_accounting', _type_accounting)
        param.set_param('accounting_transfer.mail_accounting', _mail_accounting)
        param.set_param('accounting_transfer.path_account_transfer', _path_account_transfer)      