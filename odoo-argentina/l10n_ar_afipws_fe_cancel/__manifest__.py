# -*- coding: utf-8 -*-
##############################################################################
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Integration between electronic invoice and account cancel",
    'version': '10.0.1.0.0',
    'category': 'Localization/Argentina',
    'sequence': 14,
    'author': 'Moogah,ADHOC SA',
    'website': 'www.moogah.com',
    'license': 'AGPL-3',
    'summary': '',
    'description': """
Integration between electronic invoice and account cancel
=========================================================
""",
    'depends': [
        'l10n_ar_afipws_fe',
        'account_cancel',
    ],
    'external_dependencies': {
    },
    'data': [
        'views/invoice_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
