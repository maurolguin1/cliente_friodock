# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CswFiscalApproval(models.TransientModel):
    _name = "csw.fiscal.approval"
    _description = "Fiscal Storage Approval"

    date_approval = fields.Date(
        string='Fiscal Approval Date', default=fields.Date.context_today,
        required=True)

    @api.multi
    def set_approval_date(self):
        self.ensure_one()
        packages = self.env['stock.quant.package'].browse(
            self._context.get('active_id', False))
        packages.write({
            'date_fiscal_approval': self.date_approval,
            'fiscal_approval': True,
            'fiscal_approval_user_id': self.env.uid
        })
