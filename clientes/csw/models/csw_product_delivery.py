# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class CSWProductDelivery(models.Model):
    _name = 'csw.product.delivery'
    _inherit = ['mail.thread']
    _description = 'WH Product Delivery'

    name = fields.Char(
        string="Product Delivery No.", default='/', copy=False, index=True,
        readonly=True)
    way_bill_id = fields.Many2one(
        'csw.way.bill', string='Way Bill No.', required=True)
    partner_id = fields.Many2one(
        'res.partner', string='Customer', domain="[('customer', '=', True)]",
        readonly=True)
    transport_type = fields.Selection([
        ('own', 'Own'),
        ('other', 'Others')],
        string='Transport Type',
        readonly=True)
    truck_id = fields.Many2one(
        'csw.truck', string='Truck', required=True, readonly=True)
    license_number = fields.Char(
        'Truck License Number', related='truck_id.license_number',
        readonly=True)
    trailer_number = fields.Char('Trailer Number', readonly=True)
    driver_id = fields.Many2one(
        'csw.driver', string='Driver', required=True, readonly=True)
    weight_entry = fields.Float(
        string='Entry Weight (Kg)', digits=(16, 2))
    weight_exit = fields.Float(
        string='Exit Weight (Kg)', digits=(16, 2))
    date = fields.Datetime(
        string='Date', default=fields.Datetime.now, required=True,
        readonly=True, states={'draft': [('readonly', False)]})
    start_time = fields.Float()
    end_time = fields.Float()
    storage_type_id = fields.Many2one(
        'csw.storage.type', string='Cold Storage Type', readonly=True,
        states={'draft': [('readonly', False)]})
    delivery_number = fields.Char(
        'Customer Delivery Number', readonly=True,
        states={'draft': [('readonly', False)]})
    inspection_number = fields.Char(
        'Health Inspection No.', readonly=True,
        states={'draft': [('readonly', False)]})
    seals_number = fields.Char(
        'Seals No.', readonly=True, states={'draft': [('readonly', False)]})
    senasa_number = fields.Char('SENASA Auth. Number')
    dock_id = fields.Many2one(
        'csw.dock', string='Dock Number', readonly=True,
        states={'draft': [('readonly', False)]})
    location_id = fields.Many2one(
        'stock.location', 'Origin Location', required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    product_market = fields.Selection([
        ('local', 'Product Local Market'),
        ('import', 'Imported Products'),
        ('export', 'Products for Exports')],
        string='Products Market')
    storage_service_id = fields.Many2one(
        'csw.storage.service', string='Could Storage Service')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed')],
        string='Status', default='draft', readonly=True, required=True,
        copy=False)
    line_ids = fields.One2many(
        'csw.product.delivery.line', 'product_delivery_id',
        string='Product Delivery Lines', readonly=True)
    total_pallet_qty = fields.Integer(
        string="Total Pallets Qty", compute='_compute_total_pallet_qty')
    total_product_qty = fields.Float(
        string="Total Products Qty", compute='_compute_total_product_qty')
    user_id = fields.Many2one(
        'res.users', 'Responsible', default=lambda self: self._uid,
        readonly=False, states={'finish': [('readonly', True)],
                                'cancel': [('readonly', True)]})
    notes = fields.Text(string="Comment")
    # auxiliary fields
    # truck_operation_ids = fields.One2many(
    #     'csw.truck.operation', 'way_bill_id', string='Truck Operations')
    # entry_weight_exists = fields.Boolean(
    #     compute='_compute_entry_weight_exists')
    # exit_weight_exists = fields.Boolean(
    #     compute='_compute_exit_weight_exists')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Product Delivery No. must be unique!'),
    ]

    @api.multi
    def _compute_total_pallet_qty(self):
        for delivery in self:
            lines = delivery.line_ids.filtered(lambda x: x.customer_pallet_no)
            delivery.total_pallet_qty = len(lines)

    @api.multi
    def _compute_total_product_qty(self):
        for delivery in self:
            delivery.total_product_qty = sum(
                line.product_qty for line in delivery.line_ids)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'csw.product.delivery') or '/'
        return super(CSWProductDelivery, self).create(vals)

    @api.multi
    def unlink(self):
        raise UserError(_(
            'You cannot delete a WH Product Movement once it was generated'
            ' from a Way Bill record'))


class CSWProductDeliveryLine(models.Model):
    _name = 'csw.product.delivery.line'
    _description = 'Product Delivery Line'

    product_delivery_id = fields.Many2one(
        'csw.product.delivery', string='WH Product Delivery', required=True)
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain="[('store_ok', '=', True), ('owner_id', '=', product_delivery_id.partner_id)]",
        required=True)
    customer_pallet_no = fields.Char('Customer Pallet No.')
    package_id = fields.Many2one(
        'stock.quant.package', string='Our Pallet No.', required=True)
    product_qty = fields.Float('Product Qty', required=True)
    temperature = fields.Float(string='Real Temperature˚C')
    avg_temperature = fields.Float(string='Average Temperature˚C')
    lot_number = fields.Char(string='Lot No.')
    create_date = fields.Datetime('Creation Date')
    use_date = fields.Date('Best Before Date')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.pallet_type_id = self.product_id.pallet_type_id

    @api.onchange('pallet_type_id')
    def _onchange_pallet_type_id(self):
        self.product_qty = self.pallet_type_id.product_qty
