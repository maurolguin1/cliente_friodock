# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class CSWProductReception(models.Model):
    _name = 'csw.product.reception'
    _inherit = ['mail.thread']
    _description = 'WH Product Reception'

    @api.model
    def _default_location_id(self):
        location_id = self.env['ir.values'].get_default(
            'csw.config.settings', 'reception_location_id')
        return self.env['stock.location'].browse(location_id)

    @api.model
    def _default_picking_type(self):
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get(
            'company_id') or self.env.user.company_id.id
        types = type_obj.search(
            [('code', '=', 'incoming'),
             ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search(
                [('code', '=', 'incoming'), ('warehouse_id', '=', False)])
        return types[:1]

    name = fields.Char(
        string="Product Reception No.", default='/', copy=False, index=True,
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
        'stock.location', 'Origin Location', required=True,
        default=_default_location_id, readonly=True,
        states={'draft': [('readonly', False)]})
    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location', required=True, readonly=True,
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
        'csw.product.reception.line', 'product_reception_id',
        string='Product Reception Lines')
    total_pallet_qty = fields.Integer(
        string="Total Pallets Qty", compute='_compute_total_pallet_qty')
    total_product_qty = fields.Float(
        string="Total Products Qty", compute='_compute_total_product_qty')
    user_id = fields.Many2one(
        'res.users', 'Responsible', default=lambda self: self._uid,
        readonly=True, states={'draft': [('readonly', False)]})
    service_type_id = fields.Many2one(
        'csw.service.type', string='Service Type')
    notes = fields.Text(string="Comment")
    company_id = fields.Many2one(
        'res.company', 'Company', required=True, index=True,
        readonly=True, states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get(
            'csw.product.reception'))
    # auxiliary fields
    available_package_ids = fields.Many2many(
        'stock.quant.package', string='Available Packages',
        compute='_compute_available_package_ids')
    picking_ids = fields.One2many(
        'stock.picking', 'product_reception_id', string='Receipts')
    way_bill_count = fields.Integer(
        compute='_compute_way_bill_count', string="Number of Way Bills")
    picking_count = fields.Integer(
        compute='_compute_picking_count', string="Number of Receipts")
    start_time_is_set = fields.Boolean(
        help="Technical field used just to check if start time is set")
    end_time_is_set = fields.Boolean(
        help="Technical field used just to check if end time is set")
    # truck_operation_ids = fields.One2many(
    #     'csw.truck.operation', 'way_bill_id', string='Truck Operations')
    # entry_weight_exists = fields.Boolean(
    #     compute='_compute_entry_weight_exists')
    # exit_weight_exists = fields.Boolean(
    #     compute='_compute_exit_weight_exists')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Product Reception No. must be unique!'),
    ]

    @api.multi
    def _compute_total_pallet_qty(self):
        reception_line_obj = self.env['csw.product.reception.line']
        for reception in self:
            packages = reception_line_obj.read_group(
                [('id', 'in',
                  reception.line_ids.filtered(lambda x: x.package_id).ids)],
                ['package_id'], ['package_id'])
            reception.total_pallet_qty = len(packages)

    @api.multi
    def _compute_total_product_qty(self):
        for reception in self:
            reception.total_product_qty = sum(
                line.product_qty for line in reception.line_ids)

    @api.multi
    def _compute_available_package_ids(self):
        for reception in self:
            reception.available_package_ids = [
                wbl.package_id.id for wbl in
                reception.way_bill_id.line_ids]

    @api.multi
    @api.depends('way_bill_id')
    def _compute_way_bill_count(self):
        for reception in self:
            reception.way_bill_count = 1 if self.way_bill_id else 0

    @api.multi
    @api.depends('picking_ids')
    def _compute_picking_count(self):
        for reception in self:
            reception.picking_count = len(reception.picking_ids)

    @api.multi
    def open_way_bill(self):
        self.ensure_one()
        action = {
            'name': _('Way Bill'),
            'view_type': 'form',
            'view_mode': 'tree,form,calendar',
            'res_model': 'csw.way.bill',
            'type': 'ir.actions.act_window',
            'domain': [('id', '=', self.way_bill_id.id)],
        }
        if self.way_bill_id:
            action['view_mode'] = 'form'
            action['res_id'] = self.way_bill_id.id
        return action

    @api.multi
    def open_stock_picking(self):
        self.ensure_one()
        action = {
            'name': _('Receipts'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.picking_ids.ids)],
        }
        if len(self.picking_ids) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = self.picking_ids[0].id
        return action

    @api.multi
    def set_start_time(self):
        today = fields.Datetime.from_string(fields.Datetime.now())
        self.write({
            'start_time': self._time_to_float(today),
            'start_time_is_set': True
        })

    @api.multi
    def set_end_time(self):
        today = fields.Datetime.from_string(fields.Datetime.now())
        self.write({
            'end_time': self._time_to_float(today),
            'end_time_is_set': True
        })

    def _time_to_float(self, time):
        hour = float(time.strftime('%H'))
        minute = float(time.strftime('%M'))
        return hour + (minute / 60)

    @api.multi
    def action_confirm(self):
        for reception in self:
            reception._check_conditions_before_confirm()
            reception.way_bill_id.action_exit_control()
        pickings = self._create_pickings()
        pickings.do_new_transfer()
        self.line_ids.action_confirm()
        self.write({'state': 'confirm'})
        return True

    def _check_conditions_before_confirm(self):
        self.ensure_one()
        if self.partner_id.id != self.way_bill_id.partner_id.id:
            raise UserError(_(
                'Customer should be the same in the WH Product Reception and'
                ' in the Way Bill: %s') % self.way_bill_id.name)
        if self.truck_id.id != self.way_bill_id.truck_id.id:
            raise UserError(_(
                'Truck should be the same in the WH Product Reception and'
                ' in the Way Bill: %s') % self.way_bill_id.name)
        if self.total_pallet_qty != self.way_bill_id.total_pallet_qty:
            raise UserError(_(
                "Value of field 'Total Pallets Qty' should be the same in the"
                " WH Product Reception and in the Way Bill: %s")
                            % self.way_bill_id.name)

        reception_lines = self.env['csw.product.reception.line'].read_group(
            [('id', 'in', self.line_ids.filtered(lambda x: x.product_id).ids)],
            ['product_id', 'product_qty'], ['product_id'])
        for reception_line in reception_lines:
            way_bill_total = self.way_bill_id.get_product_qty_per_product(
                reception_line['product_id'][0])
            if way_bill_total != reception_line['product_qty']:
                raise UserError(_(
                    "Total Product Qty of product %s should be same in the"
                    " WH Product Reception and in the Way Bill: %s. Current"
                    " values are %s and %s respectively.") % (
                                    reception_line['product_id'][1],
                                    self.way_bill_id.name,
                                    reception_line['product_qty'],
                                    way_bill_total))

    @api.model
    def _prepare_picking(self):
        return {
            'product_reception_id': self.id,
            'picking_type_id': self._default_picking_type().id,
            'partner_id': self.partner_id.id,
            'date': self.date,
            'origin': self.name,
            'location_dest_id': self.location_dest_id.id,
            'location_id': self.location_id.id,
            'company_id': self.company_id.id,
        }

    @api.multi
    def _create_pickings(self):
        StockPicking = self.env['stock.picking']
        pickings = StockPicking.browse()
        for reception in self:
            if any([ptype in ['product', 'consu'] for ptype in
                    reception.line_ids.mapped('product_id.type')]):
                picking = StockPicking.create(reception._prepare_picking())
                moves = reception.line_ids._create_stock_moves(picking)
                moves = moves.filtered(lambda x: x.state not in (
                    'done', 'cancel')).action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date_expected):
                    seq += 5
                    move.sequence = seq
                moves.force_assign()
                picking.message_post_with_view(
                    'mail.message_origin_link', values={
                        'self': picking, 'origin': reception},
                    subtype_id=self.env.ref('mail.mt_note').id)
                # set qty done in operations and put them in packs
                picking.set_quantities_done()
                pickings |= picking
        return pickings

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'csw.product.reception') or '/'
        return super(CSWProductReception, self).create(vals)

    @api.multi
    def unlink(self):
        raise UserError(_(
            'You cannot delete a WH Product Movement once it was generated'
            ' from a Way Bill record'))


