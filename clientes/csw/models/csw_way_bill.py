# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class CSWDriver(models.Model):
    _name = 'csw.driver'
    _inherit = ['mail.thread']
    _description = 'Driver'

    name = fields.Char(required=True)
    main_id_category_id = fields.Many2one(
        'res.partner.id_category', string="Main Identification Category")
    main_id_number = fields.Char('Main Identification Number')
    license_number = fields.Char('Driver License Number')
    partner_id = fields.Many2one(
        'res.partner', string='Customer', domain="[('customer', '=', True)]",
        help="For those cases where driver works in customer's company.")
    afip_responsability_type_id = fields.Many2one(
        'afip.responsability.type', string='AFIP Responsibility Type')
    transport_company_id = fields.Many2one(
        'res.partner', string='Transport Company',
        domain="[('transport', '=', True)]",
        help="If driver does not directly work for the customer, it is advisable to identify the Transport Company he/she belongs to.")


class CSWTruck(models.Model):
    _name = 'csw.truck'
    _inherit = ['mail.thread']
    _description = 'Truck'

    name = fields.Char(string="Vehicle name", required=True, default='/')
    license_number = fields.Char('License Number')
    partner_id = fields.Many2one(
        'res.partner', string='Customer', domain="[('customer', '=', True)]",
        help="For those cases where truck belongs to customer's company")
    transport_company_id = fields.Many2one(
        'res.partner', string='Transport Company',
        domain="[('transport', '=', True)]",
        help="If truck does not belong to the customer, it is advisable to identify the Transport Company it belongs to.")
    weight_tare = fields.Float(string='Truck Tare Weight (Kg)', digits=(16, 2))
    trailer_number = fields.Char('Trailer Number')
    weight_trailer = fields.Float(
        string='Trailer Tare Weight (Kg)', digits=(16, 2))
    insurance_company_id = fields.Many2one(
        'res.partner', string='Insurance Company',
        domain="[('supplier', '=', True), ('insurance', '=', True)]")
    insurance_type = fields.Char('Insurance type')
    date_valid_until = fields.Date(
        string='Insurance Valid Until', help="Expiration date of insurance")
    state = fields.Selection([
        ('street', 'On Street'),
        ('dock', 'On Dock'),
        ('exit', 'Exit Control')],
        string='Status', default='street', readonly=True, required=True,
        copy=False,
        help="When the Way Bill is validated, the status is 'On Street'. When the Way Bill is Confirmed, it has a Truck Operation of type Entry Weight and the field Dock has been filled, the status is set to 'On Dock'. If a truck operation of type Exit Weight is recorded the status is set to 'Exit Control'.")
    notes = fields.Text()
    truck_operation_ids = fields.One2many(
        'csw.truck.operation', 'truck_id', string='Truck Operations')
    operations_editable = fields.Boolean(
        compute='_compute_operations_editable')

    _sql_constraints = [
        ('license_number_uniq', 'unique(license_number)',
         'License Number must be unique!'),
    ]

    def _compute_operations_editable(self):
        self.operations_editable = self.user_has_groups(
            'stock.group_stock_manager')

    @api.multi
    def action_on_street(self):
        self.write({'state': 'street'})

    @api.multi
    def action_on_dock(self):
        self.write({'state': 'dock'})

    @api.multi
    def action_exit_control(self):
        self.write({'state': 'exit'})

    @api.model
    def create(self, vals):
        truck = super(CSWTruck, self).create(vals)
        if 'name' not in vals or vals['name'] == '/':
            truck.write({'name': '%s - %s' % (
                truck.license_number, truck.partner_id.name)})
        return truck


class CSWTruckOperation(models.Model):
    _name = 'csw.truck.operation'
    _description = 'Truck Operation'

    truck_id = fields.Many2one('csw.truck', string='Truck', required=True)
    date_start = fields.Datetime('Start Date & Time')
    date_end = fields.Datetime('End Date & Time')
    way_bill_id = fields.Many2one('csw.way.bill', string='Way Bill')
    action = fields.Selection([
        ('entry', 'Entry Weight'),
        ('exit', 'Exit Weight'),
        ('cancel', 'Cancelled')], string='Action')
    weight_total = fields.Float(
        string='Total Weight (Kg)', digits=(16, 2))
    user_id = fields.Many2one(
        'res.users', string='User', default=lambda self: self.env.user)


