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
    'depends': ['crm','sale','stock', 'delivery', 'website','website_sale', 'payment'],
    'data': [
        'account/menus.xml',
        'auto_ship/menus.xml', 
        
        'account/views.xml',
        'auto_ship/auto_ship_views.xml',
        'auto_ship/sale_order_views.xml',

        'auto_ship/sequence.xml',
        'data/cron.xml',
    ],
    'installable': True,
}
