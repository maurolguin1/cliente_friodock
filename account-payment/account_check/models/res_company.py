# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models, api, _
from openerp.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Own
    own_check_rejected_account_id = fields.Many2one(
        'account.account',
        'Own Checks Rejected Account', translate=True,
        help='Own Checks Rejected Account, for eg. "Own Rejected Checks"',
    )
    own_check_cancelled_account_id = fields.Many2one(
        'account.account',
        'Own Check Cancelled Account', translate=True,
        help='Own Check Cancelled Account, for eg. "Own Cancelled Checks"',
    )
    deferred_check_account_id = fields.Many2one(
        'account.account',
        'Deferred Check Account', translate=True,
        help='Deferred Checks account, for eg. "Deferred Checks"',
    )

    payment_method_validate_jr = fields.Boolean(
        string='Validate Payment Method in Journals', translate=True,
    )

    # Third Party
    third_party_checks_cancelled_account_id = fields.Many2one(
        'account.account',
        'Third Party Cancelled Check Account', translate=True,
        help='Third Party Cancelled Account, for eg. "Third Party Cancelled Checks"',
    )
    third_party_checks_bounced_endorsed_account_id = fields.Many2one(
        'account.account',
        'Third Party Bounced Check Account', translate=True,
        help='Third Party Bounced Check Account, for eg. "Third Party Bounced Checks"',
    )
    rejected_check_account_id = fields.Many2one(
        'account.account',
        'Third Party Rejected Check Account', translate=True,
        help='Third Party Rejected Check Account, for eg. "Third Party Rejected Checks"',
    )
    holding_check_account_id = fields.Many2one(
        'account.account',
        'Third Party Holding Check Account', translate=True,
        help='Third Party Holding Checks account for third checks, for eg. "Third Party Holding Checks"',
    )

    @api.multi
    def _get_check_account(self, type):
        self.ensure_one()
        if type == 'holding':
            account = self.holding_check_account_id
        elif type == 'rejected':
            account = self.rejected_check_account_id
        elif type == 'deferred':
            account = self.deferred_check_account_id
        elif type == 'returned':
            account = self.own_check_cancelled_account_id
        elif type == 'own_check_rejected':
            account = self.own_check_rejected_account_id
        elif type == 'own_check_cancelled':
            account = self.own_check_cancelled_account_id
        elif type == 'third_party_cancelled':
            account = self.third_party_checks_cancelled_account_id
        elif type == 'third_party_bounced_endorsed':
            account = self.third_party_checks_bounced_endorsed_account_id
        else:
            raise UserError(_("Type %s not implemented!") % (type))
        if not account:
            raise UserError(_('No checks %s account defined for company %s') % (type, self.name))
        return account
