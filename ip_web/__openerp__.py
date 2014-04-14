{
    'name': 'IP Web',
    'category': 'Website',
    'summary': 'Customer portal and product quantity changes.',
    'version': '1.0',
    'description': """
Website Customer Account
========================
More user friendly account view for customers. Display things like orders, invoices & tracking codes.

Also show quantity widget when adding products to basket
        """,
    'author': 'Max Mumford (OpenERP)',
    'depends': ['crm','sale','stock','website','website_sale', 'alpha_direct_services'],
    'data': [
        'data/website_account_data.xml', 
        'views/website_account_account.xml',
    ],
    'installable': True,
}
