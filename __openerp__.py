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
        'models/auto_ship/data/cron.xml',
        'web/account/data/menus.xml',
        'web/account/data/users.xml',
        
        'models/auto_ship/data/menus.xml', 
        'models/auto_ship/data/sequence.xml',
        
        'web/account/views/account.xml',
        'web/account/views/account_address.xml',
        
        'models/auto_ship/views/auto_ship.xml',
        'models/auto_ship/views/sale_order.xml',
        'models/auto_ship/views/partner.xml',
        'models/diseases/views/partner.xml',
        'models/auto_ship/views/product.xml',
    ],
    'installable': True,
}
