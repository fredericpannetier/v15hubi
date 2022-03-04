# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    di_over_credit = fields.Boolean('Allow Over Credit?')
