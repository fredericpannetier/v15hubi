# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
   
class HubiWizTracabilite(models.TransientModel):
    _name = "wiz.hubi.tracabilite"
    _description = "Wizard Hubi Traçabilité"
    
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company,  index=True, required=True)
    product_id = fields.Many2one('product.product', 'Product', check_company=True,
        domain="[('type', 'in', ['product']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", index=True, required=True)
    description_picking = fields.Char('Description of Picking')
    product_qty = fields.Float('Real Quantity',  help='Quantity in the default UoM of the product')
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure')

    qty_pack = fields.Float(string='Quantity of Packs')
    stock_packaging= fields.Many2one('di.multi.table', string='Stock Packaging', domain=[('record_type', '=', 'StockPackaging')], help="The Packaging of the stock.")
    
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', related='product_id.product_tmpl_id', readonly=False, help="Technical: used in views")
    location_id = fields.Many2one('stock.location', 'Source Location', auto_join=True, index=True, required=True,check_company=True,
        help="Sets a location if you produce at a fixed location.")
    location_dest_id = fields.Many2one('stock.location', 'Destination Location', auto_join=True, index=True, required=True, check_company=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot',
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]", check_company=True)
    lot_name = fields.Char('Lot/Serial Number Name')
  
    location_first = fields.Char('First Location')
    location_last = fields.Char('Last Location')
  
    product_id_scrap = fields.Many2one('product.product', 'Product : scrap', check_company=True,
        domain="[('type', 'in', ['product']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", index=True, required=True)

    location_id_scrap = fields.Many2one('stock.location', 'Location : scrap', auto_join=True, index=True, required=True,check_company=True)
    location_dest_id_scrap = fields.Many2one('stock.location', 'Location : scrap', 
                            domain="[('scrap_location', '=', True)]",
                            auto_join=True, index=True, required=True,check_company=True)
    lot_id_scrap = fields.Many2one('stock.production.lot', 'Lot : scrap',
        domain="[('product_id', '=', product_id_scrap), ('company_id', '=', company_id)]", check_company=True)
    product_qty_scrap = fields.Float('Quantity _scrap',  help='Quantity scrap in the default UoM of the product')
    
    line_ids = fields.One2many('wiz.hubi.tracabilite.line', 'tracabilite_id')
    
    type_picking = fields.Char('Type of Picking')
    picking_id = fields.Integer('Picking id')
    picking_type_id = fields.Integer('Picking type id')
    move_id = fields.Integer('Move id')
    
    @api.onchange('qty_pack', 'stock_packaging')
    def _calcul_qty(self):
        qty=0
        if (self.qty_pack != 0) and (self.stock_packaging.weight != 0):
            qty = self.qty_pack * self.stock_packaging.weight
            self.product_qty = qty
        

    def tracabilite_regrouping(self):
        res=""
        # Stock.picking : state = Done
        self.update_picking()
        
        # Update x OUTPut
        lines = self.env['stock.move'].search([('picking_id', '=', self.picking_id)])
        for move_out in lines:
            self.update_move_line_out(move_out)

        # IN
        lines = self.env['wiz.hubi.tracabilite'].search([('id', '=', self.id)])
        for line in lines:
            self.update_line_in(line)

        # Perte
        self.update_scrap()
        
        return res


    def tracabilite_calibration(self):
        res=""
 
        # Stock.picking : state = Done
        self.update_picking()
               
        # move out : state = done
        move_out = self.env['stock.move'].search([('id', '=', self.move_id), ('picking_id', '=', self.picking_id), ('company_id', '=', self.company_id.id)] , limit=1)
        self.update_move_line_out(move_out)
        
        
        # insert x Inputs
        #vals_list = []
        lines = self.env['wiz.hubi.tracabilite.line'].search([('id', 'in', self.line_ids.ids)])
        for line in lines:
            self.update_line_in(line)
                 
        # Perte
        self.update_scrap()
 
        return res
    
    
    
    def update_picking(self):
        # Stock.picking : state = Done
        picking = self.env['stock.picking'].search([('id', '=', self.picking_id)] , limit=1)
        picking.update({
                'state': 'done',
                'date_done': fields.Datetime.now(),
                'is_locked': True
                
                })
    
    def update_move_line_out(self, move_out):
            # insert stock_move_line Out
            move_line_out = self.env['stock.move.line'].search([('picking_id', '=', self.picking_id), ('move_id', '=', move_out.id), ('company_id', '=', move_out.company_id.id)] , limit=1)
            if not move_line_out.ids:
                # insert Out : stock_move_line
                move_line_out_vals = {
                    'picking_id': self.picking_id,
                    'move_id': move_out.id,
                    'company_id': move_out.company_id.id,
                    'date': fields.Datetime.now(),
                    'product_id': move_out.product_id.id,
                    'product_uom_id': move_out.product_id.uom_id.id,
                   
                    'product_uom_qty':  move_out.product_uom_qty,
                    'qty_done': '0',
                    'lot_id': move_out.di_lot_id.id,
                    'lot_name': move_out.di_lot_name,
                    'location_id': move_out.location_id.id,
                    'location_dest_id': move_out.location_id.id,
                  
                    }
                move_line_out = self.env['stock.move.line'].create(move_line_out_vals)
        
            # action = done
            move_out.update({
                'location_dest_id': move_out.location_id.id or False,
                'state': 'done',
                'is_done': True
                })
                
            move_line_out.update({
                'product_uom_qty': '0',
                'qty_done': move_out.product_uom_qty,
            })
                
            # stock.quant
            quant_out = self.env['stock.quant'].search([('product_id', '=',  move_out.product_id.id), ('location_id', '=', move_out.location_id.id), ('company_id', '=', move_out.company_id.id), ('lot_id', '=', move_out.di_lot_id.id)] , limit=1)
            if not quant_out.ids:
                # insert  : stock_quant
                quant_out_vals = {
                        'product_id': move_out.product_id.id,
                        'location_id': move_out.location_id.id,
                        'company_id': move_out.company_id.id,
                        'lot_id': move_out.di_lot_id.id,
                        'in_date': fields.Datetime.now(),
                        'quantity': move_out.product_uom_qty * (-1),
                }
                quant_out = self.env['stock.quant'].create(quant_out_vals)
            else:
                quantity = quant_out.quantity - move_out.product_uom_qty
                quant_out.update({
                        'quantity': quantity,
                })
        
        
    def update_line_in(self, line):
            move_in_vals = {
                    'name': _('IN:') + (line.product_id.name or ''),
                    'picking_id': self.picking_id,
                    'description_picking': (line.description_picking or ''),
                    'picking_type_id': self.picking_type_id,
                    'company_id': line.company_id.id,
                    'date': fields.Datetime.now(),
                    'product_id': line.product_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uom_qty': line.product_qty,
                    
                    'di_qty_pack': line.qty_pack or 0, 
                    'di_stock_packaging':line.stock_packaging.id or False,
                    'di_lot_id': line.lot_id.id,
                    'di_lot_name': line.lot_name,
                    'location_id': line.location_dest_id.id,
                    'location_dest_id': line.location_dest_id.id,
                    'di_location_first': line.location_first,
                    'di_location_last': line.location_last,
                    'state':'draft',
                    #'is_done':True,
                    'move_line_ids': [(0, 0, {
                    #    'date': fields.Datetime.now(),
                        'picking_id': self.picking_id,
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_id.uom_id.id,
                        'description_picking': line.description_picking or '',
                        'product_uom_qty': line.product_qty,
                        'qty_done': '0',
                        'lot_id': line.lot_id.id,
                        'lot_name': line.lot_name,
                        'location_id': line.location_dest_id.id,
                        'location_dest_id': line.location_dest_id.id,
                        
                    })]
                    
                    }
            move_in = self.env['stock.move'].create(move_in_vals)
            id_move_in = move_in.id
            
            # action = done
            move_in.update({
                'state': 'done',
                'is_done': True
                })
            
            move_line_in = self.env['stock.move.line'].search([('picking_id', '=', self.picking_id), ('move_id', '=', id_move_in), ('company_id', '=', self.company_id.id)] , limit=1)
            move_line_in.update({
                'product_uom_qty': '0',
                'qty_done': line.product_qty,
                })
            

            # stock.quant
            quant_in = self.env['stock.quant'].search([('product_id', '=',  line.product_id.id), ('location_id', '=', line.location_dest_id.id), ('company_id', '=', self.company_id.id), ('lot_id', '=', line.lot_id.id)] , limit=1)
            if not quant_in.ids:
                quant_in_vals = {
                    'product_id': line.product_id.id,
                    'location_id': line.location_dest_id.id,
                    'company_id': line.company_id.id,
                    'lot_id': line.lot_id.id,
                    'in_date': fields.Datetime.now(),
                    
                    'quantity': line.product_qty ,
                    }
                quant_in = self.env['stock.quant'].create(quant_in_vals)
            else:
                quantity = quant_in.quantity + line.product_qty
                quant_in.update({
                    'quantity': quantity,
                    })

    def update_scrap(self):
        _origin = self.env['stock.picking'].search([('id', '=', self.picking_id)] , limit=1).name
        
        move_in_vals = {
                    'name': _('Scrap:') + (self.product_id_scrap.name or ''),
                    'picking_id': self.picking_id,
                    'origin': _origin,
                    'description_picking':  _('Scrap:') + (self.product_id_scrap.name or ''),
                    #'picking_type_id': self.picking_type_id,
                    'company_id': self.company_id.id,
                    'date': fields.Datetime.now(),
                    'product_id': self.product_id_scrap.id,
                    'product_uom': self.product_id_scrap.uom_id.id,
                    'product_uom_qty': self.product_qty_scrap,
                    
                    'di_qty_pack':  0, 
                    'di_stock_packaging': False,
                    'di_lot_id': self.lot_id_scrap.id,
                    'di_lot_name': '',
                    'location_id': self.location_id_scrap.id,
                    'location_dest_id': self.location_dest_id_scrap.id,
                    'di_location_first': '',
                    'di_location_last': '',
                    'state':'draft',
                    #'is_done':True,
                    'move_line_ids': [(0, 0, {
                    #    'date': fields.Datetime.now(),
                        #'picking_id': self.picking_id,
                        'product_id': self.product_id_scrap.id,
                        'product_uom_id': self.product_id_scrap.uom_id.id,
                        'description_picking': _('Scrap:') + (self.product_id_scrap.name or ''),
                        'product_uom_qty': self.product_qty_scrap,
                        'qty_done': '0',
                        'lot_id': self.lot_id_scrap.id,
                        'lot_name': '',
                        'location_id': self.location_id_scrap.id,
                        'location_dest_id': self.location_dest_id_scrap.id,
                        
                    })]
                    
                    }
        move_in = self.env['stock.move'].create(move_in_vals)
        id_move_in = move_in.id
            
     
        # stock.quant : OUT from location_id_scrap
        """
        _location = self.env['stock.picking'].search([('id', '=', self.picking_id)] , limit=1).location_id.id
        quant_out = self.env['stock.quant'].search([('product_id', '=',  self.product_id_scrap.id), ('location_id', '=', _location), ('company_id', '=', self.company_id.id), ('lot_id', '=', self.lot_id_scrap.id)] , limit=1)
        if quant_out.ids:
            quantity = quant_out.quantity - self.product_qty_scrap
            quant_out.update({
                'quantity': quantity,
            })
            
        quant_out = self.env['stock.quant'].search([('product_id', '=',  self.product_id_scrap.id), ('location_id', '=', self.location_id_scrap.id), ('company_id', '=', self.company_id.id), ('lot_id', '=', self.lot_id_scrap.id)] , limit=1)
        if not quant_out.ids:
            # insert  : stock_quant
            quant_out_vals = {
                'product_id': self.product_id_scrap.id,
                'location_id': self.location_id_scrap.id,
                'company_id': self.company_id.id,
                'lot_id': self.lot_id_scrap.id,
                'in_date': fields.Datetime.now(),
                'quantity': self.product_qty_scrap * (-1),
            }
            quant_out = self.env['stock.quant'].create(quant_out_vals)
        else:
            quantity = quant_out.quantity - self.product_qty_scrap
            quant_out.update({
                'quantity': quantity,
            })
           
        # stock.quant : IN from location_id_scrap
        quant_out = self.env['stock.quant'].search([('product_id', '=',  self.product_id_scrap.id), ('location_id', '=', self.location_dest_id_scrap.id), ('company_id', '=', self.company_id.id), ('lot_id', '=', self.lot_id_scrap.id)] , limit=1)
        if not quant_out.ids:
            # insert  : stock_quant
            quant_out_vals = {
                'product_id': self.product_id_scrap.id,
                'location_id': self.location_dest_id_scrap.id,
                'company_id': self.company_id.id,
                'lot_id': self.lot_id_scrap.id,
                'in_date': fields.Datetime.now(),
                'quantity': self.product_qty_scrap ,
            }
            quant_out = self.env['stock.quant'].create(quant_out_vals)
        else:
            quantity = quant_out.quantity + self.product_qty_scrap
            quant_out.update({
                'quantity': quantity,
            })    
        """
         
        # stock.scrap
        scrap = self.env['stock.scrap'].search([('product_id', '=',  self.product_id_scrap.id), ('location_id', '=', self.location_dest_id_scrap.id), ('company_id', '=', self.company_id.id), ('lot_id', '=', self.lot_id_scrap.id)] , limit=1)
        if not scrap.ids:
            # insert  : stock_quant
            scrap_vals = {
                'company_id': self.company_id.id,
                'product_id': self.product_id_scrap.id,
                'product_uom_id': self.product_id_scrap.uom_id.id,
                'lot_id': self.lot_id_scrap.id,
                'move_id': id_move_in,
                'picking_id': self.picking_id,
                
                'location_id': self.location_id_scrap.id,
                'scrap_location_id': self.location_dest_id_scrap.id,
                'scrap_qty': self.product_qty_scrap ,
                'state': 'done',
                'date_done': fields.Datetime.now(),
                
            }
            scrap = self.env['stock.scrap'].create(scrap_vals)
        else:
            quantity = scrap.scrap_qty + self.product_qty_scrap
            scrap.update({
                'scrap_qty': quantity,
            })  
                        
        # action = done
        move_in.update({
                'state': 'done',
                'is_done': True
                })
            
        move_line_in = self.env['stock.move.line'].search([('move_id', '=', id_move_in), ('company_id', '=', self.company_id.id)] , limit=1)
        move_line_in.update({
                'product_uom_qty': '0',
                'qty_done': self.product_qty_scrap,
                })
       
    
