# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CswBillCancellation(models.TransientModel):
    _name = "csw.bill.cancellation"
    _description = "Way Bill Cancellation"

    way_bill_id = fields.Many2one(
        'csw.way.bill', string='Way Bill', required=True)
    date_cancel = fields.Date(
        string='Cancellation Date', default=fields.Date.context_today,
        required=True)
    cancellation_reason = fields.Char(string="Cancellation Reason")

    @api.multi
    def cancel_way_bill(self):
        self.ensure_one()
        self.way_bill_id.write({
            'cancellation_reason': self.cancellation_reason,
            'state': 'cancel',
            'kanban_state': '6cancel'
        })
        if self.way_bill_id.state == 'confirm':
            self.env['csw.truck.operation'].create({
                'way_bill_id': self.way_bill_id.id,
                'truck_id': self.way_bill_id.truck_id.id,
                'action': 'cancel',
                'date_start': fields.Datetime.now(),
                'user_id': self.env.user.id
            })
            self.way_bill_id.truck_id.write({'state': 'street'})
        return True
