# -*- coding: utf-8 -*-
{
    'name': 'Could Storage Warehouse',
    'version': '1.0',
    'description': """
    This module adds some extensions in order to fulfill customer requirements.
    """,
    'author': "Moogah",
    'website': "www.moogah.com",
    'category': 'Warehouse',
    'summary': '',
    'depends': [
        'stock',
        'l10n_ar_partner',
        'l10n_ar_account',
        'product_expiry',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'data/csw_data.xml',
        'views/csw_menu_views.xml',
        'views/csw_config_settings_views.xml',
        'views/csw_configuration_views.xml',
        'views/res_partner_views.xml',
        'views/product_template_views.xml',
        'views/stock_quant_package_views.xml',
        'views/csw_way_bill_views.xml',
        'views/csw_product_reception_views.xml',
        'views/csw_product_delivery_views.xml',
        'views/csw_storage_service_views.xml',
        'wizard/csw_bill_weight_view.xml',
        'wizard/csw_bill_cancellation_view.xml',
        'wizard/csw_fiscal_approval_view.xml',
        'wizard/csw_pallet_consolidation_view.xml',
    ],
    'installable': True,
    'application': True,
}
