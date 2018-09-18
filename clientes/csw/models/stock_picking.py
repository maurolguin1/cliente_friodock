# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    product_reception_id = fields.Many2one(
        'csw.product.reception', string='Product Reception')

    @api.multi
    def set_quantities_done(self):
        """
        Set quantities done in picking operations. Set values from
        reception_line to packs and put operations in it.
        Operations should be length 1 in all cases in this function, one
        operation per reception_line.
        """
        for pick in self:
            for rl in pick.product_reception_id.line_ids:
                operations = pick.pack_operation_ids.filtered(
                    lambda x: x.qty_done == 0)

                # checking if there is no tracking for reception_line.product_id
                operations.filtered(
                    lambda x: not x.lots_visible and
                              x.product_id.id == rl.product_id.id
                ).write({'qty_done': rl.product_qty})
                # checking if there is tracking for reception_line.product_id
                operations_with_lots = operations.filtered(
                    lambda x: x.lots_visible and
                              x.product_id.id == rl.product_id.id)
                operation_lot_obj = self.env['stock.pack.operation.lot']
                for operation in operations_with_lots:
                    operation_lot_obj.create({
                        'operation_id': operation.id,
                        'qty': rl.product_qty,
                        'lot_name': rl.lot_number,
                    })
                    operation.write({'qty_done': rl.product_qty})

                package = rl.package_id
                # setting values from reception_line to operation's pack
                package.write({
                    'partner_id': rl.product_reception_id.partner_id.id,
                    'storage_service_id':
                        rl.product_reception_id.storage_service_id.id,
                    'product_market':
                        rl.product_reception_id.product_market,
                    'customer_pallet_no': rl.customer_pallet_no,
                    'pallet_type_id': rl.pallet_type_id.id,
                    # 'use_date': rl.use_date,
                    'temp_reception': rl.temperature,
                    'avg_temp_reception': rl.avg_temperature,
                    'senasa_control': rl.pallet_type_id.senasa_control,
                    'senasa_number': rl.product_reception_id.senasa_number,
                    'fiscal_storage_type':
                        rl.pallet_type_id.fiscal_storage_type,
                    'inspection_number':
                        rl.product_reception_id.inspection_number,
                    'seals_number': rl.product_reception_id.seals_number,
                })
                # putting picking operations in Packs
                operations = pick.pack_operation_ids.filtered(
                    lambda x: x.qty_done > 0 and (not x.result_package_id))
                pick._custom_put_in_pack(operations, package.id)

    def _custom_put_in_pack(self, operations, package_id):
        pack_operation_ids = self.env['stock.pack.operation']
        for operation in operations:
            # If we haven't done all qty in operation, we have to split into 2 operation
            op = operation
            if operation.qty_done < operation.product_qty:
                new_operation = operation.copy(
                    {'product_qty': operation.qty_done,
                     'qty_done': operation.qty_done})

                operation.write(
                    {'product_qty': operation.product_qty - operation.qty_done,
                     'qty_done': 0})
                if operation.pack_lot_ids:
                    packlots_transfer = [
                        (4, x.id) for x in operation.pack_lot_ids]
                    new_operation.write({'pack_lot_ids': packlots_transfer})

                    # the stock.pack.operation.lot records now belong to the new, packaged stock.pack.operation
                    # we have to create new ones with new quantities for our original, unfinished stock.pack.operation
                    new_operation._copy_remaining_pack_lot_ids(operation)

                op = new_operation
            pack_operation_ids |= op
        if operations:
            pack_operation_ids.check_tracking()
            pack_operation_ids.write({'result_package_id': package_id})
        else:
            raise UserError(
                _('Please process some quantities to put in the pack first!'))
