# -*- coding: utf-8 -*-
 
import odoo.http as http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception,content_disposition#, CSVExport
    
class SaleOrderController(http.Controller):
    @http.route('/csv/download/sale_order/<int:order_id>/partner_name/<string:partner_name>', type='http', auth='user')
    def sale_order_lines_csv_download(self, order_id, partner_name, **kw):
        if partner_name:
            csv = http.request.env['sale.order']._csv_download({'order_id': order_id, 'partner_name':partner_name})
        else:
            csv = http.request.env['sale.order']._csv_download({'order_id': order_id, 'partner_name': False})
        filename = 'order_lines_%s_%s.csv'%(order_id,partner_name)
        
        return request.make_response(csv,
                                        [('Content-Type', 'text/csv'),
                                         ('Content-Disposition', 'attachment; filename="%s"'%(filename))])
        
        
	
    
    @http.route('/csv/', type='http', auth='user')
    def transfert_compta_csv_download(self, csv,filename):
        
       
        response = http.HttpRequest.make_response(csv,
                                        [('Content-Type', 'text/csv'),
                                         ('Content-Disposition',content_disposition(filename))])
        
        
        
        return response 