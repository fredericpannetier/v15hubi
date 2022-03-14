# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
   
class HubiTracabilitePicking(models.Model):
    _inherit = "stock.picking"
 
    def _default_di_picking_type(self, valeur): 
       
        retour = 0
        """
        default_location_src_id = 0
        warehouse_location_id = 0
        
        if self.company_id.id:
            company = self.company_id.id
        else:
            company = self._context.get('force_company', self.env.user.company_id.id)
        
        warehouse_id = self.env.user._get_default_warehouse_id()   
        warehouse_w = self.env['stock.warehouse'].search([('id','=', warehouse_id.id)])
        for warehouse in warehouse_w:
            if warehouse_location_id == 0:
                warehouse_location_id = warehouse.view_location_id.id
            if retour == 0:
                    retour = warehouse.int_type_id.id    
        """
        
        
        """
        location_w = self.env['stock.location'].search([('usage','=', valeur),('active','=', True),('company_id', '=',company),('location_id','=', warehouse_location_id)])
        for location in location_w:
            if default_location_src_id == 0:
                default_location_src_id = location.id   
        
        if default_location_src_id != 0: 
            check_type=self.env['stock.picking.type'].search([('code','=', valeur),('active','=', True),('company_id', '=',company),('default_location_src_id','=', default_location_src_id)])
            for check in check_type:
                if retour == 0:
                    retour = check.id
        """
                       
        return retour
    
    #di_default_picking_type_transf = fields.Integer("Default picking type transfer", default = lambda self: self._default_di_picking_type('internal'))
    ##di_default_picking_type_transf = fields.Integer("Default picking type transfer", compute = '_default_di_picking_type')
    ##di_default_picking_type_transf = fields.Integer("Default picking type transfer", compute=lambda self: self._default_di_picking_type('internal'))

    @api.onchange('location_id')
    def _change_location(self):
        qty=0
        if (self.location_id):
            self.location_dest_id = self.location_id


    def action_regrouping_calibration(self):
        type=21
        
        ctx = {
            'search_default_picking_type_id': 21,
            'default_picking_type_id': 21,
            'contact_display': 'partner_address',
            
        }
 
        ir_model_data = self.env['ir.model.data']
        try:
            tracabilite_regroup_form_id = ir_model_data.check_object_reference('hubi_tracabilite', 'view_tracabilite_form', True)[1]
            tracabilite_regroup_search_id = ir_model_data.check_object_reference('hubi_tracabilite', 'view_tracabilite_form', True)[1]
            
        except ValueError:
            tracabilite_regroup_form_id = False
            tracabilite_regroup_search_id = False
        
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            #'domain': [['categ_id', '=', self.id]],
            'res_model': 'wiz.hubi.tracabilite',
            #'src_model': 'product.category',
            'views': [(tracabilite_regroup_form_id, 'form')],
            'view_id': tracabilite_regroup_form_id,
            'target': 'new',
            'context': ctx
        }    

    def action_regrouping(self):
        location = False
        
        ctx = {
            'default_type_picking': 'Regrouping',
            'default_company_id':self.company_id.id,
            'default_picking_id':self.id,
            'default_picking_type_id':self.picking_type_id.id,

            'default_location_dest_id':self.location_dest_id.id,
            'default_location_id':self.location_id.id,
            'default_location_id_scrap':self.location_id.id,
            
        }

       #This function opens a window to regroup  products 
        ir_model_data = self.env['ir.model.data']
        try:
            tracabilite_regroup_form_id = ir_model_data.check_object_reference('hubi_tracabilite', 'wiz_tracabilite_step1', True)[1]
            
        except ValueError:
            tracabilite_regroup_form_id = False
            
        
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            #'domain': [['categ_id', '=', self.id]],
            'res_model': 'wiz.hubi.tracabilite',
            #'src_model': 'product.category',
            'views': [(tracabilite_regroup_form_id, 'form')],
            'view_id': tracabilite_regroup_form_id,
            'target': 'new',
            'context': ctx
        }    
       
        
    
    def action_calibration(self):
        lot = False
        prod = False
        qte = False
        qte_pack = False
        packaging = False
        move_id = False
        location_id = False
        location_dest_id = False
        description_picking = False
        location_first = False
        location_last = False
        
        if len(self.move_lines.ids) !=0:
            move_id = self.move_lines[0].id or False
            prod = self.move_lines[0].product_id[0].id or False
            qte = self.move_lines[0].product_uom_qty or 0
            description_picking = self.move_lines[0].description_picking or ''
            location_first = self.move_lines[0].di_location_first or ''
            location_last = self.move_lines[0].di_location_last or ''
            
            qte_pack = self.move_lines[0].di_qty_pack or 0
            if self.move_lines[0].di_stock_packaging:
                packaging = self.move_lines[0].di_stock_packaging[0].id or False
        
            if self.move_lines[0].di_lot_id:
                lot = self.move_lines[0].di_lot_id[0].id
                
            if self.move_lines[0].location_id:
                location_id = self.move_lines[0].location_id[0].id
            if self.move_lines[0].location_dest_id:
                location_dest_id = self.move_lines[0].location_dest_id[0].id
                
        ctx = {
            'default_type_picking': 'Calibration',
            'default_company_id':self.company_id.id,
            'default_picking_id':self.id,
            'default_picking_type_id':self.picking_type_id.id,
            'default_move_id':move_id or False,
            'default_product_id':prod or False,
            'default_lot_id':lot or False,
            'default_product_qty':qte or False,
            
            'default_qty_pack':qte_pack or False,
            'default_stock_packaging':packaging or False,
            
            'default_location_dest_id':location_dest_id,
            'default_location_id':location_id,
            'default_description_picking':description_picking,
            'default_location_first':location_first,
            'default_location_last':location_last,
            
            'default_product_id_scrap':prod  or False,
            'default_location_id_scrap':self.location_id.id,
            

            
        }

       #This function opens a window to regroup  products 
        ir_model_data = self.env['ir.model.data']
        try:
            tracabilite_regroup_form_id = ir_model_data.check_object_reference('hubi_tracabilite', 'wiz_tracabilite_step1', True)[1]
            
        except ValueError:
            tracabilite_regroup_form_id = False
            
        
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            #'domain': [['categ_id', '=', self.id]],
            'res_model': 'wiz.hubi.tracabilite',
            #'src_model': 'product.category',
            'views': [(tracabilite_regroup_form_id, 'form')],
            'view_id': tracabilite_regroup_form_id,
            'target': 'new',
            'context': ctx
        }    
      

            
   
 
