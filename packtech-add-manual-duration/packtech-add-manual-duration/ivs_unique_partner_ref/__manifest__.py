# -*- coding: utf-8 -*-
{
    'name': """Unique Partner Reference""",
    'summary': """Set the Reference (Code) on Partners to be Unique per partner""",
    'description': """
        Installing this module will make the field (Reference) on the Partner form unique, so you can add the partners code without duplication
    """,
    'author': 'I Value Solutions',
    'website': 'www.ivalue-s.com',
    'email': 'info@ivalue-s.com',
    'license': 'OPL-1',
    'category': 'Accounting',
    'version': '0.1',
    'images': [],
    'depends': ['base', 'web', 'contacts'],
    'data': [
        'views/res_partner.xml',
    ],
}
