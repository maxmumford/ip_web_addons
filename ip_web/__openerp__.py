{
    'name': 'IP Web',
    'category': 'Website',
    'summary': 'Customer portal, auto shipments and product ordering changes',
    'version': '1.0',
    'description': """
Website Customer Account
========================
More user friendly account portal for customers. Display things like orders, invoices & tracking codes.

Add auto shipment functionality to sales order.

Also show quantity widget when adding products to basket
        """,
    'author': 'Max Mumford (OpenERP)',
    'depends': ['crm','sale','stock','website','website_sale', 'payment'],
    'data': [
        'data/menus.xml', 
        'views/account.xml',
    ],
    'installable': True,
}
