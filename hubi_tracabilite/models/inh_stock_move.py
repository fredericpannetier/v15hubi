# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
   
class HubiTracabiliteMove(models.Model):
    _inherit = "stock.move"
 
    di_lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number',
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]", check_company=True)
    #di_lot_id = fields.Many2one('stock.quant', 'Lot/Serial Number',
    #    domain="[('product_id', '=', product_id), ('company_id', '=', company_id), ('location_id', '=', location_id) , ('quantity', '>', 0)]", check_company=True)
    
    di_lot_name = fields.Char('Lot/Serial Number Name')
    di_qty_pack = fields.Float(string='Quantity of Packs')
    di_stock_packaging= fields.Many2one('di.multi.table', string='Stock Packaging', domain=[('record_type', '=', 'StockPackaging')], help="The Packaging of the stock.")
    di_location_first = fields.Char('First Location')
    di_location_last = fields.Char('Last Location')
    
    def _set_product_qty(self):
        return ""
    
    @api.onchange('di_qty_pack', 'di_stock_packaging')
    def _calcul_qty(self):
        qty=0
        if (self.di_qty_pack != 0) and (self.di_stock_packaging.weight != 0):
            qty = self.di_qty_pack * self.di_stock_packaging.weight
            self.product_uom_qty = qty
     
    @api.onchange('product_id')
    def _change_product(self):
        
        _origin = self._context.get('form_view_ref') or ''
        _origin_picking = self._context.get('default_picking_id') or ''
        if _origin == "hubi_tracabilite.view_tracabilite_form" and not _origin_picking: 
           raise UserError(_('You must first save.'))

        """
                _origin = self._context.get('form_view_ref') or ''
                if _origin == "hubi_tracabilite.view_tracabilite_form" and not self.ids:
                    picking_vals = {
                        'state': 'draft',
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'date': fields.Datetime.now(),
                        'picking_type_id': self.picking_type_id.id,
                    
                    }
                    picking = self.env['stock.picking'].create(picking_vals)
        """
           

    @api.onchange('di_lot_id', 'product_id', 'location_id')
    def _calcul_lot_qty(self):
        qty=0
        for line in self:
            if line.di_lot_id and line.product_id and line.location_id:
                qtys =self.env['stock.quant'].search([('product_id', '=', line.product_id.id), ('location_id', '=', line.location_id.id), ('lot_id', '=', line.di_lot_id.id)])#.mapped('quantity')
                qty=qtys.quantity
                if qty <= 0:
                    raise UserError(_('No available quantity for this location and this lot.'))

                
    @api.constrains('di_lot_id', 'product_id', 'location_id')
    def _check_lot_product(self):
        for line in self:
            if line.di_lot_id and line.product_id != line.di_lot_id.sudo().product_id:
                raise ValidationError(_(
                    'This lot %(lot_name)s is incompatible with this product %(product_name)s',
                    lot_name=line.di_lot_id.name,
                    product_name=line.product_id.display_name
                ))
                
                 
           
                
                

class HubiTracabiliteMoveLine(models.Model):
    _inherit = "stock.move.line"
 
    def _set_product_qty(self):
        return ""

