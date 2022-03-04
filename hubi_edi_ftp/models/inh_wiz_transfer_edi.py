# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
   
class HubiWizTransferEDI(models.TransientModel):
    _inherit = "wiz.edi.ftp"
 
    def di_ligne_fac_par(self, invoices_id, ligne, ean_cd_par, nom_cd_par, ean_cd_a, nom_cd_a, ean_liv, nom_liv, ean_fac, nom_fac, ean_regle, nom_regle, ean_factor, nom_factor):
        if invoices_id.partner_id.di_sender_establishment.di_code_ean:
           ean_cd_a =  invoices_id.partner_id.di_sender_establishment.di_code_ean
           nom_cd_a =  invoices_id.partner_id.di_sender_establishment.name
        
        res = super(HubiWizTransferEDI, self).di_ligne_fac_par(invoices_id, ligne, ean_cd_par, nom_cd_par, ean_cd_a, nom_cd_a, ean_liv, nom_liv, ean_fac, nom_fac, ean_regle, nom_regle, ean_factor, nom_factor)
        return res