# -*- coding: utf-8 -*-

from odoo import fields, api, models, _


class QuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    name = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code('stock.quant.package.csw') or _('Unknown Pack'))
    partner_id = fields.Many2one(
        'res.partner', string='Customer Ownership',
        domain="[('customer', '=', True)]", readonly=True)
    pallet_type_id = fields.Many2one(
        'csw.pallet.type', string='Pallet Type', readonly=True)
    storage_type_id = fields.Many2one(
        'csw.storage.type', string='Cold Storage Type', readonly=True)
    current_location_id = fields.Many2one('stock.location', 'Current Location')
    customer_pallet_no = fields.Char('Customer Pallet No.', readonly=True)
    lot_id = fields.Many2one(
        'stock.production.lot', 'Pallet Lot No.', compute='_compute_lot_id')
    use_date = fields.Date(
        string='Pallet Expiry Date', compute='_compute_use_date')
    product_market = fields.Selection([
        ('local', 'Product Local Market'),
        ('import', 'Imported Products'),
        ('export', 'Products for Exports')],
        string='Products Market', readonly=True)
    service_type_id = fields.Many2one(
        'csw.service.type', related='pallet_type_id.service_type_id',
        readonly=True)
    current_location_id = fields.Many2one('stock.location', 'Current Location')
    product_reception_id = fields.Many2one(
        'csw.product.reception', string='WH Product Reception', readonly=True)
    product_delivery_id = fields.Many2one(
        'csw.product.delivery', string='WH Product Delivery', readonly=True)
    # details & controls fields
    temp_reception = fields.Float(
        string='Real Temp.˚C(Reception)', readonly=True)
    avg_temp_reception = fields.Float(
        string='Avg Temp.˚C(Reception)', readonly=True)
    temp_delivery = fields.Float(
        string='Real Temp.˚C(Delivery)', readonly=True)
    avg_temp_delivery = fields.Float(
        string='Avg Temp.˚C(Delivery)', readonly=True)
    senasa_control = fields.Selection([
        ('not_certificate', 'Does not require a certificate'),
        ('domestic_product', 'Domestic Products Certification'),
        ('imported_product', 'Imported Products Certification')],
        string='Senasa Control')
    senasa_number = fields.Char('SENASA Auth. No.', readonly=True)
    fiscal_storage_type = fields.Selection([
        ('not_approval', 'Does not need approval'),
        ('need_approval', 'Needs approval for des-consolidation ')],
        string='Fiscal Storage Type', readonly=True)
    date_fiscal_approval = fields.Date(string='Fiscal Approval Date')
    fiscal_approval = fields.Boolean(string='Fiscal Approval')
    fiscal_approval_user_id = fields.Many2one(
        'res.users', string='Fiscal Approval User')
    inspection_number = fields.Char('Health Inspection No.', readonly=True)
    seals_number = fields.Char('Seals No.', readonly=True)
    date_consolidation = fields.Date(
        string='Pallet Consolidation Date', readonly=True)
    date_de_consolidation = fields.Date(
        string='Pallet De-consolidation Date', readonly=True)
    # invoicing fields
    date_last_invoice = fields.Date(string='Last Invoice Date')
    date_stock_in = fields.Datetime(
        string='Stock In Date', related='product_reception_id.date',
        readonly=True)
    date_stock_out = fields.Datetime(
        string='Stock Out Date', related='product_delivery_id.date',
        readonly=True)
    days_stock = fields.Integer(
        string='Total Days in Stock', compute='_compute_days_stock')

    @api.multi
    def _compute_lot_id(self):
        for package in self:
            quants = package.quant_ids.filtered(
                lambda x: x.lot_id).sorted(key=lambda l: l.lot_id.use_date)
            package.lot_id = quants[0].lot_id.id if quants else False

    @api.multi
    def _compute_use_date(self):
        for package in self:
            quants = package.quant_ids.filtered(
                lambda x: x.lot_id).sorted(key=lambda l: l.lot_id.use_date)
            package.use_date = quants[0].lot_id.use_date if quants else False

    @api.multi
    def _compute_days_stock(self):
        for package in self:
            nb_of_days = False
            if package.date_stock_in and package.date_stock_out:
                day_from = fields.Datetime.from_string(package.date_stock_in)
                day_to = fields.Datetime.from_string(package.date_stock_out)
                nb_of_days = (day_to - day_from).days
            package.days_stock = nb_of_days

    @api.onchange('pallet_type_id')
    def _onchange_pallet_type(self):
        self.senasa_control = self.pallet_type_id.senasa_control
        self.fiscal_storage_type = self.pallet_type_id.fiscal_storage_type
