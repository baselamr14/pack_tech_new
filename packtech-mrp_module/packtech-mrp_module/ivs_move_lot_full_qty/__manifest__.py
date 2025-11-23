# -*- coding: utf-8 -*-
{
    'name': "IVS Move Lot Full Qty",
    'summary': """Force Product transfer Full Qty""",
    'description': """Force Product transfer Full Qty""",
    'author': 'I Value Solutions',
    'website': 'https://www.ivalue-s.com',
    'email': 'info@ivalue-s.com',
    'license': 'OPL-1',
    'category': 'Inventory',
    'version': '16.0.0.0',
    'depends': ['stock'],

    'data': [
        "security/ir.model.access.csv",
        "wizard/sh_message_wizard.xml",
        'views/product.xml',
        'views/location.xml',
    ],


}
