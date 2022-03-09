# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class MiadiAccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends('account_id', 'partner_id')
    def _display_account_aux(self):
        result = []
        for account in self:
            compte = ""
            if account.account_id:
                if account.account_id.code[0:2] == "41":
                    compte = account.partner_id.di_auxiliary_account_customer or ""
                if account.account_id.code[0:2] == "40":
                    compte = account.partner_id.di_auxiliary_account_supplier or ""
            
                if compte != "":    
                   account.update({'di_account_aux': compte})       
            #result.append((compte))
        #return result
    

    di_transfer_accounting = fields.Boolean(string='Transfer Accounting', default=False) 
    #di_payment_mode_id = fields.Integer(string='Payment mode', related='payment_id.di_payment_mode_id.id')
    di_account_aux = fields.Char(string='Auxilary Account', store=True, compute='_display_account_aux' )
    di_move_state = fields.Selection(string='State', related='move_id.state', store=False)
    
    """
    @api.onchange('di_transfer_accounting')
    def di_onchange_di_transfer_accounting(self):
        move = self.env["account.move"].search([("id", "=", self.move_id)] )
        transfer_lines = move.line_ids.filtered(lambda line: line.di_transfer_accounting)
        move.update({
                'di_transfer_lines_count': len(transfer_lines),
                
            })
    """
        
    def copy_data(self, default=None):
        res = super(MiadiAccountMoveLine, self).copy_data(default=default)

        for line, values in zip(self, res):
            values['di_transfer_accounting'] = False
            
        return res
    
   
class MiadiAccountMove(models.Model):
    _inherit = "account.move"
    
    di_transfer_lines_count = fields.Integer(string="Number transfered lines", compute='_compute_transfer_line', store=True)
    
    @api.depends( 'line_ids.di_transfer_accounting')
    def _compute_transfer_line(self):
        for move in self:
            transfer_lines = move.line_ids.filtered(lambda line: line.di_transfer_accounting)
            move.update({
                'di_transfer_lines_count': len(transfer_lines),
                
            })
    
    """
            move_line = self.env["account.move.line"].search(
                [
                    ("move_id", "=", move.id),
                    ("di_transfer_accounting", "=", True),
                ],
                )
            move.di_transfer_lines_count = len(move_line)
    """
            
                
    def _reverse_moves(self, default_values_list=None, cancel=False):
        credit_note = super(MiadiAccountMove, self)._reverse_moves(default_values_list, cancel)   
        if credit_note:
            for credit in credit_note:
                for line in credit.line_ids:
                    line.update({'di_transfer_accounting':False})
        return credit_note
       