# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class CSWStorageService(models.Model):
    _name = 'csw.storage.service'
    _inherit = ['mail.thread']
    _description = 'Could Storage Service'

    name = fields.Char(
        string="CS Service No.", default='/', copy=False, index=True,
        readonly=True)
    partner_id = fields.Many2one(
        'res.partner', string='Customer', domain="[('customer', '=', True)]")
    transport_type = fields.Selection([
        ('own', 'Own'),
        ('other', 'Others')],
        string='Transport Type')
    truck_id = fields.Many2one(
        'csw.truck', string='Truck', required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    license_number = fields.Char(
        'Truck License Number', related='truck_id.license_number',
        readonly=True)
    origin_document = fields.Selection([
        ('waybill', 'Way Bills'),
        ('reception', 'WH Product Reception'),
        ('delivery', 'WH Product Delivery')],
        string='Origin Document Is', required=True)
    way_bill_ids = fields.One2many(
        'csw.way.bill', 'storage_service_id', string='Way bills',
        # domain="[('state', '=', 'confirm'), ('partner_id', '=', partner_id)]" # TODO da bateo el domain
    )
    product_reception_ids = fields.One2many(
        'csw.product.reception', 'storage_service_id',
        string='Product Receptions',
        # domain="[('state', '=', 'confirm'), ('partner_id', '=', partner_id)]" # TODO da bateo el domain
    )
    product_delivery_ids = fields.One2many(
        'csw.product.delivery', 'storage_service_id',
        string='Product Deliveries',
        # domain="[('state', '=', 'confirm'), ('partner_id', '=', partner_id)]" # TODO da bateo el domain
    )
    date = fields.Datetime(
        string='Date', default=fields.Datetime.now, required=True,
        readonly=True, states={'draft': [('readonly', False)]})
    storage_type_id = fields.Many2one(
        'csw.storage.type', string='Cold Storage Type', readonly=True,
        states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('start', 'Started'),
        ('progress', 'In Progress'),
        ('complete', 'Completed'),
        ('cancel', 'Cancelled')],
        string='Status', default='draft', readonly=True, required=True,
        copy=False)
    line_ids = fields.One2many(
        'csw.storage.service.line', 'storage_service_id',
        string='CS Service Lines')
    total_pallet_qty = fields.Integer(
        string="Total Pallets Qty", compute='_compute_total_pallet_qty')
    total_product_qty = fields.Float(
        string="Total Products Qty", compute='_compute_total_product_qty')
    user_id = fields.Many2one(
        'res.users', 'Responsible', default=lambda self: self._uid,
        readonly=False, states={'finish': [('readonly', True)],
                                'cancel': [('readonly', True)]})
    service_type_id = fields.Many2one(
        'csw.service.type', string='Service Type')
    invoicing_policy = fields.Selection(
        related='service_type_id.invoicing_policy', readonly=True)
    price_unit = fields.Float(
        string='Unit Price', digits=dp.get_precision('Product Price'))
    pallet_qty = fields.Float(string='Qty. Pallets to Apply Service')
    service_qty = fields.Float(string='Services Qty. / Pallet')
    date_invoiced = fields.Date(
        string='Invoiced Date', readonly=True,
        states={'draft': [('readonly', False)]}, copy=False)
    invoice_id = fields.Many2one(
        'account.invoice', string='Invoice Reference', index=True)
    date_invoice = fields.Date(
        string='Invoice Date', related='invoice_id.date_invoice',
        readonly=True)
    notes = fields.Text(string="Comment")
    way_bill_id = fields.Many2one(
        'csw.way.bill', string='Way Bill', required=True, ondelete='cascade',
        help='Way Bill this CS Service was generated from')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'CS Service No. must be unique!'),
    ]

    @api.multi
    def _compute_total_pallet_qty(self):
        for way_bill in self:
            lines = way_bill.line_ids.filtered(lambda x: x.customer_pallet_no)
            way_bill.total_pallet_qty = len(lines)

    @api.multi
    def _compute_total_product_qty(self):
        for way_bill in self:
            way_bill.total_product_qty = sum(
                line.product_qty for line in way_bill.line_ids)

    @api.multi
    def action_confirm(self):
        self.filtered(lambda way_bill: way_bill.state == 'draft').write(
            {'state': 'confirm', 'kanban_state': '2confirm'})
        return True
    #
    # @api.multi
    # def action_entry_weight(self):
    #     self.ensure_one()
    #     view = self.env.ref('csw.view_csw_bill_weight')
    #     wiz = self.env['csw.bill.weight'].create({
    #         'way_bill_id': self.id,
    #         'action': 'entry'
    #     })
    #     return {
    #         'name': _('Entry Weight'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'csw.bill.weight',
    #         'views': [(view.id, 'form')],
    #         'view_id': view.id,
    #         'target': 'new',
    #         'res_id': wiz.id,
    #         'context': self.env.context,
    #     }
    #
    # @api.multi
    # def action_assign_dock(self):
    #     if self.filtered(lambda way_bill: way_bill.state != 'confirm' or
    #             not way_bill.entry_weight_exists):
    #         raise UserError(
    #             _('Please check if the Way Bill is set to Confirmed state and'
    #               ' if exists an Entry Weight operation for the truck.'))
    #     if self.filtered(lambda way_bill: not way_bill.dock_id):
    #         raise UserError(_('Please enter assigned Dock No.'))
    #     self.write({'state': 'product_move'})
    #
    # @api.multi
    # def action_exit_weight(self):
    #     self.ensure_one()
    #     view = self.env.ref('csw.view_csw_bill_weight')
    #     wiz = self.env['csw.bill.weight'].create({
    #         'way_bill_id': self.id,
    #         'action': 'exit'
    #     })
    #     return {
    #         'name': _('Exit Weight'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'csw.bill.weight',
    #         'views': [(view.id, 'form')],
    #         'view_id': view.id,
    #         'target': 'new',
    #         'res_id': wiz.id,
    #         'context': self.env.context,
    #     }
    #
    # @api.multi
    # def action_cancel(self):
    #     self.ensure_one()
    #     if self.env['csw.truck.operation'].search_count(
    #             [('way_bill_id', '=', self.id),
    #              ('truck_id', '=', self.truck_id.id),
    #              ('action', '=', 'entry')]) > 0:
    #         raise UserError(_(
    #             'You cannot cancel a way bill having already an Entry Weight'
    #             ' operation'))
    #     view = self.env.ref('csw.view_csw_bill_cancellation')
    #     wiz = self.env['csw.bill.cancellation'].create(
    #         {'way_bill_id': self.id})
    #     return {
    #         'name': _('Way Bill Cancellation'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'csw.bill.cancellation',
    #         'views': [(view.id, 'form')],
    #         'view_id': view.id,
    #         'target': 'new',
    #         'res_id': wiz.id,
    #         'context': self.env.context,
    #     }

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'csw.storage.service') or '/'
        return super(CSWStorageService, self).create(vals)

    @api.multi
    def unlink(self):
        if any([service.state != 'draft' for service in self]):
            raise UserError(_('You can only delete services in Draft state'))
        return super(CSWStorageService, self).unlink()


class CSWStorageServiceLine(models.Model):
    _name = 'csw.storage.service.line'
    _inherit = ['mail.thread']
    _description = 'CS Service Line'

    storage_service_id = fields.Many2one(
        'csw.storage.service', string='CS Service', required=True)
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain="[('store_ok', '=', True), ('owner_id', '=', way_bill_id.partner_id)]",
        required=True)
    customer_pallet_no = fields.Char('Customer Pallet No.')
    package_id = fields.Many2one(
        'stock.quant.package', string='Our Pallet No.', required=True)
    pallet_type_id = fields.Many2one(
        'csw.pallet.type', string='Pallet Type',
        related='package_id.pallet_type_id', readonly=True)
    lot_number = fields.Char(string='Lot No.')
    product_qty = fields.Float('Product Qty p/Pallet', required=True)
    use_date = fields.Date('Best Before Date')

    @api.onchange('package_id')
    def _onchange_partner_id(self):
        self.lot_number = self.package_id.lot_id.name
