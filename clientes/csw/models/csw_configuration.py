# -*- coding: utf-8 -*-

from odoo import fields, models


class CSWStorageType(models.Model):
    _name = 'csw.storage.type'
    _description = 'Cold Storage Type'
    _rec_name = 'description'

    description = fields.Char(string='Description', required=True)
    code = fields.Char()
    active = fields.Boolean(
        default=True,
        help="Set active to false to hide the cold storage type without removing it.")


class CSWServiceType(models.Model):
    _name = 'csw.service.type'
    _description = 'Service Type'
    _rec_name = 'code'

    code = fields.Char(required=True)
    service_task = fields.Selection([
        ('move_in', 'Movement In'),
        ('move_out', 'Movement Out'),
        ('storage', 'Stay in Storage'),
        ('tunnel', 'Tunnel Service'),
        ('pallet', 'Pallet Service'),
        ('bulk', 'Bulk Service'),
        ('film', 'Film Service'),
        ('entry_weight', 'Entry Weight'),
        ('exit_weight', 'Exit Weight'),
        ('plug_in', 'Plug-In Truck'),
        ('de_consolidate', 'De-Consolidate'),
        ('consolidate', 'Consolidate'),
        ('temp', 'Temperature Control'),
        ('other', 'Others')], string='Service Task')
    invoicing_policy = fields.Selection([
        ('invoiceable', 'Invoiceable Service'),
        ('free', 'Free Service')], string='Invoicing policy')
    invoice_product_id = fields.Many2one(
        'product.product', string='Product for Invoices')
    active = fields.Boolean(
        default=True,
        help="Set active to false to hide the service type without removing it.")


class CSWDock(models.Model):
    _name = 'csw.dock'
    _description = 'Dock'
    _rec_name = 'description'

    description = fields.Char(required=True)
    code = fields.Char()


class CSWPalletType(models.Model):
    _name = 'csw.pallet.type'
    _description = 'Pallet Type'
    _rec_name = 'code'

    code = fields.Char(required=True)
    service_type_id = fields.Many2one(
        'csw.service.type', string='Service Type for Storage',
        domain="[('service_task', '=', 'storage'),('invoicing_policy', '=', 'invoiceable')]")
    move_in_service_type_id = fields.Many2one(
        'csw.service.type', string='Service Type for Movement In',
        domain="[('service_task', '=', 'move_in'),('invoicing_policy', '=', 'invoiceable')]")
    move_out_service_type_id = fields.Many2one(
        'csw.service.type', string='Service Type for Movement Out',
        domain="[('service_task', '=', 'move_out'),('invoicing_policy', '=', 'invoiceable')]")
    senasa_control = fields.Selection([
        ('not_certificate', 'Does not require a certificate'),
        ('domestic_product', 'Domestic Products Certification'),
        ('imported_product', 'Imported Products Certification')],
        string='Senasa Control')
    fiscal_storage_type = fields.Selection([
        ('not_approval', 'Does not need approval'),
        ('need_approval', 'Needs approval for des-consolidation ')],
        string='Fiscal Storage Type')
    product_qty = fields.Float(string='Default Product Qty. p/Pallet')
    active = fields.Boolean(
        default=True,
        help="Set active to false to hide the pallet type without removing it.")