class CSWProductReceptionLine(models.Model):
    _name = 'csw.product.reception.line'
    _description = 'Product Reception Line'

    product_reception_id = fields.Many2one(
        'csw.product.reception', string='WH Product Reception', required=True)
    product_id = fields.Many2one(
        'product.product', string='Product',
        # domain="[('store_ok', '=', True), ('owner_id', '=', product_reception_id.partner_id)]",
        required=True)
    description_sale = fields.Text(
        related='product_id.description_sale', readonly=True)
    customer_pallet_no = fields.Char('Customer Pallet No.')
    package_id = fields.Many2one(
        'stock.quant.package', string='Our Pallet No.', required=True)
    pallet_type_id = fields.Many2one(
        'csw.pallet.type', string='Pallet Type')
    product_qty = fields.Float('Product Qty', required=True)
    product_uom = fields.Many2one(
        'product.uom', 'Unit of Measure', required=True)
    temperature = fields.Float(string='Real Temperature˚C')
    avg_temperature = fields.Float(string='Average Temperature˚C')
    lot_number = fields.Char(string='Lot No.')
    create_date = fields.Datetime('Creation Date')
    use_date = fields.Date('Best Before Date')

    @api.multi
    def action_confirm(self):
        for line in self:
            line.package_id.write({
                'product_reception_id': line.product_reception_id.id})
        return True

    @api.multi
    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one WH product reception line.
        Returns a list of dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        return {
            # 'name': self.name or '',
            'name': self.product_id.name,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'product_uom_qty': self.product_qty,
            'date': self.product_reception_id.date,
            # 'date_expected': self.date_planned,
            'date_expected': self.product_reception_id.date,
            'location_id': self.product_reception_id.location_id.id,
            'location_dest_id': self.product_reception_id.location_dest_id.id,
            'picking_id': picking.id,
            # 'partner_id': self.product_reception_id.partner_id.id,
            'move_dest_id': False,
            'state': 'draft',
            # 'purchase_line_id': self.id,
            'company_id': self.product_reception_id.company_id.id,
            # 'price_unit': price_unit,
            'picking_type_id': picking.picking_type_id.id,
            # 'group_id': self.order_id.group_id.id,
            'procurement_id': False,
            'origin': self.product_reception_id.name,
            'route_ids': picking.picking_type_id.warehouse_id and [
                (6, 0, [x.id for x in
                        picking.picking_type_id.warehouse_id.route_ids])]
                         or [],
            'warehouse_id': picking.picking_type_id.warehouse_id.id,
        }

    @api.multi
    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            done += moves.create(line._prepare_stock_moves(picking))
        return done

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.pallet_type_id = self.product_id.pallet_type_id
        self.product_uom = self.product_id.uom_id.id
        return {'domain': {'product_uom': [
            ('category_id', '=', self.product_id.uom_id.category_id.id)]}}

    @api.onchange('pallet_type_id')
    def _onchange_pallet_type_id(self):
        self.product_qty = self.pallet_type_id.product_qty
