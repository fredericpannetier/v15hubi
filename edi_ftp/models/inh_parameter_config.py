# -*- coding: utf-8 -*-
from odoo import api, fields, models, modules

class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']
    
    ftp_name = fields.Char(string='Name FTP')
    ftp_address = fields.Char(string='Address FTP')
    ftp_port = fields.Char(string='Port FTP')
    ftp_login = fields.Char(string='Login FTP')
    ftp_password = fields.Char(string='Password FTP')
    ftp_directory = fields.Char(string='FTP Directory')
    
    invoice_file_edi = fields.Char(string='File For Invoice EDI', 
                                   help="""The string [datetime] will  be replaced  by the current datetime. It is useful if you want to keep an history of your files and not delete the last one when you make a new one.""")
    sale_file_edi = fields.Char(string='File For Sale EDI',
                                help="""The string [datetime] will  be replaced  by the current datetime. It is useful if you want to keep an history of your files and not delete the last one when you make a new one.""")

    ftp_directory_import_sale = fields.Char(string='FTP Directory for Import Sale')
    local_directory_import_sale = fields.Char(string='Local Directory for Import Sale')
    ftp_sale_file = fields.Char(string='FTP Sale File')
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            ftp_name = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_name'),
            ftp_address = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_address'),
            ftp_port = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_port'),
            ftp_login = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_login'),
            ftp_password = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_password'),
            ftp_directory = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_directory'),
            invoice_file_edi = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.invoice_file_edi'),
            sale_file_edi = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.sale_file_edi'),
            
            ftp_directory_import_sale = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_directory_import_sale'),
            local_directory_import_sale = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.local_directory_import_sale'),
            ftp_sale_file = self.env['ir.config_parameter'].sudo().get_param('edi_ftp.ftp_sale_file'),

        )
        return res

    #@api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        _ftp_name = self.ftp_name and self.ftp_name or False
        _ftp_address = self.ftp_address and self.ftp_address or False
        _ftp_port = self.ftp_port and self.ftp_port or False
        _ftp_login = self.ftp_login and self.ftp_login or False
        _ftp_password = self.ftp_password and self.ftp_password or False
        _ftp_directory = self.ftp_directory and self.ftp_directory or False
        _invoice_file_edi = self.invoice_file_edi and self.invoice_file_edi or False
        _sale_file_edi = self.sale_file_edi and self.sale_file_edi or False
        
        _ftp_directory_import_sale = self.ftp_directory_import_sale  or False
        _local_directory_import_sale = self.local_directory_import_sale  or False
        _ftp_sale_file = self.ftp_sale_file or False       
               
        param.set_param('edi_ftp.ftp_name', _ftp_name)
        param.set_param('edi_ftp.ftp_address', _ftp_address)
        param.set_param('edi_ftp.ftp_port', _ftp_port)
        param.set_param('edi_ftp.ftp_login', _ftp_login)
        param.set_param('edi_ftp.ftp_password', _ftp_password)
        param.set_param('edi_ftp.ftp_directory', _ftp_directory)
        param.set_param('edi_ftp.invoice_file_edi', _invoice_file_edi)
        param.set_param('edi_ftp.sale_file_edi', _sale_file_edi)
        
        param.set_param('edi_ftp.ftp_directory_import_sale', _ftp_directory_import_sale)
        param.set_param('edi_ftp.local_directory_import_sale', _local_directory_import_sale)
        param.set_param('edi_ftp.ftp_sale_file', _ftp_sale_file)
        