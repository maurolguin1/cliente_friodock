# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    transport = fields.Boolean(
        string='Is a Transport Company',
        help="Check this box if this contact is a transport company.")
    insurance = fields.Boolean(
        string='Is an Insurance Company',
        help="Check this box if this contact is an insurance company.")
