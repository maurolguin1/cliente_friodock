# -*- coding: utf-8 -*-

from odoo import fields, models, api


class CSWConfigSettings(models.TransientModel):
    _name = 'csw.config.settings'
    _inherit = 'res.config.settings'

    reception_location_id = fields.Many2one(
        'stock.location', string='WH Reception Location – Origin',
        domain="[('usage', '=', 'customer')]")
    default_location_dest_id = fields.Many2one(
        'stock.location', string='WH Reception Location – Destination',
        domain="[('usage', '=', 'internal')]",
        default_model='csw.product.reception')
    default_location_id = fields.Many2one(
        'stock.location', string='WH Delivery Location – Origin',
        domain="[('usage', '=', 'internal')]",
        default_model='csw.product.delivery')
    delivery_location_dest_id = fields.Many2one(
        'stock.location', string='WH Delivery Location – Destination',
        domain="[('usage', '=', 'customer')]")

    @api.multi
    def set_reception_location_id_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'csw.config.settings', 'reception_location_id',
            self.reception_location_id.id)

    @api.multi
    def set_delivery_location_dest_id_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'csw.config.settings', 'delivery_location_dest_id',
            self.delivery_location_dest_id.id)
