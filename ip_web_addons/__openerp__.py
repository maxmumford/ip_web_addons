{
    'name': 'IP Web Addons',
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
    'depends': ['crm','sale','stock', 'delivery', 'website','website_sale', 'payment'],
    'data': [
        'auto_ship/data/cron.xml',
        'account/data/menus.xml',
        
        'auto_ship/data/menus.xml', 
        'auto_ship/data/sequence.xml',
        
        'account/views/account.xml',
        'account/views/account_address.xml',
        
        'auto_ship/views/auto_ship.xml',
        'auto_ship/views/sale_order.xml',
        'auto_ship/views/product.xml',
    ],
    'installable': True,
}