class HubiWizTracabiliteLine(models.TransientModel):
    _name = "wiz.hubi.tracabilite.line"
    _description = "Wizard Hubi Traçabilité Lignes"


    
    def _calcul(self):
        qty=0
        return qty

    company_id = fields.Many2one('res.company', 'Company',  related='tracabilite_id.company_id', readonly=False)
    product_id = fields.Many2one('product.product', 'Product', check_company=True,
        domain="[('type', 'in', ['product']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", index=True, required=True)
    description_picking = fields.Char('Description of Picking')
    product_qty = fields.Float('Real Quantity',  help='Quantity in the default UoM of the product')
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure')
    qty_pack = fields.Float(string='Quantity of Packs')
    stock_packaging= fields.Many2one('di.multi.table', string='Stock Packaging', domain=[('record_type', '=', 'StockPackaging')], help="The Packaging of the stock.")

    product_tmpl_id = fields.Many2one('product.template', 'Product Template', related='product_id.product_tmpl_id', readonly=False, help="Technical: used in views")
    location_id = fields.Many2one('stock.location', 'Source Location', auto_join=True, index=True,check_company=True,
        help="Sets a location if you produce at a fixed location.")
    location_dest_id = fields.Many2one('stock.location', 'Destination Location', auto_join=True, index=True, required=True, check_company=True,
        help="Location where the system will stock the finished products.")
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number',
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]", check_company=True)
    lot_name = fields.Char('Lot/Serial Number Name')
    
    location_first = fields.Char('First Location')
    location_last = fields.Char('Last Location')

    tracabilite_id = fields.Many2one('wiz.hubi.tracabilite', 'Traceability', check_company=True, index=True)
  
    @api.onchange('qty_pack', 'stock_packaging')
    def _calcul_qty(self):
        qty=0
        if (self.qty_pack != 0) and (self.stock_packaging.weight != 0):
            qty = self.qty_pack * self.stock_packaging.weight
            self.product_qty = qty    
            
    @api.onchange('product_id')
    def _calcul_lot(self):

        if self.product_id :
            stock_lot = self.tracabilite_id.lot_id.id
            stock_lot_name = self.tracabilite_id.lot_id.name 
            
            new_lot = stock_lot 
            new_name = ""
            
            #moves_lots = self.lot_id.filtered(lambda lot: lot.name  in stock_lot_name).mapped('name')
            moves_lots = self.env['stock.production.lot'].search([('name', '>=', stock_lot_name), ('name', '<=', stock_lot_name + "-9999")]).mapped('name')
            lot_name = max(moves_lots, default= stock_lot_name) 
            
            x=lot_name.find('-')
            if x != -1:
                y = lot_name[x+1:]
                if y.isnumeric():
                    y = int(y) + 1
                    new_name = lot_name[:x] + "-" +  '{0:02d}'.format(y)    # str(y)
                else:
                    new_name = lot_name + "-01"    
            else:
                new_name = lot_name + "-01"
             
                   
            lots = self.env['stock.production.lot'].search([('name', 'ilike', new_name)])
            if not lots.ids:
                lots_vals = {
                    'name': new_name,
                    'product_id': self.product_id.id,
                    'product_uom_id': self.product_id.uom_id.id,
                    'company_id': self.product_id.company_id.id,
                    
                    }
                lots = self.env['stock.production.lot'].create(lots_vals)  
            new_lot = lots.id
                                
            self.lot_id = new_lot
            
            #self.lot_name = new_name      