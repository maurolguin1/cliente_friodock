# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CswBillWeight(models.TransientModel):
    _name = "csw.bill.weight"
    _description = "Way Bill Register Weight"

    way_bill_id = fields.Many2one(
        'csw.way.bill', string='Way Bill', required=True)
    action = fields.Selection([
        ('entry', 'Entry Weight'),
        ('exit', 'Exit Weight')], string='Action', readonly=True,
        required=True)
    license_number = fields.Char('Truck License No.')
    weight_total = fields.Float(
        string='Truck Total Weight (kg)', digits=(16, 2))

    @api.multi
    def register_weight(self):
        self.ensure_one()
        if self.license_number != self.way_bill_id.license_number:
            raise UserError(
                _('The License No. entered does not match the one from the Way'
                  ' Bill record. Please check your data and try again.'))

        values = {'weight_entry': self.weight_total}
        operation_values = {
            'way_bill_id': self.way_bill_id.id,
            'truck_id': self.way_bill_id.truck_id.id,
            'action': 'entry',
            # TODO faltan campos
            'weight_total': self.weight_total,
            'user_id': self.env.user.id
        }
        if self.action == 'exit':
            values = {
                'weight_exit': self.weight_total,
                'kanban_state': '5finish'
            }
            operation_values.update({'action': 'exit'})
            self.way_bill_id.truck_id.action_exit_control()

        self.way_bill_id.write(values)
        self.env['csw.truck.operation'].create(operation_values)
        return True
