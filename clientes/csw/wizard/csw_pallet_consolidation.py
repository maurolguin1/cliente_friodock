# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class CswPalletConsolidation(models.TransientModel):
    _name = "csw.pallet.consolidation"
    _description = "Pallet Consolidation"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(CswPalletConsolidation, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type == 'form':
            active_ids = self._context.get('active_ids')
            if len(active_ids) == 1:
                raise UserError(
                    _('Please select at least two pallets registers before'
                      ' trying to Consolidate'))
            packages = self.env['stock.quant.package'].browse(active_ids)
            if any(packages.filtered(lambda x: not x.quant_ids)):
                raise UserError(
                    _('There should be at least one stock quant (Bulk Content)'
                      ' in each one of selected pallets to be consolidated'))
            res['fields']['package_id']['domain'] = [('id', 'in', active_ids)]
            res['fields']['consolidate_package_id']['domain'] = [
                ('id', 'in', active_ids)]
        return res

    package_id = fields.Many2one(
        'stock.quant.package', string='Pallet to De-consolidate',
        required=True)
    consolidate_package_id = fields.Many2one(
        'stock.quant.package', string='Pallet to Consolidate', required=True)

    @api.multi
    def apply_consolidation(self):
        self.ensure_one()
        if self.package_id.id == self.consolidate_package_id.id:
            raise UserError(
                _('Please select two different Pallets!'))
        self._check_conditions()
        self.package_id.quant_ids.write({
            'package_id': self.consolidate_package_id.id})
        self.package_id.write({
            'date_de_consolidation': fields.Date.today(),
        })
        self.consolidate_package_id.write({
            'date_consolidation': fields.Date.today(),
        })
        # self._create_cs_service()
        return True

    def _check_conditions(self):
        if self.package_id.current_location_id.id != \
                self.consolidate_package_id.current_location_id.id or \
                        self.package_id.pallet_type_id.id != \
                        self.consolidate_package_id.pallet_type_id.id or \
                        self.package_id.senasa_control != \
                        self.consolidate_package_id.senasa_control:
            raise ValidationError(
                _('Selected pallets must have the same Current location,'
                  ' Pallet type, SENASA control and Fiscal Storage Status.'))
