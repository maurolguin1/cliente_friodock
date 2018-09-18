# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    store_ok = fields.Boolean('Can be Store')
    owner_id = fields.Many2one(
        'res.partner', 'Owner by', domain="[('customer', '=', True)]",
        index=True)
    pallet_type_id = fields.Many2one('csw.pallet.type', string='Pallet Type')

    @api.one
    @api.constrains('type', 'store_ok')
    def _check_type(self):
        if self.type != 'product' and self.store_ok:
            raise ValidationError(_(
                'Error! Products with field Can be Store cheked, must be of'
                ' type Stockable Product.'))
