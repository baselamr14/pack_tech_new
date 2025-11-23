# -*- coding: utf-8 -*-
{
    'name': "IVS Sales Plan",
    'summary': """IVS Sales Plan""",
    'description': """IVS Sales Plan""",
    'author': 'I VALUE Solutions',
    'website': 'info@yossefelsherif.com',
    'email': 'info@yossefelsherif.com',
    'license': 'OPL-1',
    'category': 'MRP',
    'depends': ['base', 'mrp', 'purchase', 'sale', 'stock'],
    'data': [
        'security/security.xml',
        'data/email.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/sales_plan.xml',
    ],
    "images": [
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
