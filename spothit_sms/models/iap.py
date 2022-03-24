# ©  2015-2018 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import fields, models


class IapAccount(models.Model):
    _inherit = "iap.account"

    endpoint = fields.Char(string='URL to SMS web service (all before ?)')
    expeditor = fields.Char(string='Name that appears upon message')
