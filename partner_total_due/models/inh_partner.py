# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    di_total_due = fields.Monetary(compute='_compute_total_due', string='Total Due')
    di_total_overdue = fields.Monetary(compute='_compute_total_due', string='Total Overdue')
    
    residual_aml_ids = fields.One2many('account.move.line', 'partner_id',
                                           domain=[
                                                   ('move_id.payment_state', 'in', ('not_paid', 'partial')),
                                                   ('move_id.state', '=', 'posted' )])
    

    def _compute_total_due(self):
        """
        Compute the fields 'total_due', 'total_overdue'
        """
        
        today = fields.Date.context_today(self)
        for record in self:
            total_due = 0
            total_overdue = 0
           
            for aml in record.residual_aml_ids:
                if aml.company_id == self.env.company:
                    amount = aml.amount_residual
                    total_due += amount
                    is_overdue = today > aml.date_maturity if aml.date_maturity else today > aml.date
                    if is_overdue and not aml.blocked:
                        total_overdue += amount
            record.di_total_due = total_due
            record.di_total_overdue = total_overdue
            
