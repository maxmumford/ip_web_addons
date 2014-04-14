{
    'name': 'Website Customer Account',
    'category': 'Website',
    'summary': 'More user friendly account for customers. Display things like orders, invoices & tracking codes.',
    'version': '1.0',
    'description': """
Website Customer Account
========================
More user friendly account view for customers. Display things like orders, invoices & tracking codes.
        """,
    'author': 'Max Mumford (OpenERP)',
    'depends': ['crm','sale','stock','website','website_sale'],
    'data': [
        'data/website_account_data.xml', 
        'views/website_account_account.xml',
    ],
    'installable': True,
}