class CSWWayBill(models.Model):
    _name = 'csw.way.bill'
    _inherit = ['mail.thread']
    _description = 'Way Bill'

    READONLY_STATES = {
        'finish': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    name = fields.Char(
        string="Way Bill No.", default='/', copy=False, index=True,
        readonly=True)
    partner_id = fields.Many2one(
        'res.partner', string='Customer', domain="[('customer', '=', True)]")
    transport_type = fields.Selection([
        ('own', 'Own'),
        ('other', 'Others')],
        string='Transport Type')
    truck_id = fields.Many2one(
        'csw.truck', string='Truck', readonly=True,
        domain="[('partner_id', '=', partner_id)]",
        states={'draft': [('readonly', False)]})
    license_number = fields.Char(
        'Truck License Number', related='truck_id.license_number',
        readonly=True)
    trailer_number = fields.Char('Trailer Number')
    driver_id = fields.Many2one(
        'csw.driver', string='Driver', readonly=True,
        states={'draft': [('readonly', False)]})
    weight_entry = fields.Float(
        string='Entry Weight (Kg)', digits=(16, 2))
    weight_exit = fields.Float(
        string='Exit Weight (Kg)', digits=(16, 2))
    type = fields.Selection([
        ('entry', 'Entry of Products'),
        ('exit', 'Exit of Products')],
        string='Way Bill Type', required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    date = fields.Datetime(
        string='Date', default=fields.Datetime.now, required=True,
        readonly=True, states={'draft': [('readonly', False)]})
    storage_type_id = fields.Many2one(
        'csw.storage.type', string='Cold Storage Type', readonly=True,
        states={'draft': [('readonly', False)]})
    delivery_number = fields.Char('Customer Delivery Number')
    inspection_number = fields.Char('Health Inspection No.')
    seals_number = fields.Char('Seals No.')
    senasa_number = fields.Char('SENASA Auth. Number')
    dock_id = fields.Many2one(
        'csw.dock', string='Dock Number', readonly=False,
        states=READONLY_STATES)
    storage_service_id = fields.Many2one(
        'csw.storage.service', string='Could Storage Service')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('product_move', 'Warehouse Product Movement'),
        ('finish', 'Finished'),
        ('cancel', 'Cancelled')],
        string='Status', default='draft', readonly=True, required=True,
        copy=False)
    kanban_state = fields.Selection([
        ('1draft', 'Draft'),
        ('2confirm', 'Confirmed'),
        ('3dock', 'At the Dock'),
        ('4exit', 'Exit Controls'),
        ('5finish', 'Finished'),
        ('6cancel', 'Cancelled')],
        string='Kanban Status', default='1draft', readonly=True, required=True,
        copy=False)
    line_ids = fields.One2many(
        'csw.way.bill.line', 'way_bill_id', string='Way Bill Lines')
    total_pallet_qty = fields.Integer(
        string="Total Pallets Qty", compute='_compute_total_pallet_qty')
    total_product_qty = fields.Float(
        string="Total Products Qty", compute='_compute_total_product_qty')
    user_id = fields.Many2one(
        'res.users', 'Responsible', default=lambda self: self._uid,
        readonly=False, states=READONLY_STATES)
    service_type_id = fields.Many2one(
        'csw.service.type', string='Service Type')
    product_reception_id = fields.Many2one(
        'csw.product.reception', string='WH Product Reception',
        compute='_compute_product_reception')
    product_delivery_id = fields.Many2one(
        'csw.product.delivery', string='WH Product Delivery',
        compute='_compute_product_delivery')
    start_time = fields.Float(compute='_compute_start_time')
    end_time = fields.Float(compute='_compute_end_time')
    cancellation_reason = fields.Char(
        readonly=True, states={'cancel': [('readonly', False)]})
    notes = fields.Text(string="Comment")
    shift_requested = fields.Boolean(
        readonly=False, states=READONLY_STATES)
    company_id = fields.Many2one(
        'res.company', 'Company', required=True, index=True,
        states=READONLY_STATES,
        default=lambda self: self.env.user.company_id.id)

    # auxiliary fields
    shift_requested_string = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string='Shift', compute='_compute_shift_requested')
    truck_operation_ids = fields.One2many(
        'csw.truck.operation', 'way_bill_id', string='Truck Operations')
    entry_weight_exists = fields.Boolean(
        compute='_compute_entry_weight_exists')
    exit_weight_exists = fields.Boolean(
        compute='_compute_exit_weight_exists')
    product_reception_ids = fields.One2many(
        'csw.product.reception', 'way_bill_id', string='WH Product Receptions')
    product_delivery_ids = fields.One2many(
        'csw.product.delivery', 'way_bill_id', string='WH Product Deliveries')
    transport_type_string = fields.Char(
        string='Transport Type', compute='_compute_transport_type_string')
    storage_service_ids = fields.One2many(
        'csw.storage.service', 'way_bill_id', string='CS Services')
    storage_service_count = fields.Integer(
        compute='_compute_service_count', string="Number of CS Services")
    product_reception_count = fields.Integer(
        compute='_compute_product_reception_count',
        string="Number of CS WH Product Receptions")
    product_delivery_count = fields.Integer(
        compute='_compute_product_delivery_count',
        string="Number of CS WH Product Deliveries")

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Way Bill No. must be unique!'),
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
    def _compute_shift_requested(self):
        for way_bill in self:
            way_bill.shift_requested_string = 'yes' \
                if way_bill.shift_requested else 'no'

    @api.multi
    @api.depends('truck_operation_ids')
    def _compute_entry_weight_exists(self):
        operation_obj = self.env['csw.truck.operation']
        for way_bill in self:
            way_bill.entry_weight_exists = operation_obj.search_count(
                [('way_bill_id', '=', way_bill.id),
                 ('truck_id', '=', way_bill.truck_id.id),
                 ('action', '=', 'entry')]) > 0

    @api.multi
    @api.depends('truck_operation_ids')
    def _compute_exit_weight_exists(self):
        operation_obj = self.env['csw.truck.operation']
        for way_bill in self:
            way_bill.exit_weight_exists = operation_obj.search_count(
                [('way_bill_id', '=', way_bill.id),
                 ('truck_id', '=', way_bill.truck_id.id),
                 ('action', '=', 'exit')]) > 0

    @api.multi
    @api.depends('product_reception_ids', 'type')
    def _compute_product_reception(self):
        for way_bill in self:
            res = False
            if way_bill.type == 'entry' and len(
                    self.product_reception_ids) == 1:
                res = self.product_reception_ids[0]
            way_bill.product_reception_id = res

    @api.multi
    @api.depends('product_delivery_ids', 'type')
    def _compute_product_delivery(self):
        for way_bill in self:
            res = False
            if way_bill.type == 'exit' and len(self.product_delivery_ids) == 1:
                res = self.product_delivery_ids[0]
            way_bill.product_delivery_id = res

    @api.multi
    @api.depends('product_reception_id')
    def _compute_start_time(self):
        for way_bill in self:
            way_bill.start_time = way_bill.product_reception_id.start_time \
                if way_bill.type == 'entry' \
                else way_bill.product_delivery_id.start_time

    @api.multi
    @api.depends('product_delivery_id')
    def _compute_end_time(self):
        for way_bill in self:
            way_bill.end_time = way_bill.product_reception_id.end_time \
                if way_bill.type == 'exit' \
                else way_bill.product_delivery_id.end_time

    @api.multi
    @api.depends('storage_service_ids')
    def _compute_service_count(self):
        for way_bill in self:
            way_bill.storage_service_count = len(way_bill.storage_service_ids)

    @api.multi
    @api.depends('product_reception_ids')
    def _compute_product_reception_count(self):
        for way_bill in self:
            way_bill.product_reception_count = len(
                way_bill.product_reception_ids)

    @api.multi
    @api.depends('product_delivery_ids')
    def _compute_product_delivery_count(self):
        for way_bill in self:
            way_bill.product_delivery_count = len(
                way_bill.product_delivery_ids)

    @api.multi
    def _compute_transport_type_string(self):
        for way_bill in self:
            res = False
            if way_bill.type == 'entry':
                res = _('Entry of Products')
            elif way_bill.type == 'exit':
                res = _('Exit of Products')
            way_bill.transport_type_string = res

    @api.multi
    def action_confirm(self):
        for way_bill in self:
            if way_bill.state != 'draft':
                raise UserError(_('The way bill is not in draft state'))
            if not way_bill.line_ids:
                raise UserError(_('Please create some Operations'))
            way_bill.line_ids.action_confirm()
        self.write({'state': 'confirm', 'kanban_state': '2confirm'})
        return True

    # @api.multi
    # def action_confirm(self):
    #     self.filtered(lambda way_bill: way_bill.state == 'draft').write(
    #         {'state': 'confirm', 'kanban_state': '2confirm'})
    #     return True

    @api.multi
    def action_entry_weight(self):
        self.ensure_one()
        view = self.env.ref('csw.view_csw_bill_weight')
        wiz = self.env['csw.bill.weight'].create({
            'way_bill_id': self.id,
            'action': 'entry'
        })
        return {
            'name': _('Entry Weight'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'csw.bill.weight',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    @api.multi
    def action_assign_dock(self):
        if any(self.filtered(lambda way_bill: way_bill.state != 'confirm' or
                not way_bill.entry_weight_exists)):
            raise UserError(
                _('Please check if the Way Bill is set to Confirmed state and'
                  ' if exists an Entry Weight operation for the truck.'))
        if any(self.filtered(lambda way_bill: not way_bill.dock_id)):
            raise UserError(_('Please enter assigned Dock No.'))

        reception_obj = self.env['csw.product.reception']
        delivery_obj = self.env['csw.product.delivery']
        for way_bill in self:
            way_bill.truck_id.action_on_dock()

            values = way_bill._prepare_wh_product_movement()
            if way_bill.type == 'entry':
                reception_obj.create(values)
            elif way_bill.type == 'exit':
                delivery_obj.create(values)
        self.write({'state': 'product_move', 'kanban_state': '3dock'})

    @api.multi
    def action_exit_control(self):
        self.write({'kanban_state': '4exit'})

    @api.multi
    def action_exit_weight(self):
        self.ensure_one()
        view = self.env.ref('csw.view_csw_bill_weight')
        wiz = self.env['csw.bill.weight'].create({
            'way_bill_id': self.id,
            'action': 'exit'
        })
        return {
            'name': _('Exit Weight'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'csw.bill.weight',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    @api.multi
    def action_cancel(self):
        self.ensure_one()
        if self.env['csw.truck.operation'].search_count(
                [('way_bill_id', '=', self.id),
                 ('truck_id', '=', self.truck_id.id),
                 ('action', '=', 'entry')]) > 0:
            raise UserError(_(
                'You cannot cancel a way bill having already an Entry Weight'
                ' operation'))
        view = self.env.ref('csw.view_csw_bill_cancellation')
        wiz = self.env['csw.bill.cancellation'].create(
            {'way_bill_id': self.id})
        return {
            'name': _('Way Bill Cancellation'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'csw.bill.cancellation',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    @api.multi
    def action_finish(self):
        for way_bill in self:
            if not way_bill.exit_weight_exists:
                raise UserError(
                    _('Please check if exists an Exit Weight operation for the'
                      ' truck.'))
            if way_bill.type == 'entry' and \
                    way_bill.product_reception_ids.filtered(
                    lambda x: x.state != 'confirm') or way_bill.type == 'exit'\
                    and way_bill.product_delivery_ids.filtered(
                    lambda x: x.state != 'confirm'):
                raise UserError(
                    _('Please check if generated Product Movement from this'
                      ' Way Bill is set to Confirmed state'))
            way_bill.truck_id.action_on_street()
        self.write({'state': 'finish', 'kanban_state': '5finish'})

    @api.multi
    def open_storage_service(self):
        self.ensure_one()
        action = {
            'name': _('CS Service'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'csw.storage.service',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.storage_service_ids.ids)],
        }
        if len(self.storage_service_ids) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = self.storage_service_ids[0].id
        return action

    @api.multi
    def open_product_reception(self):
        self.ensure_one()
        action = {
            'name': _('WH Product Reception'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'csw.product.reception',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.product_reception_ids.ids)],
        }
        if len(self.product_reception_ids) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = self.product_reception_ids[0].id
        return action

    @api.multi
    def open_product_delivery(self):
        self.ensure_one()
        action = {
            'name': _('WH Product Delivery'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'csw.product.delivery',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.product_delivery_ids.ids)],
        }
        if len(self.product_delivery_ids) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = self.product_delivery_ids[0].id
        return action

    def _prepare_wh_product_movement(self):
        return {
            'way_bill_id': self.id,
            'partner_id': self.partner_id.id,
            'transport_type': self.transport_type,
            'truck_id': self.truck_id.id,
            'driver_id': self.driver_id.id,
            'trailer_number': self.trailer_number,
            'date': self.date,
            'storage_type_id': self.storage_type_id.id,
            'delivery_number': self.delivery_number,
            'inspection_number': self.inspection_number,
            'seals_number': self.seals_number,
            'senasa_number': self.senasa_number,
            'dock_id': self.dock_id.id,
        }

    def _prepare_cold_storage_service(self):
        return {
            'way_bill_id': self.id,
            'partner_id': self.partner_id.id,
            'transport_type': self.transport_type,
            'truck_id': self.truck_id.id,
            'origin_document': 'waybill',
            'date': self.date,
            'storage_type_id': self.storage_type_id.id,
        }

    @api.multi
    def action_add_service(self):
        self.env['csw.storage.service'].create(
            self._prepare_cold_storage_service()
        )

    def get_product_qty_per_product(self, product_id):
        return sum([line.product_qty for line in self.line_ids.filtered(
            lambda x: x.product_id.id == product_id)])

    @api.onchange('truck_id')
    def onchange_truck_id(self):
        self.trailer_number = self.truck_id.trailer_number

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        return self._apply_truck_complex_domain()

    @api.onchange('transport_type')
    def onchange_transport_type(self):
        return self._apply_truck_complex_domain()

    def _apply_truck_complex_domain(self):
        self.truck_id = False
        if self.transport_type:
            vals = [('partner_id', '=', self.partner_id.id)]
            if self.transport_type == 'other':
                vals = [('transport_company_id', '!=', False)]
            trucks = self.env['csw.truck'].search(vals)
            domain = [('id', 'in', trucks.ids)]
            return {'domain': {'truck_id': domain}}

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'csw.way.bill') or '/'
        return super(CSWWayBill, self).create(vals)


class CSWWayBillLine(models.Model):
    _name = 'csw.way.bill.line'
    _description = 'Way Bill Line'

    way_bill_id = fields.Many2one(
        'csw.way.bill', string='Way Bill', required=True, ondelete='cascade')
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain="[('store_ok', '=', True), ('owner_id', '=', way_bill_id.partner_id)]",
        required=True)
    customer_pallet_no = fields.Char('Customer Pallet No.')
    package_id = fields.Many2one(
        'stock.quant.package', string='Our Pallet No.')
    pallet_type_id = fields.Many2one(
        'csw.pallet.type', string='Pallet Type',
        related='product_id.pallet_type_id', readonly=True)
    lot_number = fields.Char(
        string='Lot No.')  # TODO definir si es de tipo char o un m2o a lot
    product_qty = fields.Float('Product Qty p/Pallet', required=True)
    use_date = fields.Date('Best Before Date', required=True)
    # auxiliary fields
    type = fields.Selection(
        related='way_bill_id.type', readonly=True)

    @api.onchange('package_id')
    def _onchange_partner_id(self):
        self.lot_number = self.package_id.lot_id.name
        self.use_date = self.package_id.use_date

    @api.onchange('pallet_type_id')
    def _onchange_pallet_type_id(self):
        self.product_qty = self.pallet_type_id.product_qty

    @api.multi
    def action_confirm(self):
        package_obj = self.env['stock.quant.package']
        for line in self:
            package = package_obj.create({})
            line.write({
                'package_id': package.id
            })
        return True

    # @api.model
    # def create(self, vals):
    #     package = self.env['stock.quant.package'].create({})
    #     vals.update({
    #         'package_id': package.id
    #     })
    #     return super(CSWWayBillLine, self).create(vals)
