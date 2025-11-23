{
    'name': """Unique Product Internal Reference""",
    'summary': """Set the Internal Reference on the Products to be Unique per product """,
    'description': """
    Installing this module will make the field (Internal Reference) on the Product form unique, so you can add the Product code without duplication""",
    'author': 'I Value Solutions',
    'website': 'https://www.ivalue-s.com',
    'email': 'info@ivalue-s.com',
    'version': '16.0.0.1',
    'category': 'Productivity',
    'license':'OPL-1',
    'images': ['static/description/banner.png'],
    'price': 4.99,
    'currency': 'USD',
    'depends': ['base', 'product'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/product.xml',
    ],
    'installable': True,
    'auto_install': False,
}
