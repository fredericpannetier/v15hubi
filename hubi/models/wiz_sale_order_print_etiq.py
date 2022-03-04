from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
#from ..controllers import ctrl_print
from . import tools_hubi
import datetime

class wizard_sale_order_print_etiq(models.Model):
    _name = "wiz_sale_order_print_etiq"
    _description = "Wizard to create table in order to stock order line"
    
    sale_order_line_id = fields.Char(string="Line Id")
    sale_order_id = fields.Integer(string="Sale Order Id")
    sale_order_num = fields.Char(string="Piece")
    packaging_date = fields.Date(string="Packaging date")
    sending_date = fields.Date(string="Sending date")
    caption_etiq = fields.Char(string="Caption label")
    product_id = fields.Integer(string="Product ID")
    product_name = fields.Char(string="Product")
    caliber_name = fields.Char(string="Caliber")
    packaging_name = fields.Char(string="Packaging")
    code_barre = fields.Char(string="Bar Code")
    code_128 = fields.Char(string="Bar Code 128")
    qte = fields.Float(string="Quantity")
    pds = fields.Float(string="Weight")
    numlot = fields.Char(string="Batch number")
    nb_mini = fields.Float(string="Minimum number")
    partner_id = fields.Many2one("res.partner", string='Customer')
    etabexp_id = fields.Many2one("res.partner", string='Sender establishment')
    printer_id = fields.Many2one("di.printing.printer", string='Etiquette Printer', domain=[('isimpetiq', '=', True)])
    model_id = fields.Many2one("di.printing.etiqmodel", string='Etiquette Model')
    color_etiq = fields.Selection([("#FF00FF", "magenta"),("#0000FF", "blue"),
                                    ("#FFFF00", "yellow"),("#FF0000", "red"),
                                    ("#008000", "green"),("#D2691E", "brown"),
                                    ("#FFFFFF", "white"),("#CCCCCC", "grey"),
                                    ("#FFC0CB", "pink")], string='Color Etiq')
    carrier_id = fields.Integer(string="Carrier ID")
    date_dluo = fields.Date(string="DLUO Date")

    def action_view_sale_order_line_print_etiq(self):
        query = """SELECT id FROM wiz_sale_order_print_etiq"""
        self.env.cr.execute(query)
        order_line = [r[0] for r in self.env.cr.fetchall()]

        if len(order_line) >= 1:
            action = self.env.ref('hubi.action_wiz_sale_order_print_etiq_tree').read()[0]
            action['domain'] = [('id', 'in', order_line)]
        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action

    def update_wiz_table(self):
        line_id = getattr(self, '_origin', self)._ids[0]
        packaging_date = self.packaging_date
        sending_date = self.sending_date
        code_barre = self.code_barre
        qte = self.qte
        pds = self.pds
        nb_mini = self.nb_mini
        printer_id = self.printer_id.id
        model_id = self.model_id.id
        numlot = self.numlot

        req = """UPDATE wiz_sale_order_print_etiq SET 
                    packaging_date=%s,
                    sending_date=%s,
                    code_barre=%s,
                    qte=%s,
                    pds=%s,
                    nb_mini=%s,
                    numlot=%s """

        params = (packaging_date, sending_date, code_barre, qte, pds, nb_mini, numlot)

        if printer_id:
            req += ",printer_id=" + str(printer_id) + " "
            # params.__add__(printer_id)

        if model_id:
            req += ",model_id=" + str(model_id) + " "
            # params.__add__(model_id)

        req += "WHERE id='" + str(line_id) + "' "
        # params.__add__(line_id)

        self._cr.execute(req, params)
        self.env.cr.commit()

    @api.onchange('packaging_date', 'sending_date', 'code_barre', 'qte', 'pds', 'nb_mini', 'printer_id', 'model_id',
                  'numlot')
    def _onchange_order_line_print_etiq(self):
        self.update_wiz_table()

    #    @api.multi
    def load_order_line(self, origin):
        user = self.env.user.id
        self.delete_table_temp(user)

        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or self._ids or []

        self.env.cr.commit()
        params = [tuple(active_ids)]
        # FP20190318 Remplacement ???? sl.pds par case ...sl.pds / sl.qte end
        query1 = """SELECT o.id, o.name, ol.id as line_id, o.di_packaging_date, o.di_sending_date, ol.product_id, p.default_code, 
                        GREATEST(case when uom.category_id = 2 then 1.0 else ol.product_uom_qty end -
                        COALESCE((SELECT SUM(real_number_etiq) FROM di_printing_printing AS hprint WHERE ol.id = hprint.order_line), 0),0) as qte,
                        ol.di_weight, categ.name, cond.name, ol.di_no_lot, 
                        t.id, etab.id, t.di_etiq_printer, t.di_etiq_model_id, t.di_customer_color_etiq,
                        pt.di_quantity, pt.di_etiq_printer, pt.di_etiq_model, pt.di_product_color, p.barcode,
                        linepl.di_price_printer, linepl.di_etiq_model_id, linepl.di_price_color, linepl.di_price_ean13, o.carrier_id, ol.di_date_dluo
                        FROM sale_order o 
                        INNER JOIN sale_order_line ol ON o.id = ol.order_id
                        INNER JOIN product_product p ON ol.product_id = p.id
                        INNER JOIN res_partner t ON o.partner_id = t.id
                        LEFT JOIN res_partner etab ON t.di_sender_establishment = etab.id
                        INNER JOIN product_template pt ON p.product_tmpl_id = pt.id 
                        LEFT JOIN di_multi_table categ ON pt.di_caliber_id = categ.id
                        LEFT JOIN di_multi_table cond ON pt.di_packaging_id = cond.id 
                        LEFT JOIN ir_property prop ON (prop.res_id = concat('res.partner,', t.id) AND prop.value_reference like 'product.pricelist,_')
                        LEFT JOIN product_pricelist pricelist ON prop.value_reference = concat('product.pricelist,', pricelist.id)
                        LEFT JOIN product_pricelist_item linepl ON (pricelist.id = linepl.pricelist_id AND pt.id = linepl.product_tmpl_id)
                        LEFT JOIN uom_uom uom ON (ol.product_uom = uom.id)"""

        if origin == 'order':
            query2 = """ WHERE pt.di_etiquette = true AND o.id IN %s ORDER BY o.name """
        else:
            query2 = """ WHERE ol.id IN %s ORDER BY o.name """

        query = ''.join([query1, query2])

        self.env.cr.execute(query, tuple(params))
        list_orders_ids = []

        ids = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], \
                r[11], r[12], r[13], r[14], r[15], r[16], r[17], r[18], r[19], r[20], \
                r[21], r[22], r[23], r[24], r[25], r[26], r[27]) for r in self.env.cr.fetchall()]

        for order_id, order_num, sale_order_line_id, packaging_date, sending_date, product_id, product_code, qte, weight, calibre, cond, \
            lot, clientid, etabexpid, clientprinter, clientetiq, clientcolor, nbmini, prodprinter, prodetiq, prodcolor, \
            prodcodbar, priceprinter, priceetiq, pricecolor, pricecodbar, carrier, date_dluo in ids:
            # Imprimante
            if (priceprinter is not None and priceprinter != ""):
                printer = priceprinter
            else:
                if (prodprinter is not None and prodprinter != ""):
                    printer = prodprinter
                else:
                    if (clientprinter is not None and clientprinter != ""):
                        printer = clientprinter
                    else:
                        printer = None
            # Modèle Etiquette
            if (priceetiq is not None and priceetiq != ""):
                etiq = priceetiq
            else:
                if (clientetiq is not None and clientetiq != ""):
                    etiq = clientetiq
                else:
                    if (prodetiq is not None and prodetiq != ""):
                        etiq = prodetiq
                    else:
                        etiq = None
            # Couleur
            if (pricecolor is not None and pricecolor != ""):
                color = pricecolor
            else:
                if (prodcolor is not None and prodcolor != ""):
                    color = prodcolor
                else:
                    if (clientcolor is not None and clientcolor != ""):
                        color = clientcolor
                    else:
                        color = None
            # Code Barre
            if (pricecodbar is not None and pricecodbar != ""):
                codebarre = pricecodbar
            else:
                if (prodcodbar is not None and prodcodbar != ""):
                    codebarre = prodcodbar
                else:
                    codebarre = None

            # printer = None  etiq = None => Default Value
            if (printer is None or etiq is None):
                default_value = self.env['di.printing.parameter'].search([('name', '=ilike', 'DEFAULT')])
                for default in default_value:
                    if (printer is None):
                        printer = default.printer_id.id
                    if (etiq is None):
                        etiq = default.etiquette_model_id.id

            insert = {
                'sale_order_id': order_id,
                'sale_order_num': order_num,
                'sale_order_line_id': sale_order_line_id,
                'packaging_date': packaging_date,
                'sending_date': sending_date,
                'product_id': product_id,
                'product_name': product_code,
                'caliber_name': calibre,
                'packaging_name': cond,
                'nb_mini': nbmini,
                'code_barre': codebarre,
                'qte': qte,
                'pds': weight,
                'numlot': lot,
                'partner_id': clientid,
                'etabexp_id': etabexpid,
                'printer_id': printer,
                'model_id': etiq,
                'color_etiq': color,
                'carrier_id': carrier,
                'date_dluo': date_dluo,
            }
            prepare_print_etiq = self.env['wiz_sale_order_print_etiq'].create(insert)
            list_orders_ids.append(int(prepare_print_etiq.id))
            # list_orders_ids.append(int(prepare_print_etiq.sale_order_line_id))

        self.env.cr.commit()

        return list_orders_ids

    #    @api.multi
    def print_etiq_from_order(self):
        self.env.cr.commit()

        query_args = {'id_sale': self.sale_order_id}
        query = """SELECT id 
                    FROM wiz_sale_order_print_etiq 
                    WHERE qte<>0 AND model_id is not null"""

        self.env.cr.execute(query, query_args)
        ids = [(r[0]) for r in self.env.cr.fetchall()]

        for id in ids:
            self.print_line(id)

        return self.ids

    def print_line(self, id):
        nom_table = "wiz_sale_order_print_etiq"
        tools_hubi.prepareprintetiq(self, nom_table, id)
        # return {'type': 'ir.actions.act_window_close'}

    #    @api.multi
    def delete_table_temp(self, user):
        query = "DELETE FROM wiz_sale_order_print_etiq WHERE create_uid=" + str(user)
        self.env.cr.execute(query)